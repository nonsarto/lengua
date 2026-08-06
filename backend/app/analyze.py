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
import logging
import os
from anthropic import Anthropic

from lang import get_lang

PACK = get_lang()
logger = logging.getLogger("lengua")

# Lazy: the deterministic half of this module (apply_analysis, compute_priority, ...)
# must be importable without an API key — only analyze() itself needs the client.
_client: Anthropic | None = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


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
        "mode": {"type": "string", "enum": ["check", "decode", "brief", "listen", "word"]},
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
        "brief": {
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "situation_name": {"type": "string"},
                        "key_vocab": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "term": {"type": "string"},
                                    "translation": {"type": "string"},
                                    "register": {"type": "string",
                                                 "enum": ["formal", "neutral", "coloquial"]},
                                    "region": _NULLABLE_STR,
                                },
                                "required": ["term", "translation", "register", "region"],
                                "additionalProperties": False,
                            },
                        },
                        "phrases": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "intent": {"type": "string"},
                                    "es": {"type": "string"},
                                    "de": {"type": "string"},
                                },
                                "required": ["intent", "es", "de"],
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
                                    "why": {"type": "string"},
                                },
                                "required": ["slug", "label", "why"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["situation_name", "key_vocab", "phrases", "concepts"],
                    "additionalProperties": False,
                },
                {"type": "null"},
            ]
        },
    },
    "required": ["mode", "gist", "correction", "lemmas", "concepts", "verbs", "notes", "brief"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = PACK.SYSTEM_PROMPT


# --------------------------------------------------------------------------- chapter bodies
# On-demand content for LLM-proposed draft concepts (the seed covers the curated backbone;
# concepts born from captures start as slug+label only). Same content rules as
# seed_reference.py, same human gate: the result stays reviewed=false.
CHAPTER_MODEL = "claude-opus-4-8"  # one-time content work — quality over cost, like the seed

CHAPTER_BODY_SCHEMA = {
    "type": "object",
    "properties": {
        "label": {"type": "string"},
        "explanation": {"type": "string"},
        "rule_of_thumb": {"type": "string"},
        "german_pitfall": {"type": "string"},
        "member_verbs": {"type": "array", "items": {"type": "string"}},
        "default_exercises": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"q": {"type": "string"}, "a": {"type": "string"}},
                "required": ["q", "a"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["label", "explanation", "rule_of_thumb", "german_pitfall",
                 "member_verbs", "default_exercises"],
    "additionalProperties": False,
}

CHAPTER_SYSTEM = PACK.CHAPTER_SYSTEM


def generate_chapter_body(slug: str, label: str, cefr: str | None) -> dict:
    """Fill a draft concept with reference content — returns the column dict to persist."""
    resp = _get_client().messages.create(
        model=CHAPTER_MODEL,
        max_tokens=2500,
        system=CHAPTER_SYSTEM,
        messages=[{"role": "user", "content":
                   f"Write the chapter body for: slug '{slug}', current label '{label}',"
                   f" CEFR level {cefr or 'unknown'}."}],
        output_config={"format": {"type": "json_schema", "schema": CHAPTER_BODY_SCHEMA}},
    )
    body = json.loads(next(b.text for b in resp.content if b.type == "text"))
    return {
        "label": body["label"],
        "explanation": body["explanation"],
        "rule_of_thumb": body["rule_of_thumb"],
        "german_pitfall": body["german_pitfall"],
        "member_verbs": body["member_verbs"] or None,
        "default_exercises": body["default_exercises"],
        "reviewed": False,  # the human gate stays — approve is a separate act
    }


EXERCISES_SCHEMA = {
    "type": "object",
    "properties": {
        "exercises": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "etype": {"type": "string", "enum": ["mcq", "cloze"]},
                    "prompt": {"type": "string"},
                    "options": {"type": "array", "items": {"type": "string"}},  # leer bei cloze
                    "answers": {"type": "array", "items": {"type": "string"}},
                    "explanation": {"type": "string"},
                },
                "required": ["etype", "prompt", "options", "answers", "explanation"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["exercises"],
    "additionalProperties": False,
}

EXERCISES_SYSTEM = PACK.EXERCISES_SYSTEM


def generate_exercises(slug: str, label: str, cefr: str | None, chapter: dict,
                       existing_prompts: list[str] | None = None, n: int = 10) -> list[dict]:
    """LLM writes a batch of interactive exercises for one chapter — grounded in its
    reference body. Grading stays deterministic (see grade_exercise); this only CREATES."""
    ground = "\n".join(filter(None, [
        f"Chapter: '{label}' (slug {slug}), CEFR {cefr or 'unknown'}.",
        chapter.get("explanation") and f"Explanation: {chapter['explanation']}",
        chapter.get("rule_of_thumb") and f"Rule of thumb: {chapter['rule_of_thumb']}",
        chapter.get("german_pitfall") and f"German pitfall: {chapter['german_pitfall']}",
        chapter.get("paradigm") and f"Paradigm: {json.dumps(chapter['paradigm'], ensure_ascii=False)}",
    ]))
    if existing_prompts:
        ground += ("\n\nALREADY EXISTING exercises (do NOT repeat these sentences or "
                   "near-variants):\n- " + "\n- ".join(existing_prompts[-40:]))
    resp = _get_client().messages.create(
        model=CHAPTER_MODEL,   # Content-Arbeit pro Kapitel — Qualität vor Kosten, wie der Seed
        max_tokens=4000,
        system=EXERCISES_SYSTEM,
        messages=[{"role": "user", "content": f"{ground}\n\nWrite {n} exercises now."}],
        output_config={"format": {"type": "json_schema", "schema": EXERCISES_SCHEMA}},
    )
    raw = json.loads(next(b.text for b in resp.content if b.type == "text"))["exercises"]
    # Validierung ist Code, nicht Vertrauen: kaputte mcq (Antwort nicht in den Optionen) fliegen.
    clean = []
    for ex in raw:
        if not ex["answers"]:
            continue
        if ex["etype"] == "mcq":
            if len(ex["options"]) < 2 or ex["answers"][0] not in ex["options"]:
                continue
        else:
            if "___" not in ex["prompt"]:
                continue
            ex["options"] = None
        clean.append(ex)
    return clean


# ---------------------------------------------------------------------------
# Transkription (Whisper) — der Audio-Eingang des einen Capture-Trichters.
# Fremder Speech-Stack, gleiche Naht: KI-Aufrufe leben nur in diesem Modul.
# ---------------------------------------------------------------------------
_openai_client = None

TRANSCRIBE_MODEL = "gpt-4o-transcribe"  # Whisper-Nachfolger, gleicher Endpoint — deutlich
                                        # stärker bei schnellem, umgangssprachlichem Audio

_AUDIO_EXT = {"audio/webm": "webm", "audio/mp4": "mp4", "audio/mpeg": "mp3",
              "audio/ogg": "ogg", "audio/wav": "wav", "audio/m4a": "m4a",
              "audio/x-m4a": "m4a", "audio/aac": "aac"}


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set — Voz-Transkription braucht ihn")
        from openai import OpenAI
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client


def transcribe(audio_b64: str, media_type: str = "audio/webm") -> str:
    """Audio (base64) → Text in der Zielsprache. Der Transkript-Text läuft danach durch
    analyze() wie jede getippte Capture — ein Trichter, keine Sonderpfade."""
    import base64
    import io
    data = base64.b64decode(audio_b64)
    ext = _AUDIO_EXT.get(media_type.split(";")[0].strip().lower(), "webm")
    f = io.BytesIO(data)
    f.name = f"captura.{ext}"   # die API braucht den Dateinamen als Format-Hinweis
    resp = _get_openai_client().audio.transcriptions.create(
        model=TRANSCRIBE_MODEL, file=f, language=PACK.LANG)
    return resp.text.strip()


TTS_MODEL = "gpt-4o-mini-tts"   # Sprachausgabe fürs Hörverstehen — gleicher OpenAI-Key wie Whisper


def synthesize(text: str, voice: str = "alloy") -> bytes:
    """Text → gesprochenes Audio (mp3-Bytes). Für den Escucha-Modus (Hörverstehen)."""
    resp = _get_openai_client().audio.speech.create(
        model=TTS_MODEL, voice=voice, input=text, response_format="mp3",
        instructions="Habla en español peninsular, tono natural y conversacional, ritmo normal.")
    return resp.content


LISTENING_SCHEMA = {
    "type": "object",
    "properties": {
        "passage": {"type": "string"},
        "gist_de": {"type": "string"},
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "q": {"type": "string"},
                    "options": {"type": "array", "items": {"type": "string"}},
                    "answer": {"type": "string"},
                },
                "required": ["q", "options", "answer"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["passage", "gist_de", "questions"],
    "additionalProperties": False,
}


def generate_listening(target_terms: list[str], level: str = "A2-B1", n_q: int = 3) -> dict:
    """Kurzer Hörverstehens-Text (2-3 Sätze), der die Zielwörter des Users natürlich einwebt,
    plus MC-Verständnisfragen. LLM-Seam; Bewertung ist danach deterministisch (Option-Match)."""
    lang = _LANG_NAMES.get(PACK.LANG, "Spanish")
    system = (
        f"You write a SHORT listening-comprehension exercise in {lang} for a German learner "
        f"(level {level}), production variety {PACK.DEFAULT_VARIETY}. Produce:\n"
        "- passage: 2-3 natural, spoken-style sentences (everyday Barcelona life) that weave in "
        "as many of the TARGET words as fit naturally — don't force all of them, don't list them.\n"
        "- gist_de: ONE short German sentence — what the passage is about.\n"
        f"- questions: exactly {n_q} multiple-choice comprehension questions IN {lang}, each with "
        "3-4 options and exactly one correct 'answer' that equals one option VERBATIM. Test whether "
        "the listener UNDERSTOOD the passage (who/what/where/when/why) — never grammar. Distractors "
        "plausible and in the same register; questions simple and solvable from the passage alone."
    )
    resp = _get_client().messages.create(
        model=MICRO_MODEL, max_tokens=1500,   # A2-Text + einfache MC-Fragen — Haiku reicht, ~halb so lang
        thinking={"type": "disabled"},
        system=system,
        messages=[{"role": "user", "content": "Target words: " + ", ".join(target_terms)}],
        output_config={"format": {"type": "json_schema", "schema": LISTENING_SCHEMA}},
    )
    data = json.loads(next(b.text for b in resp.content if b.type == "text"))
    # Validierung ist Code: nur Fragen, deren Antwort wirklich unter den Optionen steht.
    qs = [q for q in data["questions"]
          if len(q["options"]) >= 2 and q["answer"] in q["options"]]
    return {"passage": data["passage"], "gist_de": data["gist_de"], "questions": qs}


CHAT_SYSTEM = PACK.CHAT_SYSTEM
CHAT_MODEL = MODEL          # interaktiv — schnell und günstig, nicht Opus
CHAT_MAX_HISTORY = 12       # Client schickt die History mit; wir kappen serverseitig


def answer_concept_question(concept: dict, question: str,
                            history: list[dict] | None = None) -> str:
    """Klärungsfrage zu EINEM Kapitel — der dritte, bewusste LLM-Seam. Gegroundet im
    Kapitel-Body + den eigenen Fehlern des Users. Bewegt NIE Lernstand — Chat erklärt nur."""
    ground = "\n".join(filter(None, [
        f"Chapter '{concept['label']}' (slug {concept['slug']}, CEFR {concept.get('cefr') or '?'}).",
        concept.get("explanation") and f"Explanation: {concept['explanation']}",
        concept.get("rule_of_thumb") and f"Rule of thumb: {concept['rule_of_thumb']}",
        concept.get("german_pitfall") and f"German pitfall: {concept['german_pitfall']}",
        concept.get("paradigm") and f"Paradigm: {json.dumps(concept['paradigm'], ensure_ascii=False)}",
        (corr := concept.get("corrections")) and "User's own mistakes in this chapter:\n" +
            "\n".join(f"- '{c['wrong']}' → '{c['correct']}'" for c in corr[:8]),
    ]))
    msgs = [{"role": m["role"], "content": str(m["content"])[:2000]}
            for m in (history or [])[-CHAT_MAX_HISTORY:]
            if m.get("role") in ("user", "assistant") and m.get("content")]
    msgs.append({"role": "user", "content": question})
    resp = _get_client().messages.create(
        model=CHAT_MODEL,
        max_tokens=800,
        system=f"{CHAT_SYSTEM}\n\n## Chapter content (your ground truth)\n{ground}",
        messages=msgs,
    )
    return next(b.text for b in resp.content if b.type == "text")


def normalize_answer(s: str) -> str:
    """Antwort-Normalisierung fürs Grading: Groß/klein, Randspaces, Mehrfachspaces,
    Satzzeichen am Rand. Akzente bleiben SIGNIFIKANT (está != esta — das ist Lernstoff)."""
    return " ".join(s.split()).strip(" .!?¡¿,;:").lower()


def grade_exercise(exercise: dict, answer: str) -> bool:
    """Deterministisch: Antwort gegen die akzeptierten Varianten. Kein LLM, nie."""
    got = normalize_answer(answer)
    return got in {normalize_answer(a) for a in exercise["answers"]}


def apply_exercise_result(db, user_id: str, concept_id: str, correct: bool) -> dict:
    """Übungsergebnis bewegt den Konzept-State wie Capture-Evidenz — dieselben Counter,
    dieselben Schwellen, derselbe deterministische Pfad."""
    state = db.get_or_create_state(user_id, concept_id)
    if correct:
        state["success_count"] += 1
        _recompute_state(state, "success")
    else:
        state["need_count"] += 1
        _recompute_state(state, "error")
    db.save_state(state)
    return {"state": state["state"], "need": state["need_count"],
            "success": state["success_count"]}


def _clean_region(value):
    """Belt-and-braces: the schema asks for JSON null, but normalize stray string variants."""
    if value is None:
        return None
    v = value.strip().lower()
    return None if v in ("null", "none", "") else v


def analyze(raw_text: str, variety: str | None = None,
            image_b64: str | None = None, image_media_type: str = "image/jpeg",
            known_slugs: list[str] | None = None) -> dict:
    """One brain for all four capture modes. Optionally takes a photo (base64) — Claude
    reads it directly, no separate OCR step. known_slugs is the existing concept backbone:
    injecting it makes slug reuse happen at the source instead of spawning near-duplicates."""
    content: list | str = raw_text
    if image_b64:
        content = [
            {"type": "image",
             "source": {"type": "base64", "media_type": image_media_type, "data": image_b64}},
            {"type": "text", "text": raw_text or "(foto capturada)"},
        ]

    system = SYSTEM_PROMPT.replace("{variety}", variety or PACK.DEFAULT_VARIETY)
    if known_slugs:
        system += (
            "\n\nEXISTING concept slugs — ALWAYS reuse one of these when it covers the "
            "phenomenon (even partially); invent a new slug only for something genuinely "
            "uncovered:\n" + ", ".join(known_slugs)
        )

    resp = _get_client().messages.create(
        model=MODEL,
        max_tokens=3000,  # brief packages are the biggest legitimate output
        thinking={"type": "disabled"},  # pure extraction — no thinking tokens competing with output
        system=system,
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
# Phase 1: der schnelle Feedback-Call. NUR die Microdose, die der Nutzer sofort sieht
# (mode/gist/correction/word). Kleines Schema + Haiku → ~halbe Wartezeit gegenüber der
# vollen Analyse. Die volle analyze() (Konzepte/Vokabeln/Lernstand) läuft danach getrennt.
# ---------------------------------------------------------------------------
MICRO_MODEL = "claude-haiku-4-5-20251001"

MICRO_SCHEMA = {
    "type": "object",
    "properties": {
        "mode": {"type": "string", "enum": ["check", "decode", "brief", "listen", "word"]},
        "gist": _NULLABLE_STR,
        "correction": {
            "anyOf": [
                {"type": "object",
                 "properties": {"wrong": {"type": "string"}, "correct": {"type": "string"},
                                "why": {"type": "string"}, "concept_slug": {"type": "string"}},
                 "required": ["wrong", "correct", "why", "concept_slug"],
                 "additionalProperties": False},
                {"type": "null"},
            ]
        },
        "word": {
            "anyOf": [
                {"type": "object",
                 "properties": {"term": {"type": "string"}, "translation": {"type": "string"}},
                 "required": ["term", "translation"], "additionalProperties": False},
                {"type": "null"},
            ]
        },
    },
    "required": ["mode", "gist", "correction", "word"],
    "additionalProperties": False,
}

_LANG_NAMES = {"es": "Spanish", "ca": "Catalan"}


def _micro_system(variety: str | None) -> str:
    lang = _LANG_NAMES.get(PACK.LANG, "Spanish")
    v = variety or PACK.DEFAULT_VARIETY
    s = (
        f"You are the fast-feedback engine of a {lang}-learning tool for a German speaker in "
        f"Barcelona (production variety: {v}). Return ONLY the immediate micro-dose. "
        "Infer the mode from the input:\n"
        f"- check: the user produced {lang}. If there is a real error, fill correction (wrong, "
        "correct, why = ONE short German sentence, concept_slug = kebab-case canonical grammar "
        f"slug). gist = German meaning of the CORRECTED sentence. If it is fine, correction=null.\n"
        "- decode / listen: something captured or overheard. gist = plain German translation, "
        "correction=null.\n"
        "- brief: the user asks to be prepared for a situation ('prepárame para...'). "
        "gist=null, correction=null — the package is built elsewhere.\n"
        f"- word: a SINGLE word or short fixed expression ({lang} OR German), no sentence around "
        f"it. Fill word (term = dictionary form in {lang}, nouns WITH article; translation = the "
        "German meaning). gist=null, correction=null.\n"
        "For comprehension every regional variety is valid — never mark one as wrong. "
        "correction and word stay null unless their mode applies. "
        "concept_slug is a free kebab-case guess — the backbone gets matched later in the "
        "background pass, so no slug list is needed here."
    )
    return s


def analyze_micro(raw_text: str, variety: str | None = None, image_b64: str | None = None,
                  image_media_type: str = "image/jpeg") -> dict:
    """Der schnelle Feedback-Call — kleine Ausgabe, günstiges Modell. Was der Nutzer sofort
    sieht; die volle Analyse holt Konzepte/Vokabeln/Lernstand danach im Hintergrund nach.
    Braucht KEINE known_slugs: der Micro-concept_slug wird nie verwendet (das Frontend zeigt nur
    wrong/correct/why), die echte Slug-Zuordnung macht der Hintergrund-analyze(). Damit fällt ein
    Supabase-Roundtrip aus der kritischen Kette und der Haiku-Prompt schrumpft."""
    content: list | str = raw_text
    if image_b64:
        content = [
            {"type": "image",
             "source": {"type": "base64", "media_type": image_media_type, "data": image_b64}},
            {"type": "text", "text": raw_text or "(foto capturada)"},
        ]
    resp = _get_client().messages.create(
        model=MICRO_MODEL,
        max_tokens=600,
        thinking={"type": "disabled"},
        system=_micro_system(variety),
        messages=[{"role": "user", "content": content}],
        output_config={"format": {"type": "json_schema", "schema": MICRO_SCHEMA}},
    )
    return json.loads(next(b.text for b in resp.content if b.type == "text"))


# ---------------------------------------------------------------------------
# Everything below is DETERMINISTIC — no LLM. This is where learning state moves.
# The db object is implemented in db.py; this seam stays here so it's obvious
# that scoring/promotion/state transitions are code, never the model.
# ---------------------------------------------------------------------------
from datetime import datetime, timezone

NEED_THRESHOLD = 4  # tune with real data, later. Maybe ratio-based instead of fixed.
BOOST_AMOUNT = 5    # relevance boost a brief puts on its linked concepts ...
BOOST_DAYS = 7      # ... and how long it lives. Decays via compute_priority, never mixed into need.


def srs_update(item: dict, correct: bool, now: datetime | None = None) -> dict:
    """SM-2-lite, deterministic. Wrong answers reset to 'due now'; right answers stretch
    the interval by the ease factor. Returns only the fields to persist."""
    from datetime import timedelta
    now = now or datetime.now(timezone.utc)
    ease, reps, interval = item["srs_ease"], item["srs_reps"], item["srs_interval_days"]
    if correct:
        reps += 1
        interval = 1 if reps == 1 else 3 if reps == 2 else max(1, round(interval * ease))
        ease = min(2.8, ease + 0.05)
    else:
        reps, interval = 0, 0
        ease = max(1.3, round(ease - 0.2, 2))
    due = now + timedelta(days=interval)
    return {"srs_ease": ease, "srs_reps": reps,
            "srs_interval_days": interval, "srs_due": due.isoformat()}


def compute_priority(state: dict, now: datetime | None = None) -> int:
    """Chapter priority = durable need + temporary relevance boost.
    The two forces live in SEPARATE columns and only meet here, at read time:
    need persists until mastered; the boost dies with its expiry date."""
    now = now or datetime.now(timezone.utc)
    need = max(0, state["need_count"] - state["success_count"])
    boost = 0
    expires = state.get("boost_expires_at")
    if state.get("relevance_boost") and expires:
        if isinstance(expires, str):
            expires = datetime.fromisoformat(expires.replace("Z", "+00:00"))
        if now < expires:
            boost = state["relevance_boost"]
    return need + boost


def apply_analysis(db, user_id: str, capture_id: str, result: dict) -> dict:
    """Write the outcome. Reconcile slugs, bump counters, move states — all in code.
    Returns a small summary of what was written (for the API response).

    Atomicität: PostgREST kennt keine Transaktion über mehrere Calls. Statt die
    Scoring-Logik in eine plpgsql-RPC zu duplizieren (gegen die Architektur), sind hier
    die UNABHÄNGIGEN Einheiten isoliert: scheitert eine (ein kaputtes Konzept, ein DB-
    Aussetzer), machen die übrigen trotzdem Fortschritt statt alles zu verlieren. Der
    Capture-TEXT ist ohnehin schon synchron gesichert — hier geht nur Lernstand-Anreicherung
    verloren, nie die Rohdaten. Die Einheiten sind idempotent genug für einen Re-Run."""
    written = {"concepts": [], "vocab": [], "correction": None}

    # Wichtigstes zuerst: die Konzept-States (Lernstand) und die Korrektur (dein Fehler).
    for c in result.get("concepts", []):
        try:
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
        except Exception:
            logger.exception("apply_analysis: Konzept '%s' fehlgeschlagen (capture %s)",
                             c.get("slug"), capture_id)

    corr = result.get("correction")
    if corr:
        try:
            concept = db.get_or_create_concept(corr["concept_slug"], corr["concept_slug"], None)
            db.add_correction(user_id, capture_id, corr["wrong"], corr["correct"], concept["id"])
            written["correction"] = {"wrong": corr["wrong"], "correct": corr["correct"]}
        except Exception:
            logger.exception("apply_analysis: Korrektur fehlgeschlagen (capture %s)", capture_id)

    for lemma in result.get("lemmas", []):
        try:
            _, created = db.get_or_create_vocab_item(user_id, lemma, source_capture_id=capture_id)
            if created:
                written["vocab"].append(lemma["term"])
        except Exception:
            logger.exception("apply_analysis: Vokabel '%s' fehlgeschlagen (capture %s)",
                             lemma.get("term"), capture_id)

    brief = result.get("brief")
    if brief:
        try:
            written["situation"] = _apply_brief(db, user_id, capture_id, brief)
        except Exception:
            logger.exception("apply_analysis: Brief-Paket fehlgeschlagen (capture %s)", capture_id)

    return written


def _apply_brief(db, user_id: str, capture_id: str, brief: dict) -> dict:
    """A brief creates a shelf: situation + vocab + intent-phrases (same store), plus
    LINKS to grammar chapters with a temporary boost. Grammar is never copied in."""
    sit = db.get_or_create_situation(user_id, brief["situation_name"])

    for item in brief["key_vocab"]:
        vid, _ = db.get_or_create_vocab_item(user_id, item, source_capture_id=capture_id,
                                             situation_id=sit["id"])
        db.add_vocab_to_situation(sit["id"], vid)

    for ph in brief["phrases"]:
        vid, _ = db.get_or_create_vocab_item(
            user_id,
            {"term": ph["es"], "translation": ph["de"], "register": "neutral", "region": None},
            source_capture_id=capture_id, situation_id=sit["id"],
            tags=["frase", ph["intent"]],
        )
        db.add_vocab_to_situation(sit["id"], vid)

    for c in brief["concepts"]:
        concept = db.get_or_create_concept(c["slug"], c["label"], None)
        db.link_situation_concept(sit["id"], concept["id"], c["why"])
        db.boost_concept(user_id, concept["id"], BOOST_AMOUNT, BOOST_DAYS)

    return {"id": sit["id"], "name": sit["name"],
            "vocab": len(brief["key_vocab"]), "phrases": len(brief["phrases"]),
            "concepts": [c["slug"] for c in brief["concepts"]]}


def derive_state(need: int, success: int, fallback: str = "visto") -> str:
    """State purely from counters (used when merging duplicate concepts) — same thresholds
    as _recompute_state, just without an evidence event driving it."""
    if need >= NEED_THRESHOLD and success < need:
        return "aprendiendo"
    if need > 0 and success > need:
        return "dominado"
    if need > 0:
        return "flojo"
    return fallback


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
    elif evidence == "success" and state["state"] == "sin_ver":
        state["state"] = "visto"                      # produced correctly without ever struggling
