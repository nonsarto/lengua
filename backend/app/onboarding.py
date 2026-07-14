"""
onboarding.py — der Einstufungstest: 12 kuratierte Fragen, je eine pro Signatur-Konzept
einer Niveaustufe. Fest im Code (deterministisch, sofortige Auswertung, kein LLM) —
dieselbe Philosophie wie das Rückgrat: Struktur ist Code.

Die Auswertung SÄT die Konzept-States: ein Fehler markiert das Konzept flojo (need=1) und
taucht sofort in 'Lo tuyo ahora' und im Drill auf; eine richtige Antwort markiert visto.
So startet ein neuer Nutzer nicht bei null, sondern mit einer echten ersten Landkarte.
"""

from datetime import datetime, timezone

from analyze import derive_state

# (id, band, concept_slug, question, options, correct_index)
QUESTIONS: list[dict] = [
    # ---- A1 ----
    {"id": "a1-ser", "band": "A1", "concept": "ser-vs-estar",
     "q": "Yo ___ de Alemania.",
     "options": ["soy", "estoy", "tengo"], "correct": 0},
    {"id": "a1-hay", "band": "A1", "concept": "estar-vs-hay",
     "q": "___ una farmacia cerca de aquí.",
     "options": ["Está", "Hay", "Es"], "correct": 1},
    {"id": "a1-genero", "band": "A1", "concept": "genero-y-numero",
     "q": "___ problema es que no tengo tiempo.",
     "options": ["La", "El", "Los"], "correct": 1},
    {"id": "a1-presente", "band": "A1", "concept": "presente-indicativo",
     "q": "Nosotros ___ en Barcelona.",
     "options": ["vive", "vivimos", "viven"], "correct": 1},
    # ---- A2 ----
    {"id": "a2-stem", "band": "A2", "concept": "stem-change-e-ie",
     "q": "¿A qué hora ___ la película?",
     "options": ["empeza", "empieza", "empienza"], "correct": 1},
    {"id": "a2-reflexivo", "band": "A2", "concept": "verbos-reflexivos",
     "q": "Por la mañana ___ a las siete.",
     "options": ["levanto", "me levanto", "levántome"], "correct": 1},
    {"id": "a2-indefinido", "band": "A2", "concept": "indefinido",
     "q": "Anoche ___ al cine con unos amigos.",
     "options": ["fui", "iba", "he ido"], "correct": 0},
    {"id": "a2-obligacion", "band": "A2", "concept": "obligacion",
     "q": "Mañana ___ pagar el alquiler.",
     "options": ["tengo que", "debo de", "hay"], "correct": 0},
    # ---- B1 ----
    {"id": "b1-perfecto", "band": "B1", "concept": "indefinido-vs-perfecto",
     "q": "Ayer ___ a la playa.",
     "options": ["he ido", "fui", "iba"], "correct": 1},
    {"id": "b1-porpara", "band": "B1", "concept": "por-vs-para",
     "q": "Este regalo es ___ ti.",
     "options": ["por", "para", "a"], "correct": 1},
    {"id": "b1-subjuntivo", "band": "B1", "concept": "desencadenantes-subjuntivo",
     "q": "Quiero que ___ a la fiesta.",
     "options": ["vienes", "vengas", "venir"], "correct": 1},
    # ---- B2 ----
    {"id": "b2-irreal", "band": "B2", "concept": "condicional-irreal",
     "q": "Si tuviera más dinero, ___ un piso más grande.",
     "options": ["compraría", "compraré", "compraba"], "correct": 0},
]

BANDS = ["A1", "A2", "B1", "B2"]


def public_questions() -> list[dict]:
    """Questions without the answers — what the client gets."""
    return [{"id": q["id"], "band": q["band"], "q": q["q"], "options": q["options"]}
            for q in QUESTIONS]


def _estimate_level(scores: dict[str, tuple[int, int]]) -> str:
    """Deterministic banding: you hold a level if you got ≥75% of its questions."""
    for band in ("A1", "A2", "B1"):
        correct, total = scores[band]
        if total and correct / total < 0.75:
            return band
    correct, total = scores["B2"]
    return "B2" if total and correct / total >= 0.75 else "B1"


def grade(db, user_id: str, answers: dict[str, int]) -> dict:
    """Deterministic: seed states + evidence from the answers, estimate the level.
    Every counter points at evidence — the test itself is one capture."""
    capture_id = db.create_capture(user_id, "test de nivel inicial", "check",
                                   source="onboarding")
    scores = {b: [0, 0] for b in BANDS}
    weak: list[dict] = []

    for q in QUESTIONS:
        choice = answers.get(q["id"])
        if choice is None:
            continue  # skipped — no evidence, no guess-penalty
        correct = choice == q["correct"]
        scores[q["band"]][0] += int(correct)
        scores[q["band"]][1] += 1

        concept = db.get_or_create_concept(q["concept"], q["concept"], q["band"])
        db.add_evidence(user_id, concept["id"], capture_id,
                        "success" if correct else "error")
        state = db.get_or_create_state(user_id, concept["id"])
        if correct:
            state["success_count"] += 1
        else:
            state["need_count"] += 1
            weak.append({"slug": q["concept"], "label": concept["label"]})
        state["state"] = derive_state(state["need_count"], state["success_count"], "visto")
        db.save_state(state)

    level = _estimate_level({b: tuple(v) for b, v in scores.items()})
    db.update_user(user_id, {
        "level_estimate": level,
        "onboarded_at": datetime.now(timezone.utc).isoformat(),
    })
    total_correct = sum(v[0] for v in scores.values())
    total = sum(v[1] for v in scores.values())
    return {"level": level, "correct": total_correct, "total": total, "weak": weak}
