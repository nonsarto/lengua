"""
importer.py — der Vokabel-Import ist DETERMINISTISCHE Arbeit, kein LLM-Aufruf.
CSV/TSV im Anki-Stil (zwei Spalten Begriff/Übersetzung, optional weitere). Trennzeichen
wird automatisch erkannt, die Spaltenzuordnung schlägt der Parser vor und der Nutzer
bestätigt sie. Reines Parsen + Dedupe; das Schreiben ins SRS macht db.py (kalt-Start).

Bewusst getrennt von analyze.py: dort wohnt der EINE LLM-Seam, hier nur Text-Zerlegung.
"""

import csv
import io

DELIMITERS = ["\t", ";", ",", "|"]
_ANKI_COMMENT = "#"   # Anki-Exporte beginnen Metazeilen mit '#' (z.B. "#separator:tab")


def sniff_delimiter(text: str) -> str:
    """Häufigstes der Kandidaten-Trennzeichen über die ersten echten Zeilen. Tab gewinnt
    bei Gleichstand (Anki-Default). Fällt auf Tab zurück, wenn nichts auftaucht."""
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith(_ANKI_COMMENT)]
    sample = lines[:20]
    if not sample:
        return "\t"
    # Zähle je Kandidat, wie oft er pro Zeile vorkommt (Median-artig: Summe reicht hier).
    counts = {d: sum(ln.count(d) for ln in sample) for d in DELIMITERS}
    best = max(DELIMITERS, key=lambda d: counts[d])   # DELIMITERS-Reihenfolge = Tie-Break
    return best if counts[best] > 0 else "\t"


def parse_rows(text: str, delimiter: str) -> list[list[str]]:
    """Zerlegt in Zellen. Überspringt Anki-Metazeilen (#…) und komplett leere Zeilen.
    Nutzt das csv-Modul, damit Anführungszeichen/eingebettete Trennzeichen korrekt sind."""
    body = "\n".join(ln for ln in text.splitlines()
                     if ln.strip() and not ln.startswith(_ANKI_COMMENT))
    if not body:
        return []
    reader = csv.reader(io.StringIO(body), delimiter=delimiter)
    rows = []
    for cells in reader:
        cells = [c.strip() for c in cells]
        if any(cells):
            rows.append(cells)
    return rows


def looks_like_header(row: list[str]) -> bool:
    """Heuristik: eine Kopfzeile trägt typische Spaltennamen (front/term/begriff …) und
    keine offensichtlichen Sprachdaten. Nur ein VORSCHLAG — der Nutzer bestätigt."""
    HEADERS = {"front", "back", "term", "translation", "begriff", "übersetzung", "uebersetzung",
               "palabra", "traducción", "traduccion", "word", "meaning", "es", "de", "español",
               "espanol", "alemán", "aleman", "deutsch", "spanisch", "termino", "término"}
    cells = [c.lower().strip() for c in row]
    return sum(1 for c in cells if c in HEADERS) >= 1


def build_preview(text: str, delimiter: str | None = None,
                  term_col: int = 0, translation_col: int = 1,
                  has_header: bool | None = None, existing_terms: set[str] | None = None,
                  sample_size: int = 12) -> dict:
    """Die Vorschau vor dem Übernehmen: erkanntes Trennzeichen, Spaltenzahl, ein paar
    Beispielzeilen mit 'neu?'-Markierung und die Zählung neu/schon-vorhanden. Schreibt nichts."""
    delimiter = delimiter or sniff_delimiter(text)
    rows = parse_rows(text, delimiter)
    if has_header is None:
        has_header = bool(rows) and looks_like_header(rows[0])
    header = rows[0] if (has_header and rows) else None
    data_rows = rows[1:] if has_header else rows

    items = extract_items(data_rows, term_col, translation_col)
    existing = {t.lower() for t in (existing_terms or set())}

    seen_in_file: set[str] = set()
    new_count = dup_count = 0
    preview = []
    for it in items:
        key = it["term"].lower()
        if key in existing or key in seen_in_file:
            status = "dup"
            dup_count += 1
        else:
            status = "new"
            new_count += 1
        seen_in_file.add(key)
        if len(preview) < sample_size:
            preview.append({**it, "status": status})

    ncols = max((len(r) for r in rows), default=0)
    return {
        "delimiter": delimiter,
        "columns": ncols,
        "header": header,
        "has_header": has_header,
        "term_col": term_col,
        "translation_col": translation_col,
        "total": len(items),
        "new_count": new_count,
        "dup_count": dup_count,
        "sample": preview,
    }


def extract_items(data_rows: list[list[str]], term_col: int,
                  translation_col: int) -> list[dict]:
    """Aus den (Kopf-freien) Zeilen die Begriff/Übersetzung-Paare ziehen. Zeilen ohne
    beide Spalten fallen still raus. Innerhalb der Datei wird auf term dedupliziert
    (erster Treffer gewinnt)."""
    out: list[dict] = []
    seen: set[str] = set()
    for row in data_rows:
        if term_col >= len(row) or translation_col >= len(row):
            continue
        term = row[term_col].strip()
        translation = row[translation_col].strip()
        if not term or not translation:
            continue
        key = term.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append({"term": term, "translation": translation})
    return out
