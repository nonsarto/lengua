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

from analyze import analyze, apply_analysis
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
