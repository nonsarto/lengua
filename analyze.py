"""
analyze.py — the brain. Every capture mode (decode/check/brief/listen) routes through here.

This is the ONE thing that must be validated before anything else gets built. The whole app
is a thin surface over this function's output. If it produces clean, correctly-tagged learning
objects from your real Barcelona snippets, the rest is legwork. If it doesn't, you found out
in an afternoon instead of after three weeks of UI.

Design rules baked in:
- Intelligence happens AFTER capture, not before. The user never picks decode/check/brief;
  this function infers intent from the input.
- The LLM only produces the structured ANALYSIS. Scoring, promotion, state transitions are
  deterministic code elsewhere (see apply_analysis stub at the bottom) — never the LLM.
- Concept slugs must match the existing backbone. analyze() proposes slugs; the caller
  reconciles them against `concepts` (create-if-new with reviewed=false, else reuse).
"""

import json
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Verify against current docs; a Sonnet-class model is the right workhorse for this.
MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """You are the analysis engine of a Spanish-learning tool for a German speaker
living in Barcelona. You receive a snippet the user captured from real life and return a
structured analysis as JSON — nothing else, no prose, no markdown fences.

The user's production target variety is {variety} (default peninsular / Barcelona). But for
COMPREHENSION, treat all varieties as valid — never mark a Latin-American or regional form as
"wrong", only note its region.

First infer the MODE from the input:
- "check"  : the user produced Spanish and implicitly asks if it's right.
- "decode" : the user captured something they don't understand (a sign, overheard speech, text).
- "brief"  : the user asks to be prepared for a situation ("prepárame para...", "mañana tengo...").
- "listen" : a transcript of someone else speaking (fast, colloquial, possibly regional).

Then return this JSON shape:

{
  "mode": "check|decode|brief|listen",
  "gist": "plain German one-liner of what it means (for decode/listen); null otherwise",
  "correction": { "wrong": "...", "correct": "...", "concept_slug": "...", "why": "one short German sentence" } | null,
  "lemmas": [
    { "term": "...", "translation": "...", "register": "formal|neutral|coloquial", "region": "cataluña|latam|asturias|null", "cefr": "A1..C1|null" }
  ],
  "concepts": [
    { "slug": "stable-kebab-case", "label": "...", "cefr": "A1..B2|null", "evidence": "encounter|error|success" }
  ],
  "verbs": [
    { "infinitive": "...", "pattern_tags": ["..."], "note": "..." }
  ],
  "notes": "anything worth flagging, or empty string"
}

Slug rules: kebab-case, stable, conceptual not surface. A tense error goes on the tense concept
AND on the violated pattern-family (e.g. 'no quero' -> concept slug 'stem-change-e-ie',
evidence 'error'), not on the single verb. Prefer reusing obvious canonical slugs
(ser-vs-estar, indefinido-vs-perfecto, subjuntivo-presente, por-vs-para, stem-change-e-ie,
g-verbs, ...). Keep lemmas to genuinely useful items, not every word.
Return ONLY the JSON object."""


def analyze(raw_text: str, variety: str = "peninsular") -> dict:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT.replace("{variety}", variety),
        messages=[{"role": "user", "content": raw_text}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    # Be tolerant of accidental fences even though we asked for none.
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)


# ---------------------------------------------------------------------------
# Everything below is DETERMINISTIC — no LLM. This is where learning state moves.
# Sketch only; flesh out in Slice 4. Shown here so the seam is obvious.
# ---------------------------------------------------------------------------
NEED_THRESHOLD = 4  # tune with real data, later. Maybe ratio-based instead of fixed.

def apply_analysis(db, user_id, capture_id, result: dict) -> None:
    """Write the outcome. Reconcile slugs, bump counters, move states — all in code."""
    for c in result.get("concepts", []):
        concept = db.get_or_create_concept(c["slug"], c.get("label"), c.get("cefr"))
        db.add_evidence(user_id, concept.id, capture_id, c["evidence"])
        state = db.get_or_create_state(user_id, concept.id)
        if c["evidence"] == "error":
            state.need_count += 1
        elif c["evidence"] == "success":
            state.success_count += 1
        _recompute_state(state)          # sin_ver -> visto -> flojo -> aprendiendo -> dominado
        db.save_state(state)

def _recompute_state(state) -> None:
    if state.need_count >= NEED_THRESHOLD and state.success_count < state.need_count:
        state.state = "aprendiendo"      # promote: this is where a lesson materializes in the chapter
    elif state.success_count > state.need_count and state.need_count > 0:
        state.state = "dominado"         # demote back to quiet reference — the down-move matters as much
    # ... visto/flojo transitions, boost handling, etc.
