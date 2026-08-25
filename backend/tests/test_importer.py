"""
Unit-Tests für den Vokabel-Import (importer.py) — reines, deterministisches Parsen.
Kein LLM, kein DB. Trennzeichen-Erkennung, Anki-Metazeilen, Header-Heuristik, Dedupe.
"""

from importer import (build_preview, extract_items, looks_like_header, parse_rows,
                      sniff_delimiter)


# ------------------------------------------------------------- Trennzeichen
def test_sniff_prefers_tab():
    assert sniff_delimiter("hola\thallo\nadiós\ttschüss") == "\t"


def test_sniff_detects_comma():
    assert sniff_delimiter("hola,hallo\nadiós,tschüss") == ","


def test_sniff_detects_semicolon():
    assert sniff_delimiter("hola;hallo\nadiós;tschüss") == ";"


def test_sniff_empty_falls_back_to_tab():
    assert sniff_delimiter("") == "\t"


def test_sniff_ignores_anki_meta_lines():
    text = "#separator:tab\n#html:false\nhola\thallo"
    assert sniff_delimiter(text) == "\t"


# ------------------------------------------------------------- Zeilen parsen
def test_parse_skips_meta_and_blank_lines():
    text = "#separator:tab\nhola\thallo\n\nadiós\ttschüss\n"
    rows = parse_rows(text, "\t")
    assert rows == [["hola", "hallo"], ["adiós", "tschüss"]]


def test_parse_respects_quotes():
    text = 'term,translation\n"hola, amigo",hallo Freund'
    rows = parse_rows(text, ",")
    assert rows[1] == ["hola, amigo", "hallo Freund"]


# ------------------------------------------------------------- Header-Heuristik
def test_header_detected():
    assert looks_like_header(["Front", "Back"]) is True
    assert looks_like_header(["term", "translation"]) is True


def test_data_row_is_not_header():
    assert looks_like_header(["hola", "hallo"]) is False


# ------------------------------------------------------------- extract + dedupe
def test_extract_dedupes_within_file_case_insensitive():
    rows = [["hola", "hallo"], ["Hola", "hallo again"], ["adiós", "tschüss"]]
    items = extract_items(rows, 0, 1)
    assert [i["term"] for i in items] == ["hola", "adiós"]   # zweites 'Hola' fällt raus


def test_extract_skips_rows_missing_columns():
    rows = [["hola", "hallo"], ["solo"], ["", "leer"], ["adiós", "tschüss"]]
    items = extract_items(rows, 0, 1)
    assert [i["term"] for i in items] == ["hola", "adiós"]


def test_extract_uses_chosen_columns():
    rows = [["1", "hola", "hallo"], ["2", "adiós", "tschüss"]]
    items = extract_items(rows, 1, 2)
    assert items[0] == {"term": "hola", "translation": "hallo"}


# ------------------------------------------------------------- Vorschau
def test_preview_counts_new_and_dup_against_existing():
    text = "hola\thallo\nadiós\ttschüss\ngracias\tdanke"
    p = build_preview(text, existing_terms={"gracias"})
    assert p["total"] == 3
    assert p["new_count"] == 2
    assert p["dup_count"] == 1
    assert p["delimiter"] == "\t"
    assert {s["term"]: s["status"] for s in p["sample"]}["gracias"] == "dup"


def test_preview_auto_detects_header():
    text = "Front\tBack\nhola\thallo"
    p = build_preview(text)
    assert p["has_header"] is True
    assert p["total"] == 1
    assert p["sample"][0]["term"] == "hola"


def test_preview_no_header_keeps_all_rows():
    text = "hola\thallo\nadiós\ttschüss"
    p = build_preview(text)
    assert p["has_header"] is False
    assert p["total"] == 2
