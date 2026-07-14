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

from analyze import analyze, apply_analysis, compute_priority
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
        "prep_hoy": [],  # Slice 7: briefs for today's dated situations
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
