"""
main.py — FastAPI backend. One meaningful endpoint: POST /capture.

Flow (the whole app in one line): raw input → analyze() (the ONE LLM seam) →
apply_analysis() (deterministic writes: captures, evidence, corrections, states, vocab).
The response is the micro-dose the UI shows; everything else is filed silently.
"""

from pathlib import Path

from dotenv import load_dotenv

# .env lives at the repo root, two levels up from backend/app/
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import random

from analyze import analyze, apply_analysis, compute_priority, srs_update
from db import get_db

app = FastAPI(title="lengua")

app.add_middleware(
    CORSMiddleware,
    # localhost + LAN-IPs (iPhone-Test im selben WLAN); Vercel-Domain kommt beim Deploy dazu
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)(:\d+)?",
    allow_methods=["*"],
    allow_headers=["*"],
)


class CaptureIn(BaseModel):
    text: str = ""
    source: str = "web"
    image_b64: str | None = None            # Foto → Claude Vision direkt, kein OCR
    image_media_type: str = "image/jpeg"


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/capture")
def capture(body: CaptureIn) -> dict:
    if not body.text.strip() and not body.image_b64:
        raise HTTPException(422, "Captura vacía — manda texto o una foto.")

    db = get_db()
    user_id = db.get_or_create_user()

    # 1. The one LLM seam.
    result = analyze(body.text, image_b64=body.image_b64,
                     image_media_type=body.image_media_type)

    # 2. Deterministic persistence — counters turn, states move, all in code.
    capture_id = db.create_capture(user_id, body.text or "(foto)", result["mode"], body.source)
    written = apply_analysis(db, user_id, capture_id, result)

    # 3. Micro-dose back to the UI: correction + translation + one sentence why. No full lesson.
    return {
        "capture_id": capture_id,
        "mode": result["mode"],
        "gist": result.get("gist"),
        "correction": result.get("correction"),
        "notes": result.get("notes", ""),
        "concepts": [{"slug": c["slug"], "label": c["label"]} for c in result.get("concepts", [])],
        "written": written,   # what was filed silently (for debugging/curiosity)
    }


@app.get("/inicio")
def inicio() -> dict:
    """The pulse. Three bands: en caliente / para repasar / prep para hoy — 3 seconds to
    know what today is about. Prep fills in with Slice 7 (briefs)."""
    db = get_db()
    user_id = db.get_or_create_user()
    due_count, due_preview = db.due_vocab(user_id)
    return {
        "en_caliente": db.hot_concepts(user_id),
        "para_repasar": {"due": due_count, "preview": due_preview},
        "prep_hoy": db.recent_situations(user_id),
    }


@app.get("/concepts")
def concepts_list() -> list[dict]:
    """Chapter list, priority-sorted: hot ones on top, mastered ones sink into quiet
    reference. Priority is deterministic (need + unexpired boost) — computed here, never LLM."""
    db = get_db()
    user_id = db.get_or_create_user()
    rows = db.list_concepts_with_state(user_id)
    for r in rows:
        r["priority"] = compute_priority(r)
        r.pop("relevance_boost", None)
        r.pop("boost_expires_at", None)
        r.pop("id", None)
    active_rank = {"aprendiendo": 0, "flojo": 1, "visto": 2, "dominado": 3, "sin_ver": 4}
    rows.sort(key=lambda r: (-r["priority"], active_rank.get(r["state"], 9),
                             r["cefr"] or "Z", r["label"]))
    return rows


@app.get("/concepts/{slug}")
def concept_detail(slug: str) -> dict:
    """One chapter: shared body (frozen reference) + personal mantle (your errors, your state).
    The body is the same for everyone; the mantle is what makes it yours."""
    db = get_db()
    user_id = db.get_or_create_user()
    detail = db.get_concept_detail(user_id, slug)
    if detail is None:
        raise HTTPException(404, f"Concepto '{slug}' no existe.")
    state = detail.pop("user_state", None)
    detail.pop("id", None)
    detail["state"] = {
        "state": state["state"] if state else "sin_ver",
        "need_count": state["need_count"] if state else 0,
        "success_count": state["success_count"] if state else 0,
        "priority": compute_priority(state) if state else 0,
    }
    return detail


# ---------------------------------------------------------------------------
# Practicar — three drill types, ONE store. Selection is deterministic: it pulls
# exactly the items where your scoring wobbles (due SRS, shaky concepts, shaky patterns).
# ---------------------------------------------------------------------------

# Which conjugation table a shaky concept exercises. Pattern families mostly live in the
# present; the strong-preterite family in the indefinido; tense concepts in themselves.
PATTERN_TENSE = {
    "stem-change-e-ie": "presente", "stem-change-o-ue": "presente", "stem-change-e-i": "presente",
    "g-verbs": "presente", "zc-verbs": "presente", "y-verbs": "presente",
    "irregular-indefinido": "indefinido", "irregular-futuro": "futuro",
    "irregular-participio": "participio", "irregular-imperativo": "imperativo",
    "presente-indicativo": "presente", "indefinido": "indefinido", "imperfecto": "imperfecto",
    "futuro-simple": "futuro", "condicional-simple": "condicional",
    "subjuntivo-presente": "subjuntivo_presente",
    "indefinido-vs-perfecto": "indefinido", "perfecto": "participio",
}
TENSE_LABEL = {
    "presente": "presente", "indefinido": "indefinido", "imperfecto": "imperfecto",
    "futuro": "futuro", "condicional": "condicional",
    "subjuntivo_presente": "subjuntivo presente", "imperativo": "imperativo",
    "participio": "participio", "gerundio": "gerundio",
}
PERSONS = ["yo", "tu", "el", "nosotros", "vosotros", "ellos"]
PERSON_LABEL = {"yo": "yo", "tu": "tú", "el": "él/ella", "nosotros": "nosotros",
                "vosotros": "vosotros", "ellos": "ellos/ellas", "usted": "usted"}


def _conj_drills(db, shaky: list[dict], limit: int = 5) -> list[dict]:
    """Verb+tense+person cards from the shaky pattern families / tenses."""
    slugs = [s["slug"] for s in shaky if s["slug"] in PATTERN_TENSE]
    verbs = db.verbs_for_patterns([s for s in slugs if not s.endswith("-vs-perfecto")]) \
        or (db.frequent_verbs() if slugs else [])
    drills: list[dict] = []
    for verb in verbs:
        if len(drills) >= limit:
            break
        matched = [s for s in slugs if s in (verb.get("pattern_tags") or [])] or slugs
        tense = PATTERN_TENSE[matched[0]]
        table = (verb.get("conjugations") or {}).get(tense)
        if table is None:
            continue
        if isinstance(table, str):                      # gerundio/participio: single form
            person, answer = None, table
        else:
            pool = PERSONS if tense != "imperativo" else list(table)
            # Stem changes only hit the stressed stem — nosotros/vosotros don't diphthongize,
            # so drilling them there would miss the very thing the pattern is about.
            if matched[0].startswith("stem-change"):
                pool = [p for p in pool if p not in ("nosotros", "vosotros")]
            candidates = [p for p in pool if table.get(p) and table[p] != "—"]
            if not candidates:
                continue
            person = random.choice(candidates)
            answer = table[person]
        drills.append({
            "type": "conj", "verb": verb["infinitive"], "verb_de": verb["translation"],
            "tense": TENSE_LABEL[tense], "person": PERSON_LABEL.get(person, person),
            "answer": answer, "pattern": matched[0],
        })
    return drills


@app.get("/practicar/session")
def practicar_session() -> dict:
    db = get_db()
    user_id = db.get_or_create_user()
    items: list[dict] = []

    # 1) Vokabel-Recall: SRS-fällige Items (Herkunft hat die Startposition geseedet)
    for v in db.due_vocab_items(user_id, limit=8):
        items.append({"type": "vocab", "vocab_id": v["id"], "prompt": v["translation"],
                      "answer": v["term"], "register": v["register"],
                      "is_phrase": "frase" in (v.get("tags") or [])})

    # 2) Konzept-Anwendung: deine ECHTEN Fehlersätze wackliger Konzepte, nicht generisch
    shaky = db.shaky_concepts(user_id)
    seen: set[tuple[str, str]] = set()
    for corr in db.corrections_for_concepts(user_id, [s["concept_id"] for s in shaky]):
        key = (corr["wrong"], corr["correct"])
        if key in seen or len(seen) >= 5:
            continue
        seen.add(key)
        items.append({"type": "fix", "prompt": corr["wrong"], "answer": corr["correct"],
                      "concept_slug": corr["concepts"]["slug"],
                      "concept_label": corr["concepts"]["label"]})

    # 3) Konjugations-Drill: aus wackligen Mustern/Tempora
    items.extend(_conj_drills(db, shaky))

    return {"items": items}


class GradeIn(BaseModel):
    vocab_id: str
    correct: bool


@app.post("/practicar/grade")
def practicar_grade(body: GradeIn) -> dict:
    """SRS moves only here, deterministically (SM-2-lite in analyze.py)."""
    db = get_db()
    user_id = db.get_or_create_user()
    item = db.get_vocab_item(user_id, body.vocab_id)
    if item is None:
        raise HTTPException(404, "Vocab item no existe.")
    patch = srs_update(item, body.correct)
    db.update_vocab_srs(body.vocab_id, patch)
    return {"interval_days": patch["srs_interval_days"], "due": patch["srs_due"]}


# ---------------------------------------------------------------------------
# Vocabulario — shelves (situations), not a flat word list.
# ---------------------------------------------------------------------------

@app.get("/vocabulario")
def vocabulario() -> dict:
    db = get_db()
    user_id = db.get_or_create_user()
    return {"situations": db.list_situations(user_id), "sueltas": db.loose_vocab(user_id)}


@app.get("/situations/{situation_id}")
def situation_detail(situation_id: str) -> dict:
    db = get_db()
    user_id = db.get_or_create_user()
    detail = db.get_situation_detail(user_id, situation_id)
    if detail is None:
        raise HTTPException(404, "Situación no existe.")
    words = [i for i in detail["items"] if "frase" not in (i.get("tags") or [])]
    phrases = [{"intent": next((t for t in i["tags"] if t != "frase"), ""),
                "es": i["term"], "de": i["translation"]}
               for i in detail["items"] if "frase" in (i.get("tags") or [])]
    return {"id": detail["id"], "name": detail["name"], "is_seed": detail["is_seed"],
            "words": words, "phrases": phrases, "concepts": detail["concepts"]}


@app.get("/captures")
def captures(limit: int = 20) -> list[dict]:
    """History for the Capturar screen: what you threw in, newest first."""
    db = get_db()
    user_id = db.get_or_create_user()
    rows = db.list_captures(user_id, limit=min(limit, 50))
    return [{
        "id": r["id"],
        "text": r["raw_text"],
        "mode": r["kind"],
        "created_at": r["created_at"],
        "correction": (r["corrections"][0] if r.get("corrections") else None),
    } for r in rows]
