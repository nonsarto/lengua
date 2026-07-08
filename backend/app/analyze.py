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
  deterministic code below (apply_analysis / _recompute_state) — never the LLM.
- Concept slugs must match the existing backbone. analyze() proposes slugs; the caller
  reconciles them against `concepts` (create-if-new with reviewed=false, else reuse).
- Output shape is enforced via structured outputs (output_config.format) — the API guarantees
  the response validates against ANALYSIS_SCHEMA, so no fence-stripping or parse-hoping.
"""

import json
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Sonnet is the right workhorse for this extraction task: fast, cheap, strong at tagging.
MODEL = "claude-sonnet-5"

# --------------------------------------------------------------------------- schema
_NULLABLE_STR = {"anyOf": [{"type": "string"}, {"type": "null"}]}
_NULLABLE_CEFR = {
    "anyOf": [
        {"type": "string", "enum": ["A1", "A2", "B1", "B2", "C1", "C2"]},
        {"type": "null"},
    ]
}

ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "mode": {"type": "string", "enum": ["check", "decode", "brief", "listen"]},
        "gist": _NULLABLE_STR,
        "correction": {
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "wrong": {"type": "string"},
                        "correct": {"type": "string"},
                        "concept_slug": {"type": "string"},
                        "why": {"type": "string"},
                    },
                    "required": ["wrong", "correct", "concept_slug", "why"],
                    "additionalProperties": False,
                },
                {"type": "null"},
            ]
        },
        "lemmas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "term": {"type": "string"},
                    "translation": {"type": "string"},
                    "register": {"type": "string", "enum": ["formal", "neutral", "coloquial"]},
                    "region": _NULLABLE_STR,  # JSON null when standard/pan-hispanic — never the string "null"
                    "cefr": _NULLABLE_CEFR,
                },
                "required": ["term", "translation", "register", "region", "cefr"],
                "additionalProperties": False,
            },
        },
        "concepts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "slug": {"type": "string"},
                    "label": {"type": "string"},
                    "cefr": _NULLABLE_CEFR,
                    "evidence": {"type": "string", "enum": ["encounter", "error", "success"]},
                },
                "required": ["slug", "label", "cefr", "evidence"],
                "additionalProperties": False,
            },
        },
        "verbs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "infinitive": {"type": "string"},
                    "pattern_tags": {"type": "array", "items": {"type": "string"}},
                    "note": {"type": "string"},
                },
                "required": ["infinitive", "pattern_tags", "note"],
                "additionalProperties": False,
            },
        },
        "notes": {"type": "string"},
    },
    "required": ["mode", "gist", "correction", "lemmas", "concepts", "verbs", "notes"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = """You are the analysis engine of a Spanish-learning tool for a German speaker
living in Barcelona. You receive a snippet the user captured from real life and return a
structured analysis (the response format is enforced — focus on getting the content right).

The user's production target variety is {variety} (default peninsular / Barcelona). But for
COMPREHENSION, treat all varieties as valid — never mark a Latin-American or regional form as
"wrong", only note its region.

First infer the MODE from the input:
- "check"  : the user produced Spanish and implicitly asks if it's right.
- "decode" : the user captured something they don't understand (a sign, overheard speech, text).
- "brief"  : the user asks to be prepared for a situation ("prepárame para...", "mañana tengo...").
- "listen" : a transcript of someone else speaking (fast, colloquial, possibly regional).

If an image is attached, read the Spanish in it (sign, menu, letter, form) and treat that text
as the captured input (usually mode "decode").

Field guidance:
- "gist": plain German one-liner of what it means (for decode/listen); null otherwise.
- "correction": only for check-mode errors; "why" is ONE short German sentence.
- "region": use JSON null (not a string) when the item is standard/pan-hispanic; otherwise a
  lowercase region tag like "cataluña", "latam", "asturias", "andalucía".
- Keep lemmas to genuinely useful items, not every word.

Slug rules: kebab-case, stable, conceptual not surface. A tense error goes on the tense concept
AND on the violated pattern-family (e.g. 'no quero' -> concept slug 'stem-change-e-ie',
evidence 'error'), not on the single verb. Prefer reusing obvious canonical slugs
(ser-vs-estar, indefinido-vs-perfecto, subjuntivo-presente, por-vs-para, stem-change-e-ie,
g-verbs, ...)."""


def _clean_region(value):
    """Belt-and-braces: the schema asks for JSON null, but normalize stray string variants."""
    if value is None:
        return None
    v = value.strip().lower()
    return None if v in ("null", "none", "") else v


def analyze(raw_text: str, variety: str = "peninsular",
            image_b64: str | None = None, image_media_type: str = "image/jpeg") -> dict:
    """One brain for all four capture modes. Optionally takes a photo (base64) — Claude
    reads it directly, no separate OCR step."""
    content: list | str = raw_text
    if image_b64:
        content = [
            {"type": "image",
             "source": {"type": "base64", "media_type": image_media_type, "data": image_b64}},
            {"type": "text", "text": raw_text or "(foto capturada)"},
        ]

    resp = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        thinking={"type": "disabled"},  # pure extraction — no thinking tokens competing with output
        system=SYSTEM_PROMPT.replace("{variety}", variety),
        messages=[{"role": "user", "content": content}],
        output_config={"format": {"type": "json_schema", "schema": ANALYSIS_SCHEMA}},
    )
    if resp.stop_reason == "max_tokens":
        raise RuntimeError("analyze(): output truncated (max_tokens) — raise the limit")

    # Structured outputs guarantee the first text block is valid JSON matching the schema.
    text = next(b.text for b in resp.content if b.type == "text")
    result = json.loads(text)

    for lemma in result.get("lemmas", []):
        lemma["region"] = _clean_region(lemma.get("region"))
    return result


# ---------------------------------------------------------------------------
# Everything below is DETERMINISTIC — no LLM. This is where learning state moves.
# The db object is implemented in db.py; this seam stays here so it's obvious
# that scoring/promotion/state transitions are code, never the model.
# ---------------------------------------------------------------------------
NEED_THRESHOLD = 4  # tune with real data, later. Maybe ratio-based instead of fixed.


def apply_analysis(db, user_id: str, capture_id: str, result: dict) -> dict:
    """Write the outcome. Reconcile slugs, bump counters, move states — all in code.
    Returns a small summary of what was written (for the API response)."""
    written = {"concepts": [], "vocab": [], "correction": None}

    for c in result.get("concepts", []):
        concept = db.get_or_create_concept(c["slug"], c.get("label"), c.get("cefr"))
        db.add_evidence(user_id, concept["id"], capture_id, c["evidence"])
        state = db.get_or_create_state(user_id, concept["id"])
        if c["evidence"] == "error":
            state["need_count"] += 1
        elif c["evidence"] == "success":
            state["success_count"] += 1
        _recompute_state(state, c["evidence"])
        db.save_state(state)
        written["concepts"].append({"slug": c["slug"], "state": state["state"]})

    corr = result.get("correction")
    if corr:
        concept = db.get_or_create_concept(corr["concept_slug"], corr["concept_slug"], None)
        db.add_correction(user_id, capture_id, corr["wrong"], corr["correct"], concept["id"])
        written["correction"] = {"wrong": corr["wrong"], "correct": corr["correct"]}

    for lemma in result.get("lemmas", []):
        item = db.upsert_vocab_item(user_id, lemma, source_capture_id=capture_id)
        if item:
            written["vocab"].append(lemma["term"])

    return written


def _recompute_state(state: dict, evidence: str) -> None:
    """sin_ver -> visto -> flojo -> aprendiendo -> dominado. Up AND down — the demotion
    back to quiet reference matters as much as the promotion."""
    need, success = state["need_count"], state["success_count"]

    if evidence == "encounter":
        if state["state"] == "sin_ver":
            state["state"] = "visto"                  # exposure: decode/listen mark 'seen'
    elif need >= NEED_THRESHOLD and success < need:
        state["state"] = "aprendiendo"                # promote: a lesson materializes in the chapter
    elif need > 0 and success > need:
        state["state"] = "dominado"                   # demote back to quiet reference
    elif evidence == "error":
        state["state"] = "flojo"                      # errors below threshold: shaky but not promoted
