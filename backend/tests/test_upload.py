"""
Tests für den fünften Eingang (Upload). Der LLM-Seam (analyze_document) wird NICHT getestet —
das ist die Modell-Naht. Getestet wird der deterministische Teil: apply_document (Reconciliation
+ Kurs-Boost + Kalt-Import, Einheiten isoliert) und die Quellengewichtung der Vokabel-Auswahl.
"""

import types

import pytest

from analyze import apply_document, COURSE_BOOST_AMOUNT, COURSE_BOOST_DAYS
from db import Database


# --------------------------------------------------- apply_document (deterministisch)
class _DocDB:
    """Minimaler Stub: zeichnet auf, was geschrieben würde. Optional scheitert EIN Konzept."""
    def __init__(self, fail_slug=None):
        self.fail_slug = fail_slug
        self.docs, self.boosts, self.imports, self.updates = [], [], [], {}

    def create_document(self, user_id, filename, kind, mode):
        row = {"id": "doc-1", "user_id": user_id, "filename": filename,
               "kind": kind, "mode": mode}
        self.docs.append(row)
        return row

    def get_or_create_concept(self, slug, label, cefr):
        if slug == self.fail_slug:
            raise RuntimeError("boom")
        return {"id": f"cid-{slug}", "slug": slug}

    def boost_concept(self, user_id, concept_id, amount, days):
        self.boosts.append((concept_id, amount, days))

    def bulk_import_vocab(self, user_id, lemmas, source_document_id=None):
        self.imports.append((source_document_id, [l["term"] for l in lemmas]))
        return (len(lemmas), 0)

    def update_document(self, document_id, fields):
        self.updates[document_id] = fields


def _analysis():
    return {
        "suggested_mode": "both",
        "summary": "Über hace / desde hace.",
        "concepts": [
            {"slug": "pret-perfecto", "label": "Pretérito perfecto", "cefr": "A2", "why": "x"},
            {"slug": "hace-desde", "label": "hace / desde hace", "cefr": "B1", "why": "y"},
        ],
        "lemmas": [
            {"term": "el plazo", "translation": "die Frist", "register": "neutral", "region": None},
        ],
    }


def test_grammar_mode_boosts_concepts_not_vocab():
    db = _DocDB()
    out = apply_document(db, "u1", _analysis(), "grammar")
    assert len(db.boosts) == 2                     # beide Konzepte geboostet
    assert db.imports == []                         # keine Vokabeln bei reiner Grammatik
    assert out["concepts_boosted"] == ["pret-perfecto", "hace-desde"]
    assert out["vocab_imported"] == 0
    assert db.updates["doc-1"] == {"concept_slugs": ["pret-perfecto", "hace-desde"],
                                   "vocab_count": 0}


def test_vocab_mode_imports_not_boosts():
    db = _DocDB()
    out = apply_document(db, "u1", _analysis(), "vocab")
    assert db.boosts == []                          # keine Konzepte bei reinem Vokabel-Modus
    assert db.imports == [("doc-1", ["el plazo"])]  # Import mit Dokument-Herkunft
    assert out["vocab_imported"] == 1
    assert db.updates["doc-1"]["concept_slugs"] == []


def test_both_mode_does_both():
    db = _DocDB()
    out = apply_document(db, "u1", _analysis(), "both")
    assert len(db.boosts) == 2
    assert db.imports == [("doc-1", ["el plazo"])]
    assert out["vocab_imported"] == 1
    assert len(out["concepts_boosted"]) == 2


def test_course_boost_uses_the_named_constants():
    db = _DocDB()
    apply_document(db, "u1", _analysis(), "grammar")
    for _, amount, days in db.boosts:
        assert amount == COURSE_BOOST_AMOUNT
        assert days == COURSE_BOOST_DAYS


def test_failing_concept_is_isolated():
    db = _DocDB(fail_slug="pret-perfecto")
    out = apply_document(db, "u1", _analysis(), "both")
    assert out["concepts_boosted"] == ["hace-desde"]   # das gesunde Konzept überlebt
    assert db.imports == [("doc-1", ["el plazo"])]      # Vokabeln laufen trotzdem durch


def test_document_row_created_before_writes():
    db = _DocDB()
    apply_document(db, "u1", _analysis(), "both", filename="hoja.pdf", kind="pdf")
    assert db.docs[0]["filename"] == "hoja.pdf"
    assert db.docs[0]["kind"] == "pdf"
    assert db.docs[0]["mode"] == "both"


# --------------------------------------------------- Quellengewichtung (Punkt 4)
class _FakeQ:
    """Fake-Query-Builder: liefert je nach source-Filter eigene oder importierte Zeilen."""
    def __init__(self, own, imported):
        self._own, self._imported = own, imported
        self._which, self._limit = None, None

    def neq(self, col, val):          # .neq("source", "import") → die eigenen
        self._which = "own"
        return self

    def eq(self, col, val):           # .eq("source", "import") → die importierten
        self._which = "import"
        return self

    def limit(self, n):
        self._limit = n
        return self

    def execute(self):
        data = self._own if self._which == "own" else self._imported
        return types.SimpleNamespace(data=data[: self._limit])


def _rows(prefix, n):
    return [{"id": f"{prefix}{i}", "source": prefix} for i in range(n)]


def test_source_weighting_own_before_imported():
    own, imported = _rows("own-", 2), _rows("import-", 5)
    out = Database._source_weighted(lambda: _FakeQ(own, imported), limit=8)
    ids = [r["id"] for r in out]
    assert ids[:2] == ["own-0", "own-1"]             # eigene zuerst
    assert ids[2:] == ["import-0", "import-1", "import-2", "import-3", "import-4"]
    assert len(out) == 7                              # 2 eigene + 5 importierte (Rest bis 8)


def test_source_weighting_own_fills_the_budget():
    own, imported = _rows("own-", 10), _rows("import-", 100)
    out = Database._source_weighted(lambda: _FakeQ(own, imported), limit=8)
    assert len(out) == 8
    assert all(r["id"].startswith("own-") for r in out)    # ein Massenimport flutet NICHT


def test_source_weighting_imported_when_no_own():
    out = Database._source_weighted(lambda: _FakeQ([], _rows("import-", 3)), limit=8)
    assert [r["id"] for r in out] == ["import-0", "import-1", "import-2"]
