"""usage.py — LLM-Verbrauch pro Aufruf in llm_usage loggen (Admin-Dashboard).

Nutzer-Attribution über eine ContextVar: current_user (main.py) setzt sie pro
Request; die Call-Sites in analyze.py müssen kein user_id durchreichen (auch
BackgroundTasks erben den Kontext des Requests). Logging ist best-effort und
darf NIE einen Request brechen — fehlt die Tabelle (Migration 016 noch nicht
gelaufen, ca-Instanz), wird nur ein Fehler geloggt.
"""

import contextvars
import logging

logger = logging.getLogger("lengua")

_user_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("llm_user_id", default=None)


def set_user(user_id: str | None) -> None:
    _user_id.set(user_id)


def _tok(usage, name: str) -> int:
    if usage is None:
        return 0
    if isinstance(usage, dict):
        return int(usage.get(name) or 0)
    return int(getattr(usage, name, 0) or 0)


def log_usage(kind: str, model: str, usage=None, audio_seconds: int = 0) -> None:
    from db import get_db

    try:
        get_db().insert_llm_usage({
            "user_id": _user_id.get(),
            "source": "web",
            "kind": kind,
            "model": model,
            "input_tokens": _tok(usage, "input_tokens"),
            "output_tokens": _tok(usage, "output_tokens"),
            "cache_read_tokens": _tok(usage, "cache_read_input_tokens"),
            "cache_write_tokens": _tok(usage, "cache_creation_input_tokens"),
            "audio_seconds": int(audio_seconds or 0),
        })
    except Exception:
        logger.exception("llm_usage-Logging fehlgeschlagen (kind=%s)", kind)
