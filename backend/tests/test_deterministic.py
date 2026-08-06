"""
Unit-Tests für die deterministische Naht (analyze.py) — die Korrektheitsgarantie der App.
Kein LLM, keine DB: reine Funktionen, die Scoring/State/SRS/Grading bewegen. Genau die
Logik, auf der das ganze Design ruht (goldene Regel #2: das ist Code, nie ein Modell).
"""

from datetime import datetime, timedelta, timezone

import pytest

from analyze import (apply_analysis, compute_priority, derive_state, grade_exercise,
                     normalize_answer, srs_update, _recompute_state, NEED_THRESHOLD)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _item(ease=2.5, reps=0, interval=0):
    return {"srs_ease": ease, "srs_reps": reps, "srs_interval_days": interval}


# ---------------------------------------------------------------- SRS (SM-2-lite)
def test_srs_first_correct_is_one_day():
    p = srs_update(_item(), correct=True, now=NOW)
    assert p["srs_reps"] == 1
    assert p["srs_interval_days"] == 1
    assert p["srs_ease"] == pytest.approx(2.55)
    assert p["srs_due"] == (NOW + timedelta(days=1)).isoformat()


def test_srs_second_correct_is_three_days():
    p = srs_update(_item(ease=2.55, reps=1, interval=1), correct=True, now=NOW)
    assert p["srs_reps"] == 2
    assert p["srs_interval_days"] == 3
    assert p["srs_ease"] == pytest.approx(2.6)


def test_srs_third_correct_multiplies_by_ease():
    # reps 2 -> 3: interval = round(3 * 2.6) = 8
    p = srs_update(_item(ease=2.6, reps=2, interval=3), correct=True, now=NOW)
    assert p["srs_reps"] == 3
    assert p["srs_interval_days"] == 8
    assert p["srs_ease"] == pytest.approx(2.65)


def test_srs_ease_capped_at_2_8():
    p = srs_update(_item(ease=2.78, reps=5, interval=30), correct=True, now=NOW)
    assert p["srs_ease"] == pytest.approx(2.8)


def test_srs_wrong_resets_reps_and_interval():
    p = srs_update(_item(ease=2.5, reps=4, interval=30), correct=False, now=NOW)
    assert p["srs_reps"] == 0
    assert p["srs_interval_days"] == 0
    assert p["srs_ease"] == 2.3
    assert p["srs_due"] == NOW.isoformat()   # due now (interval 0)


def test_srs_ease_floored_at_1_3():
    p = srs_update(_item(ease=1.35), correct=False, now=NOW)
    assert p["srs_ease"] == 1.3


# ------------------------------------------------- State-Maschine (_recompute_state)
def _state(need, success, state):
    return {"need_count": need, "success_count": success, "state": state}


def test_encounter_marks_seen_from_sin_ver():
    s = _state(0, 0, "sin_ver")
    _recompute_state(s, "encounter")
    assert s["state"] == "visto"


def test_encounter_never_promotes_even_above_threshold():
    # Begegnung ist Exposition, kein Können — darf nie 'aprendiendo' auslösen.
    s = _state(NEED_THRESHOLD, 0, "flojo")
    _recompute_state(s, "encounter")
    assert s["state"] == "flojo"


def test_error_below_threshold_is_flojo():
    s = _state(1, 0, "visto")
    _recompute_state(s, "error")
    assert s["state"] == "flojo"


def test_error_at_threshold_promotes_to_aprendiendo():
    s = _state(NEED_THRESHOLD, 0, "flojo")
    _recompute_state(s, "error")
    assert s["state"] == "aprendiendo"


def test_success_demotes_to_dominado():
    # Der Abstieg ist so wichtig wie der Aufstieg (PRODUCT.md).
    s = _state(2, 3, "aprendiendo")
    _recompute_state(s, "success")
    assert s["state"] == "dominado"


def test_success_from_sin_ver_is_seen():
    s = _state(0, 1, "sin_ver")
    _recompute_state(s, "success")
    assert s["state"] == "visto"


# -------------------------------------------------------- derive_state (beim Merge)
def test_derive_state_transitions():
    assert derive_state(NEED_THRESHOLD, 0, "visto") == "aprendiendo"
    assert derive_state(2, 3, "visto") == "dominado"
    assert derive_state(1, 0, "visto") == "flojo"
    assert derive_state(0, 5, "visto") == "visto"          # fallback
    assert derive_state(NEED_THRESHOLD, NEED_THRESHOLD, "visto") == "flojo"  # gleichstand


# -------------------------------------------------- compute_priority (need + boost)
def test_priority_is_net_need():
    assert compute_priority({"need_count": 5, "success_count": 2,
                             "relevance_boost": 0, "boost_expires_at": None}, now=NOW) == 3


def test_priority_never_negative():
    assert compute_priority({"need_count": 2, "success_count": 5,
                             "relevance_boost": 0, "boost_expires_at": None}, now=NOW) == 0


def test_priority_adds_active_boost():
    st = {"need_count": 1, "success_count": 0, "relevance_boost": 5,
          "boost_expires_at": (NOW + timedelta(days=1)).isoformat()}
    assert compute_priority(st, now=NOW) == 6


def test_priority_ignores_expired_boost():
    st = {"need_count": 1, "success_count": 0, "relevance_boost": 5,
          "boost_expires_at": (NOW - timedelta(days=1)).isoformat()}
    assert compute_priority(st, now=NOW) == 1


def test_priority_accepts_datetime_expiry():
    st = {"need_count": 0, "success_count": 0, "relevance_boost": 3,
          "boost_expires_at": NOW + timedelta(days=2)}
    assert compute_priority(st, now=NOW) == 3


def test_priority_boost_without_expiry_is_ignored():
    st = {"need_count": 1, "success_count": 0, "relevance_boost": 5, "boost_expires_at": None}
    assert compute_priority(st, now=NOW) == 1


# ----------------------------------------------- Grading (Akzente signifikant!)
def test_normalize_strips_case_space_punct_keeps_accents():
    assert normalize_answer("  Está.  ") == "está"
    assert normalize_answer("¿Cómo   estás?") == "cómo estás"


def test_grade_accents_are_significant():
    ex = {"answers": ["está"]}
    assert grade_exercise(ex, "esta") is False        # fehlender Akzent = falsch
    assert grade_exercise(ex, "  ESTÁ. ") is True     # nur Case/Space/Punkt egal


def test_grade_accepts_any_listed_variant():
    ex = {"answers": ["voy a comer", "como"]}
    assert grade_exercise(ex, "  Voy   a  comer ") is True
    assert grade_exercise(ex, "cenar") is False


# --------------------------- apply_analysis: Einheiten sind isoliert (M2-Resilienz)
class _FakeDB:
    """Minimaler Stub: eine benannte Slug-Aussaat scheitert, der Rest muss durchlaufen."""
    def __init__(self, fail_slug=None):
        self.fail_slug = fail_slug
        self.vocab, self.corrections = [], []

    def get_or_create_concept(self, slug, label, cefr):
        if slug == self.fail_slug:
            raise RuntimeError("boom")
        return {"id": f"cid-{slug}", "slug": slug}

    def add_evidence(self, *a):
        pass

    def get_or_create_state(self, user_id, concept_id):
        return {"id": f"sid-{concept_id}", "need_count": 0, "success_count": 0, "state": "sin_ver"}

    def save_state(self, state):
        pass

    def add_correction(self, *a):
        self.corrections.append(a)

    def get_or_create_vocab_item(self, user_id, lemma, source_capture_id):
        self.vocab.append(lemma["term"])
        return ("vid", True)


def test_apply_analysis_isolates_failing_concept():
    db = _FakeDB(fail_slug="bad-slug")
    result = {
        "concepts": [
            {"slug": "bad-slug", "label": "", "cefr": None, "evidence": "error"},
            {"slug": "good-slug", "label": "", "cefr": None, "evidence": "success"},
        ],
        "correction": None,
        "lemmas": [{"term": "hola", "translation": "hallo", "register": "neutral", "region": None}],
        "brief": None,
    }
    written = apply_analysis(db, "u1", "cap1", result)
    slugs = [c["slug"] for c in written["concepts"]]
    assert "good-slug" in slugs        # gesundes Konzept trotz Fehler davor gesät
    assert "bad-slug" not in slugs     # kaputtes übersprungen, nicht geworfen
    assert "hola" in written["vocab"]  # Vokabel danach ebenfalls noch geschrieben
