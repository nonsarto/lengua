"""
main.py — FastAPI backend. One meaningful endpoint: POST /capture.

Flow (the whole app in one line): raw input → analyze() (the ONE LLM seam) →
apply_analysis() (deterministic writes: captures, evidence, corrections, states, vocab).
The response is the micro-dose the UI shows; everything else is filed silently.
"""

import logging
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

# .env lives at the repo root, two levels up from backend/app/
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import random

import onboarding
from lang import get_lang

PACK = get_lang()
from analyze import (analyze, analyze_document, analyze_micro, answer_concept_question,
                     apply_analysis, apply_document, apply_exercise_result, compute_priority,
                     generate_chapter_body, generate_exercises, generate_listening,
                     grade_exercise, srs_update, synthesize, transcribe)
from auth import hash_password, make_token, user_id_from_token, verify_password
from db import get_db
import importer

logger = logging.getLogger("lengua")

app = FastAPI(title=PACK.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    # Prod: exakte Frontend-Domain via env; Dev: localhost + LAN-IPs (iPhone im WLAN);
    # dazu Vercel-Preview-Deploys. Auth läuft über Bearer-Token, nicht Cookies.
    allow_origins=[o for o in [os.environ.get("FRONTEND_ORIGIN")] if o],
    allow_origin_regex=(
        r"http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)(:\d+)?"
        r"|https://.*\.vercel\.app"
    ),
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Auth — Admin legt Nutzer an, jeder Endpunkt unten läuft als angemeldeter Nutzer.
# ---------------------------------------------------------------------------

def current_user(user_id: str = Depends(user_id_from_token)) -> dict:
    user = get_db().get_user_by_id(user_id)
    if user is None:
        raise HTTPException(401, "Usuario no existe.")
    return user


def admin_user(user: dict = Depends(current_user)) -> dict:
    if not user.get("is_admin"):
        raise HTTPException(403, "Solo para admins.")
    return user


def _public_user(user: dict) -> dict:
    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "display_name": user["display_name"],
        "is_admin": user["is_admin"],
        "onboarded": user.get("onboarded_at") is not None,
        "level_estimate": user.get("level_estimate"),
    }


class LoginIn(BaseModel):
    username: str
    password: str


class UserIn(BaseModel):
    username: str
    password: str
    display_name: str = ""


class PasswordIn(BaseModel):
    password: str


@app.post("/auth/login")
def login(body: LoginIn) -> dict:
    db = get_db()
    user = db.get_user_by_username(body.username.lower().strip())
    if user is None or not verify_password(body.password, user.get("password_hash")):
        raise HTTPException(401, "Usuario o contraseña incorrectos.")
    return {"token": make_token(user["user_id"]), "user": _public_user(user)}


@app.get("/auth/me")
def me(user: dict = Depends(current_user)) -> dict:
    return _public_user(user)


@app.get("/admin/users")
def admin_list_users(user: dict = Depends(admin_user)) -> list[dict]:
    return [{k: v for k, v in u.items()} for u in get_db().list_users()]


@app.post("/admin/users")
def admin_create_user(body: UserIn, user: dict = Depends(admin_user)) -> dict:
    username = body.username.lower().strip()
    if not username.isalnum() or len(username) < 2:
        raise HTTPException(422, "Username: solo letras/números, mínimo 2.")
    if len(body.password) < 8:
        raise HTTPException(422, "Contraseña: mínimo 8 caracteres.")
    db = get_db()
    if db.get_user_by_username(username):
        raise HTTPException(409, f"'{username}' ya existe.")
    created = db.create_user(username, hash_password(body.password),
                             body.display_name.strip() or username.capitalize())
    return _public_user(created)


@app.post("/admin/users/{target_id}/password")
def admin_reset_password(target_id: str, body: PasswordIn,
                         user: dict = Depends(admin_user)) -> dict:
    if len(body.password) < 8:
        raise HTTPException(422, "Contraseña: mínimo 8 caracteres.")
    db = get_db()
    if db.get_user_by_id(target_id) is None:
        raise HTTPException(404, "Usuario no existe.")
    db.update_user(target_id, {"password_hash": hash_password(body.password)})
    return {"ok": True}


@app.delete("/admin/users/{target_id}")
def admin_delete_user(target_id: str, user: dict = Depends(admin_user)) -> dict:
    """Nutzer samt aller Daten löschen. Sich selbst löschen geht nicht —
    sonst sperrt sich der letzte Admin aus."""
    if target_id == user["user_id"]:
        raise HTTPException(422, "No puedes eliminarte a ti mismo.")
    db = get_db()
    if db.get_user_by_id(target_id) is None:
        raise HTTPException(404, "Usuario no existe.")
    db.delete_user_full(target_id)
    return {"ok": True}


# Username des Speaking-Bots für den Pairing-Deep-Link. Per Env überschreibbar;
# Default = der echte Bot der es-Instanz (@hablalengbot).
TELEGRAM_BOT_USERNAME = os.environ.get("TELEGRAM_BOT_USERNAME", "hablalengbot")


@app.post("/admin/users/{target_id}/telegram-link")
def admin_telegram_link(target_id: str, user: dict = Depends(admin_user)) -> dict:
    """Pairing-Link für den Telegram-Speaking-Bot erzeugen (Migration 013 sah genau
    diesen Erzeugungsweg vor). Der Link öffnet den Chat und schickt /start <code>;
    der Bot löst den Code ein und verbindet chat_id ↔ user_id. 24 h gültig, einmalig."""
    db = get_db()
    if db.get_user_by_id(target_id) is None:
        raise HTTPException(404, "Usuario no existe.")
    code = db.create_pairing_code(target_id)
    return {"code": code, "expires_hours": 24,
            "link": f"https://t.me/{TELEGRAM_BOT_USERNAME}?start={code}"}


# ---------------------------------------------------------------------------
# Onboarding — 12 Fragen, ~3 Minuten, deterministische Auswertung sät die States.
# ---------------------------------------------------------------------------

class OnboardingIn(BaseModel):
    answers: dict[str, int]  # question id -> chosen option index


@app.get("/onboarding")
def onboarding_questions(user: dict = Depends(current_user)) -> dict:
    return {"questions": onboarding.public_questions(),
            "done": user.get("onboarded_at") is not None}


@app.post("/onboarding")
def onboarding_submit(body: OnboardingIn, user: dict = Depends(current_user)) -> dict:
    db = get_db()
    # Slot atomar holen (onboarded_at nur wenn null) — NUR der Gewinner sät die States.
    # Ersetzt die frühere check-then-act-Prüfung, die bei Doppel-Submit doppelt säen konnte.
    if not db.claim_onboarding(user["user_id"]):
        raise HTTPException(409, "El test de nivel ya está hecho.")
    return onboarding.grade(db, user["user_id"], body.answers)


class CaptureIn(BaseModel):
    text: str = ""
    source: str = "web"
    image_b64: str | None = None            # Foto → Claude Vision direkt, kein OCR
    image_media_type: str = "image/jpeg"
    audio_b64: str | None = None            # Aufnahme → Whisper → Transkript → analyze()
    audio_media_type: str = "audio/webm"


@app.get("/health")
def health() -> dict:
    return {"ok": True}


def _full_analyze_and_persist(user_id: str, capture_id: str, text: str,
                              image_b64, image_media_type: str, variety) -> None:
    """Phase 2, deferred: die VOLLE Analyse (Konzepte/Vokabeln/Lernstand) + Anreicherung.
    Läuft NACH der Antwort. Die Capture-Zeile besteht bereits (synchron mit der Microdose
    angelegt) — scheitert das hier, bleibt der Text also erhalten, nur die Voll-Analyse fehlt.
    Holt sich die Slugs hier selbst: dieser Roundtrip liegt außerhalb der kritischen Kette."""
    try:
        db = get_db()
        result = analyze(text, variety=variety, image_b64=image_b64,
                         image_media_type=image_media_type,
                         known_slugs=db.list_concept_slugs())
        apply_analysis(db, user_id, capture_id, result)
        db.update_capture_analysis(user_id, capture_id, result["mode"], result)
    except Exception:
        logger.exception("Deferred full analysis failed (capture %s, user %s)",
                         capture_id, user_id)


@app.post("/capture")
def capture(body: CaptureIn, background: BackgroundTasks,
            user: dict = Depends(current_user)) -> dict:
    if not body.text.strip() and not body.image_b64 and not body.audio_b64:
        raise HTTPException(422, "Captura vacía — manda texto, una foto o audio.")

    db = get_db()
    user_id = user["user_id"]
    variety = user.get("production_variety")

    # 0. Audio zuerst zu Text — danach ist es eine ganz normale Capture (ein Trichter).
    transcript = None
    text = body.text
    if body.audio_b64:
        try:
            transcript = transcribe(body.audio_b64, body.audio_media_type)
        except RuntimeError as e:
            raise HTTPException(503, str(e))
        except Exception:
            logger.exception("Transcription failed (user %s)", user_id)
            raise HTTPException(502, "No se pudo transcribir el audio — inténtalo otra vez.")
        if not transcript and not text.strip() and not body.image_b64:
            raise HTTPException(422, "No se oyó nada en el audio.")
        text = f"{text.strip()}\n\n{transcript}".strip() if text.strip() else transcript

    # 1. Phase 1 — der schnelle Feedback-Call. NUR die Microdose (Haiku, ~halbe Wartezeit).
    #    KEIN Slug-Fetch davor: die Microdose braucht die Slugs nicht (s. analyze_micro).
    micro = analyze_micro(text, variety=variety, image_b64=body.image_b64,
                          image_media_type=body.image_media_type)
    mode = micro["mode"]
    base = {"gist": micro.get("gist"), "correction": micro.get("correction"),
            "word": None, "transcript": transcript, "notes": "", "concepts": []}

    # brief: das Paket braucht die volle, strukturierte Analyse + die Situation-ID → synchron.
    if mode == "brief":
        result = analyze(text, variety=variety, image_b64=body.image_b64,
                         image_media_type=body.image_media_type,
                         known_slugs=db.list_concept_slugs())
        capture_id = db.create_capture(user_id, text or "(foto)", result["mode"],
                                       body.source, analysis=result)
        written = apply_analysis(db, user_id, capture_id, result)
        return {**base, "capture_id": capture_id, "mode": result["mode"],
                "gist": result.get("gist"), "correction": result.get("correction"),
                "notes": result.get("notes", ""),
                "concepts": [{"slug": c["slug"], "label": c["label"]}
                             for c in result.get("concepts", [])],
                "written": written}

    # word: die Microdose IST der Wörterbucheintrag — direkt ablegen (Dedup-Check für "añadido").
    if mode == "word" and micro.get("word"):
        capture_id = db.create_capture(user_id, text or "(foto)", "word", body.source,
                                       analysis=micro)
        w = micro["word"]
        _, created = db.get_or_create_vocab_item(
            user_id, {"term": w["term"], "translation": w["translation"],
                      "register": "neutral", "region": None},
            source_capture_id=capture_id)
        return {**base, "capture_id": capture_id, "mode": "word", "gist": None,
                "correction": None,
                "word": {"term": w["term"], "translation": w["translation"], "added": created},
                "written": None}

    # check / decode / listen: Capture SOFORT synchron sichern (Microdose als Analyse-Fallback),
    # dann Microdose zurück; die volle Analyse reichert im Hintergrund an. So ist "guardado ✓"
    # ehrlich — der Text geht nie verloren, selbst wenn die Voll-Analyse scheitert.
    capture_id = str(uuid.uuid4())
    db.create_capture(user_id, text or "(foto)", mode, body.source,
                      capture_id=capture_id, analysis=micro)
    background.add_task(_full_analyze_and_persist, user_id, capture_id, text or "(foto)",
                        body.image_b64, body.image_media_type, variety)
    return {**base, "capture_id": capture_id, "mode": mode, "written": None}


@app.get("/inicio")
def inicio(user: dict = Depends(current_user)) -> dict:
    """Der Puls: die 3 dringendsten Grammatik-Themen + der Vokabel-Stand. Priorität ist
    deterministisch (need + Boost); die Begrüßung baut das Frontend (Name + Tageszeit)."""
    db = get_db()
    user_id = user["user_id"]
    rows = db.list_concepts_with_state(user_id)
    for r in rows:
        r["priority"] = compute_priority(r)
    # Nur Kapitel mit echtem persönlichem Signal (Bedarf oder berührt) — sonst zeigt
    # Inicio vor der ersten Handlung schon "deine" Grammatik und der Leerzustand
    # des Frontends ist unerreichbar.
    rows = [r for r in rows if r["priority"] > 0 or r["state"] != "sin_ver"]
    active_rank = {"aprendiendo": 0, "flojo": 1, "visto": 2, "dominado": 3, "sin_ver": 4}
    rows.sort(key=lambda r: (-r["priority"], active_rank.get(r["state"], 9),
                             -r.get("need_count", 0)))
    top = [{"slug": r["slug"], "label": r["label"], "cefr": r["cefr"],
            "state": r["state"], "need_count": r["need_count"]} for r in rows[:3]]
    due_count, due_preview = db.due_vocab(user_id)
    return {"top_grammar": top, "vocab": {"due": due_count, "preview": due_preview}}


# ---------------------------------------------------------------------------
# Sesión diaria — der eingefrorene 15-Minuten-Bogen. Der Generator ist DETERMINISTISCH
# (Auswahl/Rangfolge/Zeitbudget); er ruft nur EINEN bestehenden Content-Seam
# (generate_exercises) nach, falls das Kern-Konzept noch keine Übungen hat. Bewertung
# läuft über die bestehenden Pfade (/practicar/grade, /exercises/{id}/answer) — Lernstand
# bewegt sich exakt wie bisher, hier wird nichts Neues erfunden.
# ---------------------------------------------------------------------------

SESSION_BUDGET = 1200                                 # 20 Min als Versprechen, nicht Schätzung
SESSION_ARC = {"warmup": 240, "core": 720, "cooldown": 240}   # 20 / 60 / 20 — Grammatik im Fokus
ITEM_COST = {"vocab": 15, "fix": 30, "exercise": 60, "explain": 90}   # grobe Sekunden je Item
# So viele Übungen soll der Kern-Block mindestens haben; darunter wird per LLM aufgefüllt.
# (Kern-Budget minus Erklärungskarte / Kosten je Übung ≈ 10 → 8 lässt Luft für Fehlersätze.)
CORE_MIN_EXERCISES = 8


def _session_exercise_item(e: dict, slug: str, label: str) -> dict:
    return {"kind": "exercise", "cost": ITEM_COST["exercise"], "exercise_id": e["id"],
            "etype": e["etype"], "prompt": e["prompt"], "options": e["options"],
            "concept_slug": slug, "concept_label": label}


def _session_vocab_item(v: dict) -> dict:
    return {"kind": "vocab", "cost": ITEM_COST["vocab"], "vocab_id": v["id"],
            "prompt": v["translation"], "answer": v["term"], "register": v.get("register"),
            "is_phrase": "frase" in (v.get("tags") or [])}


def _pick_core_concept(db, user_id: str, level: str | None, exclude_slug: str | None = None):
    """Genau EIN Grammatik-Konzept. Zuerst der höchste persönliche Bedarf (compute_priority);
    ist der Bedarf leer, ein zufälliges ungelerntes Konzept aus dem CEFR-Band des Nutzers.
    exclude_slug (bei Reroll gesetzt) = das zuletzt geübte Konzept: das gleiche nicht direkt
    wiederholen, solange es eine andere Option gibt — sonst darf es fallbacken."""
    rows = db.list_concepts_with_state(user_id)
    scored = [(compute_priority(r), r) for r in rows]     # priority einmal berechnen
    needful = sorted((t for t in scored if t[0] > 0), key=lambda t: -t[0])
    if needful:
        # höchster Bedarf, aber nicht das zuletzt geübte — außer es ist der einzige mit Bedarf
        chosen = next((r for _, r in needful if r["slug"] != exclude_slug), needful[0][1])
    else:
        unlearned = [r for r in rows if r["state"] in ("sin_ver", "visto")]
        band = [r for r in unlearned if (r.get("cefr") or "") == (level or "")]
        pool = band or unlearned or rows
        pool = [r for r in pool if r["slug"] != exclude_slug] or pool
        if not pool:
            return None
        chosen = random.choice(pool)
    return db.get_concept_detail(user_id, chosen["slug"])


def _build_core(db, user_id: str, level: str | None,
                exclude_slug: str | None = None) -> tuple[list[dict], str]:
    """Der schwere Kern: 1 Erklärungs-Karte + Übungen aus echten Fehlern. Übungen: vorhandene
    zuerst; hat das Kapitel keine, wird generate_exercises() EINMAL nachgeladen (Fallback auf
    Fehlersätze/nichts, wenn der Call scheitert)."""
    detail = _pick_core_concept(db, user_id, level, exclude_slug)
    if detail is None:
        return [], ""
    slug, label, cefr = detail["slug"], detail["label"], detail.get("cefr")
    items: list[dict] = []
    if detail.get("explanation"):
        items.append({"kind": "explain", "cost": ITEM_COST["explain"], "concept_slug": slug,
                      "label": label, "explanation": detail["explanation"],
                      "rule_of_thumb": detail.get("rule_of_thumb"),
                      "german_pitfall": detail.get("german_pitfall")})

    exs = db.exercises_for_concept(detail["id"])
    attempts = db.exercise_attempts(user_id, [e["id"] for e in exs]) if exs else {}
    unseen = [e for e in exs if e["id"] not in attempts]
    # Neu generieren, sobald zu wenige UNGESEHENE für den Kern übrig sind — nicht erst, wenn
    # der Pool insgesamt klein ist. So wiederholt sich nichts, bis wirklich alles geübt wurde;
    # dann kommt eine frische Charge (Sperrliste gegen Dubletten, wie der Kapitel-Knopf).
    if len(unseen) < CORE_MIN_EXERCISES:
        try:
            batch = generate_exercises(slug, label, cefr, detail,
                                       existing_prompts=[e["prompt"] for e in exs])
            db.insert_exercises(detail["id"], batch, cefr)
            exs = db.exercises_for_concept(detail["id"])
            attempts = db.exercise_attempts(user_id, [e["id"] for e in exs])
        except Exception:
            logger.exception("session: Übungs-Generierung fehlgeschlagen (%s)", slug)

    # Ungesehene zuerst (in zufälliger Reihenfolge), dann zuletzt-falsche, dann zuletzt-richtige.
    def _order_key(e):
        a = attempts.get(e["id"])
        if a is None:
            return (0, 0)
        return (1, a["count"]) if a.get("last_correct") is False else (2, a["count"])
    random.shuffle(exs)
    exs.sort(key=_order_key)

    budget = SESSION_ARC["core"] - sum(i["cost"] for i in items)
    for e in exs:
        if budget < ITEM_COST["exercise"]:
            break
        items.append(_session_exercise_item(e, slug, label))
        budget -= ITEM_COST["exercise"]

    # Auffüllen / Fallback mit deinen ECHTEN Fehlersätzen zu diesem Konzept.
    if budget >= ITEM_COST["fix"]:
        seen = set()
        for corr in db.corrections_for_concepts(user_id, [detail["id"]]):
            key = (corr["wrong"], corr["correct"])
            if key in seen or budget < ITEM_COST["fix"]:
                continue
            seen.add(key)
            items.append({"kind": "fix", "cost": ITEM_COST["fix"], "prompt": corr["wrong"],
                          "answer": corr["correct"], "concept_slug": slug, "concept_label": label})
            budget -= ITEM_COST["fix"]
    return items, label


def _build_session_plan(db, user_id: str, level: str | None,
                        exclude_slug: str | None = None) -> tuple[list[dict], str]:
    """Der Bogen: leichter Einstieg → schwerer Kern (EIN Konzept) → leichter Ausklang.
    Füllt bis zum Zeitbudget und hört auf. Baut auch bei komplett leerem Bedarf eine
    sinnvolle Session (dann 100 % Standard-Rückgrat). exclude_slug = zuletzt geübtes
    Kern-Konzept (Reroll) — nicht direkt wiederholen."""
    db.promote_daily_seed(user_id)   # Standard-Wörter nachrücken (no-op ohne seed_vocab)

    items: list[dict] = []

    # 1. Einstieg — Vokabeln, die fast sitzen.
    budget = SESSION_ARC["warmup"]
    for v in db.warmup_vocab(user_id, limit=SESSION_ARC["warmup"] // ITEM_COST["vocab"]):
        if budget < ITEM_COST["vocab"]:
            break
        items.append(_session_vocab_item(v))
        budget -= ITEM_COST["vocab"]

    # 2. Kern — genau EIN Grammatik-Konzept.
    core_items, core_label = _build_core(db, user_id, level, exclude_slug)
    items += core_items

    # 3. Ausklang — Situationsvokabular (Fallback: fällige/Standard-Wörter).
    used_vocab = {i["vocab_id"] for i in items if i["kind"] == "vocab"}
    cool = db.situation_vocab(user_id, limit=SESSION_ARC["cooldown"] // ITEM_COST["vocab"])
    if not cool:
        cool = db.due_vocab_items(user_id, limit=SESSION_ARC["cooldown"] // ITEM_COST["vocab"])
    budget = SESSION_ARC["cooldown"]
    for v in cool:
        if budget < ITEM_COST["vocab"]:
            break
        if v["id"] in used_vocab:
            continue
        items.append(_session_vocab_item(v))
        used_vocab.add(v["id"])
        budget -= ITEM_COST["vocab"]

    return items, core_label


def _today_utc() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).date().isoformat()


def _session_payload(row: dict) -> dict:
    return {"id": row["id"], "session_date": row["session_date"], "status": row["status"],
            "headline": row["headline"], "budget_seconds": row["budget_seconds"],
            "cursor": row["cursor"], "progress": row["progress"], "items": row["plan"]}


def _generate_and_store_session(db, user_id: str, level: str | None, today: str,
                                exclude_slug: str | None = None) -> dict:
    items, core_label = _build_session_plan(db, user_id, level, exclude_slug)
    return db.create_daily_session(user_id, today, items, core_label, SESSION_BUDGET)


@app.get("/session/today")
def session_today(user: dict = Depends(current_user)) -> dict:
    """Freeze-Logik: gibt es eine offene Session (auch von gestern — Mitternacht ersetzt sie
    nicht) oder eine heute abgeschlossene, wird die zurückgegeben; sonst wird EINMAL generiert,
    eingefroren und zurückgegeben. Das Frontend lädt das getrennt, blockiert nie den Rest."""
    db = get_db()
    user_id = user["user_id"]
    today = _today_utc()
    row = db.get_current_session(user_id, today)
    if row is None:
        try:
            row = _generate_and_store_session(db, user_id, user.get("level_estimate"), today)
        except Exception:
            # Race: paralleles erstes Öffnen hat die Session schon eingefroren (unique-Constraint).
            row = db.get_current_session(user_id, today)
            if row is None:
                raise
    return _session_payload(row)


class SessionProgressIn(BaseModel):
    cursor: int
    progress: list[dict] = []


@app.post("/session/{session_id}/progress")
def session_progress(session_id: str, body: SessionProgressIn,
                     user: dict = Depends(current_user)) -> dict:
    """Fortschritt sichern (Abbruch → Fortsetzen). Bewegt KEINEN Lernstand — das machen die
    bestehenden Grade-Pfade; hier wird nur der Cursor gemerkt."""
    db = get_db()
    row = db.get_session(user["user_id"], session_id)
    if row is None:
        raise HTTPException(404, "Sesión no encontrada.")
    db.save_session_progress(session_id, body.cursor, body.progress)
    return {"ok": True}


@app.post("/session/{session_id}/complete")
def session_complete(session_id: str, user: dict = Depends(current_user)) -> dict:
    db = get_db()
    row = db.get_session(user["user_id"], session_id)
    if row is None:
        raise HTTPException(404, "Sesión no encontrada.")
    db.complete_session(session_id)
    return {"ok": True}


@app.post("/session/reroll")
def session_reroll(user: dict = Depends(current_user)) -> dict:
    """'Cambiar sesión' / neues Training: die aktuelle wegräumen und neu würfeln. Das gerade
    ersetzte Kern-Konzept wird ausgeschlossen, damit nicht direkt dasselbe kommt."""
    db = get_db()
    user_id = user["user_id"]
    today = _today_utc()
    last_core = db.last_session_core_slug(user_id)   # vor dem Wegräumen merken
    db.clear_current_session(user_id, today)
    row = _generate_and_store_session(db, user_id, user.get("level_estimate"), today,
                                      exclude_slug=last_core)
    return _session_payload(row)


class MoreExercisesIn(BaseModel):
    slug: str
    n: int = 3
    replace_index: int | None = None   # gesetzt = EINE Übung an dieser Stelle ersetzen ('otra')


@app.post("/session/{session_id}/exercises")
def session_more_exercises(session_id: str, body: MoreExercisesIn,
                           user: dict = Depends(current_user)) -> dict:
    """Mehr/neue Grammatik-Übungen in eine laufende Session ziehen. Serviert zuerst vorhandene,
    noch nicht benutzte Übungen des Kern-Konzepts; ist der Pool erschöpft, wird per KI eine
    frische Charge generiert (gleicher Seam wie das Kapitel). replace_index ersetzt EINE Übung
    ('otra' — gefällt nicht), sonst werden welche angehängt ('más ejercicios'). Der Plan wird
    aktualisiert, damit Fortsetzen konsistent bleibt."""
    db = get_db()
    row = db.get_session(user["user_id"], session_id)
    if row is None:
        raise HTTPException(404, "Sesión no encontrada.")
    detail = db.get_concept_detail(user["user_id"], body.slug)
    if detail is None:
        raise HTTPException(404, f"Concepto '{body.slug}' no existe.")

    plan = row["plan"]
    user_id = user["user_id"]
    used = {i["exercise_id"] for i in plan if i.get("kind") == "exercise"}
    pool = db.exercises_for_concept(detail["id"])
    attempts = db.exercise_attempts(user_id, [e["id"] for e in pool]) if pool else {}
    # frisch = weder in dieser Session noch je zuvor geübt → 'otra'/'más' wiederholt nichts.
    def _fresh(items):
        return [e for e in items if e["id"] not in used and e["id"] not in attempts]
    fresh = _fresh(pool)
    n = max(1, min(body.n, 5))
    if len(fresh) < n:
        try:
            batch = generate_exercises(body.slug, detail["label"], detail.get("cefr"), detail,
                                       existing_prompts=[e["prompt"] for e in pool])
            db.insert_exercises(detail["id"], batch, detail.get("cefr"))
            pool = db.exercises_for_concept(detail["id"])
            fresh = _fresh(pool)   # neue Übungen haben keine Attempts → gelten als frisch
        except Exception:
            logger.exception("session: Nachgenerieren fehlgeschlagen (%s)", body.slug)

    new_items = [_session_exercise_item(e, body.slug, detail["label"]) for e in fresh[:n]]
    if not new_items:
        return {"items": [], "replaced": False}

    if body.replace_index is not None and 0 <= body.replace_index < len(plan):
        plan[body.replace_index] = new_items[0]
        added, replaced = [new_items[0]], True
    else:
        plan = plan + new_items
        added, replaced = new_items, False
    db.save_session_plan(session_id, plan)
    return {"items": added, "replaced": replaced}


GRAMMAR_CLUSTER = PACK.GRAMMAR_CLUSTER


def _concept_category(row: dict) -> str:
    if row["ctype"] == "tense":
        return PACK.CLUSTER_TENSE_LABEL
    if row["ctype"] == "pattern_family":
        return PACK.CLUSTER_PATTERN_LABEL
    return GRAMMAR_CLUSTER.get(row["slug"], PACK.CLUSTER_OTHER_LABEL)


@app.get("/concepts")
def concepts_list(user: dict = Depends(current_user)) -> list[dict]:
    """Chapter list, priority-sorted: hot ones on top, mastered ones sink into quiet
    reference. Priority is deterministic (need + unexpired boost) — computed here, never LLM."""
    db = get_db()
    user_id = user["user_id"]
    rows = db.list_concepts_with_state(user_id)
    for r in rows:
        r["priority"] = compute_priority(r)
        r["category"] = _concept_category(r)
        r.pop("relevance_boost", None)
        r.pop("boost_expires_at", None)
        r.pop("id", None)
    active_rank = {"aprendiendo": 0, "flojo": 1, "visto": 2, "dominado": 3, "sin_ver": 4}
    rows.sort(key=lambda r: (-r["priority"], active_rank.get(r["state"], 9),
                             r["cefr"] or "Z", r["label"]))
    return rows


def _concept_detail_payload(db, user_id: str, slug: str) -> dict:
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


@app.get("/concepts/{slug}")
def concept_detail(slug: str, user: dict = Depends(current_user)) -> dict:
    """One chapter: shared body (frozen reference) + personal mantle (your errors, your state).
    The body is the same for everyone; the mantle is what makes it yours."""
    return _concept_detail_payload(get_db(), user["user_id"], slug)


# ---------------------------------------------------------------------------
# Practicar — zwei Drills, EINE Quelle: 'vocabulario' (SRS-Recall, Wörter UND Frasen)
# und 'gramatica' (eigene Fehlersätze + interaktive Übungen der wackligen Konzepte;
# Bewertung über /exercises/{id}/answer bewegt den Lernstand). Der 20-Minuten-Mix
# ist die Tages-Session (/session/today). Auswahl bleibt deterministisch.
# ---------------------------------------------------------------------------


def _vocab_cards(db, user_id: str, limit: int, phrases: bool | None) -> list[dict]:
    return [{"type": "vocab", "vocab_id": v["id"], "prompt": v["translation"],
             "answer": v["term"], "register": v["register"],
             "is_phrase": "frase" in (v.get("tags") or [])}
            for v in db.due_vocab_items(user_id, limit=limit, phrases=phrases)]


def _fix_cards(db, user_id: str, shaky: list[dict], limit: int = 5) -> list[dict]:
    items, seen = [], set()
    for corr in db.corrections_for_concepts(user_id, [s["concept_id"] for s in shaky]):
        key = (corr["wrong"], corr["correct"])
        if key in seen or len(items) >= limit:
            continue
        seen.add(key)
        items.append({"type": "fix", "prompt": corr["wrong"], "answer": corr["correct"],
                      "concept_slug": corr["concepts"]["slug"],
                      "concept_label": corr["concepts"]["label"]})
    return items


def _grammar_drill(db, user_id: str, limit: int = 10) -> list[dict]:
    """Grammatik-Drill: EIGENE Fehlersätze zuerst, dann interaktive Übungen der wackligen
    Konzepte (ungesehene zuerst, dann zuletzt-falsche). Rein deterministisch — im Drill
    wird NIE generiert; Übungs-Nachschub entsteht in der Tages-Session."""
    shaky = db.shaky_concepts(user_id)
    items: list[dict] = _fix_cards(db, user_id, shaky, limit=4)
    budget = limit - len(items)
    for s in shaky:
        if budget <= 0:
            break
        pool = db.exercises_for_concept(s["concept_id"])
        if not pool:
            continue
        attempts = db.exercise_attempts(user_id, [e["id"] for e in pool])

        def bucket(e: dict):
            a = attempts.get(e["id"])
            if a is None:
                return (0, 0)
            return (1, a["count"]) if a.get("last_correct") is False else (2, a["count"])
        pool.sort(key=bucket)
        for e in pool[:3]:
            if budget <= 0:
                break
            items.append({"type": "exercise", "exercise_id": e["id"], "etype": e["etype"],
                          "prompt": e["prompt"], "options": e["options"],
                          "concept_slug": s["slug"], "concept_label": s["label"]})
            budget -= 1
    return items


@app.get("/practicar/session")
def practicar_session(tipo: str = "vocabulario", user: dict = Depends(current_user)) -> dict:
    """'vocabulario' = SRS-Recall (Wörter und Frasen zusammen); 'gramatica' = Fehlersätze +
    interaktive Übungen. Alte Client-Namen (mix/palabras/frases) fallen auf vocabulario."""
    db = get_db()
    user_id = user["user_id"]

    if tipo in ("vocabulario", "palabras", "frases", "mix"):
        # Grundwortschatz: bis zu 10 neue Wörter/Tag rücken nach (no-op ohne seed_vocab
        # bzw. bevor der Nutzer selbst etwas captured hat)
        db.promote_daily_seed(user_id)
        return {"tipo": "vocabulario", "items": _vocab_cards(db, user_id, 15, phrases=None)}
    if tipo == "gramatica":
        return {"tipo": "gramatica", "items": _grammar_drill(db, user_id)}
    raise HTTPException(422, "Tipo de sesión desconocido.")


class GradeIn(BaseModel):
    vocab_id: str
    correct: bool


@app.post("/practicar/grade")
def practicar_grade(body: GradeIn, user: dict = Depends(current_user)) -> dict:
    """SRS moves only here, deterministically (SM-2-lite in analyze.py)."""
    db = get_db()
    user_id = user["user_id"]
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
def vocabulario(user: dict = Depends(current_user)) -> dict:
    db = get_db()
    user_id = user["user_id"]
    due_count, _ = db.due_vocab(user_id)
    return {"situations": db.list_situations(user_id), "sueltas": db.loose_vocab(user_id),
            "due": due_count, "diccionari": db.seed_topics(user_id)}


# ---------------------------------------------------------------------------
# Import — der fünfte Eingang, aber der SIMPELSTE: CSV/TSV-Vokabeln, rein deterministisch
# (kein LLM). Zwei Schritte: /preview zeigt, was erkannt wurde (Trennzeichen, Spalten, neu/
# schon-vorhanden) und schreibt NICHTS; /commit übernimmt nach Bestätigung. Importierte
# Items starten KALT (db.bulk_import_vocab) und tragen source='import' für die Gewichtung.
# ---------------------------------------------------------------------------
class ImportPreviewIn(BaseModel):
    text: str
    delimiter: str | None = None
    term_col: int = 0
    translation_col: int = 1
    has_header: bool | None = None


class ImportCommitIn(BaseModel):
    text: str
    delimiter: str | None = None
    term_col: int = 0
    translation_col: int = 1
    has_header: bool = False
    situation_name: str | None = None      # optional: Regal, dem die Vokabeln zugeordnet werden


@app.post("/import/vocab/preview")
def import_vocab_preview(body: ImportPreviewIn, user: dict = Depends(current_user)) -> dict:
    if not body.text.strip():
        raise HTTPException(422, "Archivo vacío — no hay nada que importar.")
    db = get_db()
    existing = db._user_terms(user["user_id"])
    return importer.build_preview(
        body.text, delimiter=body.delimiter, term_col=body.term_col,
        translation_col=body.translation_col, has_header=body.has_header,
        existing_terms=existing)


@app.post("/import/vocab/commit")
def import_vocab_commit(body: ImportCommitIn, user: dict = Depends(current_user)) -> dict:
    if not body.text.strip():
        raise HTTPException(422, "Archivo vacío — no hay nada que importar.")
    db = get_db()
    user_id = user["user_id"]
    delimiter = body.delimiter or importer.sniff_delimiter(body.text)
    rows = importer.parse_rows(body.text, delimiter)
    data_rows = rows[1:] if body.has_header else rows
    items = importer.extract_items(data_rows, body.term_col, body.translation_col)
    if not items:
        raise HTTPException(422, "No se reconoció ninguna fila — revisa las columnas.")

    situation_id = None
    if body.situation_name and body.situation_name.strip():
        situation_id = db.get_or_create_situation(user_id, body.situation_name.strip())["id"]

    imported, skipped = db.bulk_import_vocab(user_id, items, situation_id=situation_id)
    return {"imported": imported, "skipped": skipped, "total": len(items),
            "situation_id": situation_id}


# ---------------------------------------------------------------------------
# Upload von Lernmaterial (PDF/Bild/Text) — der LLM-Weg des fünften Eingangs. RECONCILIATION,
# kein Import: /analyze schlägt einen Modus vor und zeigt, welche BESTEHENDEN Konzepte berührt
# werden (gemappt auf die vorhandenen Slugs) + welche Vokabeln neu sind — schreibt NICHTS.
# Erst /commit legt ab: Konzepte verlinken/boosten (nie kopieren), Vokabeln kalt importieren.
# ---------------------------------------------------------------------------
class UploadFileIn(BaseModel):
    media_type: str
    data: str                    # base64 (Bild oder PDF)
    filename: str | None = None


class UploadAnalyzeIn(BaseModel):
    text: str = ""
    files: list[UploadFileIn] = []


class UploadCommitIn(BaseModel):
    mode: str                    # grammar | vocab | both (vom Nutzer bestätigt)
    analysis: dict               # das Preview-Ergebnis (concepts + lemmas + summary)
    filename: str | None = None
    kind: str = "text"           # pdf | image | text


def _doc_kind(files: list[UploadFileIn], text: str) -> str:
    mts = [(f.media_type or "").lower() for f in files]
    if any(m == "application/pdf" for m in mts):
        return "pdf"
    if any(m.startswith("image/") for m in mts):
        return "image"
    return "text"


@app.post("/upload/analyze")
def upload_analyze(body: UploadAnalyzeIn, user: dict = Depends(current_user)) -> dict:
    """Vorschau: analysiert das Material und markiert, was neu ist. Schreibt nichts."""
    if not body.text.strip() and not body.files:
        raise HTTPException(422, "Nada que analizar — sube un archivo o pega texto.")
    db = get_db()
    user_id = user["user_id"]
    known = db.list_concept_slugs()
    try:
        analysis = analyze_document(
            text=body.text, files=[f.model_dump() for f in body.files],
            variety=user.get("production_variety"), known_slugs=known)
    except Exception:
        logger.exception("upload_analyze fehlgeschlagen (user %s)", user_id)
        raise HTTPException(502, "No se pudo analizar el material — inténtalo otra vez.")

    # Anreicherung für die Vorschau (deterministisch): was ist schon im Rückgrat / im Vokabular?
    backbone = set(known)
    for c in analysis.get("concepts", []):
        c["in_backbone"] = c["slug"] in backbone
    mine = {t.lower() for t in db._user_terms(user_id)}
    new_vocab = 0
    for lemma in analysis.get("lemmas", []):
        is_new = lemma["term"].lower() not in mine
        lemma["new"] = is_new
        new_vocab += 1 if is_new else 0

    return {
        "suggested_mode": analysis.get("suggested_mode", "both"),
        "summary": analysis.get("summary"),
        "kind": _doc_kind(body.files, body.text),
        "concepts": analysis.get("concepts", []),
        "lemmas": analysis.get("lemmas", []),
        "linked_count": sum(1 for c in analysis.get("concepts", []) if c["in_backbone"]),
        "new_concept_count": sum(1 for c in analysis.get("concepts", []) if not c["in_backbone"]),
        "new_vocab_count": new_vocab,
        "analysis": analysis,           # unverändert an /commit zurückreichen
    }


@app.post("/upload/commit")
def upload_commit(body: UploadCommitIn, user: dict = Depends(current_user)) -> dict:
    """Übernehmen nach Bestätigung: Konzepte verlinken + Kurs-Boost, Vokabeln kalt importieren."""
    if body.mode not in ("grammar", "vocab", "both"):
        raise HTTPException(422, "Modo inválido.")
    if not isinstance(body.analysis, dict):
        raise HTTPException(422, "Análisis inválido.")
    db = get_db()
    result = apply_document(db, user["user_id"], body.analysis, body.mode,
                            filename=body.filename, kind=body.kind)
    return result


@app.get("/documents")
def documents_list(user: dict = Depends(current_user)) -> list[dict]:
    """Hochgeladene Dokumente (Herkunft von Boosts/Importen) — nachvollziehbar."""
    db = get_db()
    return db.list_documents(user["user_id"])


@app.get("/diccionari/{topic}")
def diccionari_topic(topic: str, user: dict = Depends(current_user)) -> dict:
    db = get_db()
    words = db.seed_words_for_topic(user["user_id"], topic)
    if not words:
        raise HTTPException(404, "Tema no existeix.")
    return {"topic": topic, "words": words}


@app.post("/diccionari/{seed_id}/add")
def diccionari_add(seed_id: str, user: dict = Depends(current_user)) -> dict:
    db = get_db()
    try:
        created = db.add_seed_word(user["user_id"], seed_id)
    except KeyError:
        raise HTTPException(404, "Paraula no existeix.")
    return {"added": created}


@app.get("/situations/{situation_id}")
def situation_detail(situation_id: str, user: dict = Depends(current_user)) -> dict:
    db = get_db()
    user_id = user["user_id"]
    detail = db.get_situation_detail(user_id, situation_id)
    if detail is None:
        raise HTTPException(404, "Situación no existe.")
    words = [i for i in detail["items"] if "frase" not in (i.get("tags") or [])]
    phrases = [{"intent": next((t for t in i["tags"] if t != "frase"), ""),
                "es": i["term"], "de": i["translation"]}
               for i in detail["items"] if "frase" in (i.get("tags") or [])]
    return {"id": detail["id"], "name": detail["name"], "is_seed": detail["is_seed"],
            "words": words, "phrases": phrases, "concepts": detail["concepts"]}


@app.post("/concepts/{slug}/merge")
def concept_merge(slug: str, into: str, user: dict = Depends(admin_user)) -> dict:
    """Consolidate a duplicate draft into its canonical chapter — deterministic, no LLM.
    Touches shared structure, so admin-only."""
    db = get_db()
    try:
        return db.merge_concept(slug, into)
    except KeyError as e:
        raise HTTPException(404, str(e))


@app.post("/concepts/{slug}/generate")
def concept_generate(slug: str, user: dict = Depends(current_user)) -> dict:
    """Fill an empty draft chapter (born from a capture) with reference content on demand.
    Stays reviewed=false — freezing remains a human act."""
    db = get_db()
    user_id = user["user_id"]
    detail = db.get_concept_detail(user_id, slug)
    if detail is None:
        raise HTTPException(404, f"Concepto '{slug}' no existe.")
    if detail.get("explanation"):
        raise HTTPException(409, "Este capítulo ya tiene contenido.")
    body = generate_chapter_body(slug, detail["label"], detail.get("cefr"))
    db.update_concept_body(slug, body)
    return _concept_detail_payload(db, user_id, slug)


# ---------------------------------------------------------------------------
# Interaktive Übungen — Generierung ist der LLM-Seam, Auswahl + Bewertung sind Code.
# ---------------------------------------------------------------------------

@app.get("/concepts/{slug}/exercises")
def concept_exercises(slug: str, limit: int = 8,
                      user: dict = Depends(current_user)) -> dict:
    """Übungs-Session fürs Kapitel: ungesehene zuerst, dann zuletzt-falsche, dann Rest.
    Lösungen bleiben serverseitig — der Client bekommt nur Aufgabe + Optionen."""
    db = get_db()
    user_id = user["user_id"]
    detail = db.get_concept_detail(user_id, slug)
    if detail is None:
        raise HTTPException(404, f"Concepto '{slug}' no existe.")
    pool = db.exercises_for_concept(detail["id"])
    attempts = db.exercise_attempts(user_id, [e["id"] for e in pool])

    def bucket(e: dict) -> int:
        a = attempts.get(e["id"])
        if a is None:
            return 0                      # nie gesehen
        if a["last_correct"] is False:
            return 1                      # zuletzt falsch — nochmal
        return 2                          # zuletzt richtig — hinten anstellen
    ordered = sorted(pool, key=lambda e: (bucket(e), attempts.get(e["id"], {}).get("count", 0)))
    session = ordered[:min(limit, 20)]
    random.shuffle(session)               # innerhalb der Session keine vorhersagbare Reihenfolge
    return {
        "slug": slug,
        "label": detail["label"],
        "total": len(pool),
        "exercises": [{"id": e["id"], "etype": e["etype"], "prompt": e["prompt"],
                       "options": e["options"]} for e in session],
    }


@app.post("/concepts/{slug}/exercises/generate")
def concept_exercises_generate(slug: str, user: dict = Depends(current_user)) -> dict:
    """Neue Übungs-Charge fürs Kapitel (LLM). Bestehende Prompts gehen als Sperrliste mit."""
    db = get_db()
    user_id = user["user_id"]
    detail = db.get_concept_detail(user_id, slug)
    if detail is None:
        raise HTTPException(404, f"Concepto '{slug}' no existe.")
    existing = db.exercises_for_concept(detail["id"])
    batch = generate_exercises(slug, detail["label"], detail.get("cefr"), detail,
                               existing_prompts=[e["prompt"] for e in existing])
    added = db.insert_exercises(detail["id"], batch, detail.get("cefr"))
    return {"added": added, "total": len(existing) + added}


# ---------------------------------------------------------------------------
# Escucha — Hörverstehen: Text aus deinen Vokabeln, vorgelesen (TTS), MC-Fragen.
# Generierung + Sprachausgabe sind LLM/Fremd-Seams; Bewertung ist Code.
# ---------------------------------------------------------------------------

@app.get("/escucha/session")
def escucha_session(user: dict = Depends(current_user)) -> dict:
    """Hörtext: Zielwörter aus dem eigenen Vokabular → Text + MC-Fragen (LLM) → Audio (TTS).
    Ein unbeantworteter Hörtext mit gespeichertem Audio wird WIEDERVERWENDET (Reload,
    Vertippen, Zurück kosten sonst je einen Text- und einen TTS-Call); erst nach dem
    Korrigieren wird neu generiert. Antworten bleiben serverseitig."""
    db = get_db()
    user_id = user["user_id"]

    reuse = db.get_reusable_listening_item(user_id)
    if reuse:
        return {
            "item_id": reuse["id"],
            "audio_b64": reuse["audio_b64"],
            "audio_media_type": reuse.get("audio_media_type") or "audio/mpeg",
            "targets": [],
            "questions": [{"index": i, "q": q["q"], "options": q["options"]}
                          for i, q in enumerate(reuse["questions"])],
        }

    terms = db.listening_target_terms(user_id, 6)
    if not terms:
        raise HTTPException(404, "Aún no tienes vocabulario para generar un audio.")
    item = generate_listening(terms)
    if not item["questions"]:
        raise HTTPException(502, "No se pudo generar el ejercicio — inténtalo otra vez.")
    try:
        audio = synthesize(item["passage"])
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception:
        logger.exception("TTS failed (user %s)", user_id)
        raise HTTPException(502, "No se pudo generar el audio — inténtalo otra vez.")
    import base64
    audio_b64 = base64.b64encode(audio).decode()
    item_id = db.create_listening_item(user_id, item["passage"], item["gist_de"],
                                       item["questions"], audio_b64=audio_b64,
                                       audio_media_type="audio/mpeg")
    return {
        "item_id": item_id,
        "audio_b64": audio_b64,
        "audio_media_type": "audio/mpeg",
        "targets": terms,
        "questions": [{"index": i, "q": q["q"], "options": q["options"]}
                      for i, q in enumerate(item["questions"])],
    }


class EscuchaGradeIn(BaseModel):
    answers: list[str]   # gewählte Option pro Frage-Index


@app.post("/escucha/{item_id}/grade")
def escucha_grade(item_id: str, body: EscuchaGradeIn,
                  user: dict = Depends(current_user)) -> dict:
    """Deterministisch bewerten (Option-Match) und Transkript + Kontext freigeben."""
    db = get_db()
    item = db.get_listening_item(item_id, user["user_id"])
    if item is None:
        raise HTTPException(404, "Ejercicio no existe.")
    qs = item["questions"]
    results, score = [], 0
    for i, q in enumerate(qs):
        given = body.answers[i] if i < len(body.answers) else None
        ok = given is not None and given.strip() == q["answer"].strip()
        score += ok
        results.append({"index": i, "correct": ok, "answer": q["answer"]})
    db.mark_listening_answered(item_id)   # ab jetzt wird ein frischer Hörtext generiert
    return {"score": score, "total": len(qs), "results": results,
            "transcript": item["passage"], "gist": item["gist"]}


class ChatIn(BaseModel):
    question: str
    history: list[dict] = []


@app.post("/concepts/{slug}/chat")
def concept_chat(slug: str, body: ChatIn, user: dict = Depends(current_user)) -> dict:
    """Klärungsfrage zum Kapitel. Stateless: die History kommt vom Client und lebt nur
    dort — Chat erklärt, er bewegt NIE Counter oder States."""
    db = get_db()
    detail = db.get_concept_detail(user["user_id"], slug)
    if detail is None:
        raise HTTPException(404, f"Concepto '{slug}' no existe.")
    question = body.question.strip()
    if not question:
        raise HTTPException(422, "Pregunta vacía.")
    answer = answer_concept_question(detail, question[:2000], body.history)
    return {"answer": answer}


class AnswerIn(BaseModel):
    answer: str


@app.post("/exercises/{exercise_id}/answer")
def exercise_answer(exercise_id: str, body: AnswerIn,
                    user: dict = Depends(current_user)) -> dict:
    """Deterministisch bewerten, Versuch loggen, Konzept-State bewegen — kein LLM."""
    db = get_db()
    user_id = user["user_id"]
    ex = db.get_exercise(exercise_id)
    if ex is None:
        raise HTTPException(404, "Ejercicio no existe.")
    correct = grade_exercise(ex, body.answer)
    db.log_exercise_attempt(user_id, exercise_id, correct)
    state = apply_exercise_result(db, user_id, ex["concepts"]["id"], correct)
    return {
        "correct": correct,
        "solution": ex["answers"][0],
        "explanation": ex["explanation"],
        "state": state,
    }


@app.get("/captures")
def captures(limit: int = 20, user: dict = Depends(current_user)) -> list[dict]:
    """History for the Capturar screen: what you threw in, newest first."""
    db = get_db()
    user_id = user["user_id"]
    rows = db.list_captures(user_id, limit=min(limit, 50))
    return [{
        "id": r["id"],
        "text": r["raw_text"],
        "mode": r["kind"],
        "created_at": r["created_at"],
        "correction": (r["corrections"][0] if r.get("corrections") else None),
    } for r in rows]


@app.get("/captures/{capture_id}")
def capture_detail(capture_id: str, user: dict = Depends(current_user)) -> dict:
    """Detailansicht eines Historien-Eintrags: die volle Analyse (Korrektur, Erklärung,
    getaggte Konzepte, erkannte Vokabeln). Neu-Einträge aus dem gespeicherten analysis-Blob,
    Alt-Einträge rekonstruiert aus den verknüpften Tabellen."""
    detail = get_db().get_capture_detail(user["user_id"], capture_id)
    if detail is None:
        raise HTTPException(404, "Captura no encontrada.")
    return detail


# ---------------------------------------------------------------------------
# Hablar — Speaking-Bot-Sessions (Produktion). Der Telegram-Bot schreibt die
# Daten; hier nur Lesen fürs Frontend. ES-only-Feature (Tab ist im Frontend
# per LANG gegated; auf der ca-Instanz existieren die Tabellen nicht).
# ---------------------------------------------------------------------------

@app.get("/hablar")
def hablar_overview(user: dict = Depends(current_user)) -> dict:
    """Fehler-Top-3 (14 Tage), offene Chunks, Sessions-Liste (neueste zuerst)."""
    db = get_db()
    user_id = user["user_id"]
    sessions = db.list_speaking_sessions(user_id)
    session_ids = [s["id"] for s in sessions]
    errors = db.list_speaking_errors(user_id, session_ids)
    chunks = db.list_speaking_chunks(user_id)
    error_by_session: dict[str, int] = {}
    for e in errors:
        error_by_session[e["session_id"]] = error_by_session.get(e["session_id"], 0) + 1
    chunk_by_session: dict[str, int] = {}
    for c in chunks:
        if c["session_id"]:
            chunk_by_session[c["session_id"]] = chunk_by_session.get(c["session_id"], 0) + 1
    counts = db.speaking_error_counts(user_id)
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:3]
    return {
        "top_errors": [{"error_type": t, "count": n} for t, n in top],
        "open_chunks": db.count_open_speaking_chunks(user_id),
        "sessions": [{
            "id": s["id"],
            "created_at": s["created_at"],
            "duration_sec": s["duration_sec"],
            "snippet": (s["transcript"] or "")[:90],
            "error_count": error_by_session.get(s["id"], 0),
            "chunk_count": chunk_by_session.get(s["id"], 0),
        } for s in sessions],
    }


@app.get("/hablar/{session_id}")
def hablar_detail(session_id: str, user: dict = Depends(current_user)) -> dict:
    """Detailansicht: Audio (signierte URL), Transkript + Korrektur, Fehler mit
    Wiederkehr-Zähler (14 Tage), Chunks der Session."""
    db = get_db()
    user_id = user["user_id"]
    session = db.get_speaking_session(user_id, session_id)
    if session is None:
        raise HTTPException(404, "Sesión no encontrada.")
    errors = db.list_speaking_errors(user_id, [session_id])
    counts = db.speaking_error_counts(user_id)
    for e in errors:
        e["recurrence"] = counts.get(e["error_type"], 0)
        e.pop("session_id", None)
    audio_url = (db.speaking_audio_url(session["audio_url"])
                 if session.get("audio_url") else None)
    return {
        "session": {
            "id": session["id"],
            "created_at": session["created_at"],
            "duration_sec": session["duration_sec"],
            "transcript": session["transcript"],
            "transcript_corrected": session["transcript_corrected"],
            "low_conf_spans": session["low_conf_spans"],
        },
        "audio_url": audio_url,
        "errors": errors,
        "chunks": [
            {k: c[k] for k in ("chunk_es", "example_es", "trigger_de", "status", "activated_at")}
            for c in db.list_speaking_chunks(user_id, session_id)
        ],
    }
