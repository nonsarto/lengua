"""
Tests fürs Einstufungs-Banding (onboarding._estimate_level) und die Session-Konstanten
(der Bogen muss das Zeitbudget wirklich aufteilen). Reine Logik, kein LLM/DB.
"""

from onboarding import _estimate_level


def _scores(a1, a2, b1, b2):
    return {"A1": a1, "A2": a2, "B1": b1, "B2": b2}


def test_level_all_passed_is_b2():
    assert _estimate_level(_scores((4, 4), (3, 4), (3, 4), (3, 4))) == "B2"


def test_level_stops_at_first_weak_band():
    # A2 unter 75 % -> das Niveau ist A2, auch wenn Höheres zufällig gut lief.
    assert _estimate_level(_scores((4, 4), (2, 4), (4, 4), (4, 4))) == "A2"


def test_level_b1_weak_is_b1():
    assert _estimate_level(_scores((4, 4), (4, 4), (2, 4), (4, 4))) == "B1"


def test_level_empty_b2_defaults_to_b1():
    assert _estimate_level(_scores((4, 4), (4, 4), (4, 4), (0, 0))) == "B1"


def test_level_all_skipped_defaults_to_b1():
    assert _estimate_level(_scores((0, 0), (0, 0), (0, 0), (0, 0))) == "B1"


def test_level_exactly_75_percent_holds():
    # 3/4 = 0.75 gilt als gehalten (>= 0.75), nicht als Schwäche.
    assert _estimate_level(_scores((3, 4), (3, 4), (3, 4), (3, 4))) == "B2"


def test_session_arc_sums_to_budget():
    import main
    assert sum(main.SESSION_ARC.values()) == main.SESSION_BUDGET
    # Kern (Grammatik) ist der größte Block — der Fokus liegt auf Grammatik.
    assert main.SESSION_ARC["core"] > main.SESSION_ARC["warmup"]
    assert main.SESSION_ARC["core"] > main.SESSION_ARC["cooldown"]
