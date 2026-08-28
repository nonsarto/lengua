"""
grammar_catalog.py — Temario: das Curriculum (A1-B2) + der Lektions-Generator.

Goldene Regeln, wie in seed_reference.py:
- SLUGS SIND KURATIERTER CODE. Die Themenliste unten ist Hand-Arbeit (angelehnt an die
  Referenz-App + Plan Curricular); das LLM schreibt nur den INHALT der Lektionen.
- Das Konzept-Rückgrat bleibt die einzige Wahrheit für den Lernstand: jedes Thema zeigt
  per concept_slug auf sein Konzept (nullable — nicht alles hat eins). Der Katalog
  verlinkt, er kopiert keinen Lernstand.
- Nichts friert automatisch ein: push schreibt reviewed=false; `approve` ist der separate,
  menschliche Schritt NACH dem Gegenlesen von GRAMMAR_REVIEW.md.

Usage (from backend/app/):
  python grammar_catalog.py generate   # LLM → db/seed/grammar_lessons.json + GRAMMAR_REVIEW.md
                                       #   (nur ANTHROPIC_API_KEY nötig; resumable)
  python grammar_catalog.py push      # Topics + Lektionen → Supabase, reviewed=false
  python grammar_catalog.py approve   # reviewed=true für alle Seed-Lektionen (erst NACH dem Gegenlesen!)
"""

import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

from anthropic import Anthropic  # noqa: E402

LESSONS_JSON = ROOT / "db" / "seed" / "grammar_lessons.json"
REVIEW_MD = ROOT / "GRAMMAR_REVIEW.md"

# Einmalige Content-Arbeit — stärkstes Modell, Qualität vor Kosten (wie seed_reference).
SEED_MODEL = "claude-opus-4-8"

# --------------------------------------------------------------------------------------
# DAS CURRICULUM — kuratiert, Reihenfolge = order_index innerhalb des Niveaus.
# (slug, level, title_es, subtitle_de, concept_slug | None)
# concept_slug zeigt auf das Konzept-Rückgrat (Status im Katalog); None = kein Konzept,
# das Thema bleibt dann dauerhaft 'sin_ver'. Mapping ist Hand-Arbeit — beim Gegenlesen prüfen.
# --------------------------------------------------------------------------------------
TOPICS: list[tuple[str, str, str, str, str | None]] = [
    # ---- A1 ----
    ("articulos-definidos",            "A1", "Artículos Definidos",
     "el, la, los, las — der bestimmte Artikel",                "articulos"),
    ("articulos-indeterminados",       "A1", "Artículos Indeterminados",
     "un, una, unos, unas — der unbestimmte Artikel",           "articulos"),
    ("genero-numero-sustantivo",       "A1", "Género y Número del Sustantivo",
     "Genus und Plural der Substantive",                        "genero-y-numero"),
    ("adjetivos-concordancia-posicion", "A1", "Adjetivos: Concordancia y Posición",
     "Angleichung und Stellung der Adjektive",                  "concordancia-adjetivo"),
    ("pronombres-personales",          "A1", "Pronombres Personales",
     "Die Subjektpronomen: yo, tú, él …",                       None),  # kein 1:1-Konzept (tuteo-vs-usted deckt nur einen Teil)
    ("pronombres-posesivos",           "A1", "Pronombres Posesivos",
     "mi, tu, su — Possessivbegleiter und -pronomen",           "posesivos"),
    ("ser-estar-tener",                "A1", "Verbos Ser, Estar y Tener",
     "Die Grundverben: sein und haben",                         "ser-vs-estar"),
    ("hay-estar",                      "A1", "Hay / Estar",
     "„es gibt“ vs. „sich befinden“",                           "estar-vs-hay"),
    ("muy-mucho",                      "A1", "Muy / Mucho",
     "sehr vs. viel",                                           "muy-vs-mucho"),
    ("presente-indicativo-1",          "A1", "Presente de Indicativo I",
     "Regelmäßige Verben im Präsens",                           "presente-indicativo"),
    ("pronombres-demostrativos",       "A1", "Pronombres Demostrativos",
     "este, ese, aquel — Zeigewörter",                          "demostrativos"),
    ("interrogativos",                 "A1", "Interrogativos",
     "Fragewörter: qué, cuál, quién …",                         "interrogativos"),
    # ---- A2 ----
    ("conjunciones",                   "A2", "Conjunciones",
     "Bindewörter: y, pero, porque …",                          None),
    ("acentuacion",                    "A2", "Acentuación",
     "Betonung und der geschriebene Akzent",                    None),
    ("preposiciones",                  "A2", "Preposiciones",
     "Die wichtigsten Präpositionen",                           "preposiciones-a-en-de"),
    ("presente-indicativo-2",          "A2", "Presente de Indicativo II",
     "Unregelmäßige Verben im Präsens",                         "presente-indicativo"),
    ("pronombres-complemento-directo", "A2", "Pronombres de Complemento Directo",
     "lo, la, los, las — direkte Objektpronomen",               "pronombres-od"),
    ("gerundio",                       "A2", "Gerundio",
     "hablando, comiendo — die Verlaufsform",                   "gerundio"),
    ("participio",                     "A2", "Participio",
     "hablado, comido — das Partizip",                          "participio"),
    ("pronombres-reflexivos",          "A2", "Pronombres Reflexivos",
     "me, te, se — reflexive Verben",                           "verbos-reflexivos"),
    ("futuro",                         "A2", "Futuro",
     "hablaré — das einfache Futur",                            "futuro-simple"),
    ("apocope",                        "A2", "Apócope",
     "buen, gran, primer — verkürzte Formen",                   "apocope"),
    ("comparativos-superlativos",      "A2", "Comparativos y Superlativos",
     "más que, el más — vergleichen und steigern",              "comparativos"),
    # ---- B1 ----
    ("pronombres-complemento-indirecto", "B1", "Pronombres Átonos de Complemento Indirecto",
     "me, te, le — indirekte Objektpronomen",                   "pronombres-oi"),
    ("preterito-indefinido",           "B1", "Pretérito Indefinido",
     "hablé — die abgeschlossene Vergangenheit",                "indefinido"),
    ("preterito-imperfecto",           "B1", "Pretérito Imperfecto de Indicativo",
     "hablaba — die beschreibende Vergangenheit",               "imperfecto"),
    ("contraste-indefinido-imperfecto", "B1", "Contraste Indefinido / Imperfecto",
     "Wann welche Vergangenheit?",                              "indefinido-vs-imperfecto"),
    ("el-vs-lo",                       "B1", "Diferencia entre el y lo",
     "el vs. lo — Artikel oder Neutrum?",                       None),
    ("imperativo",                     "B1", "Imperativo",
     "¡habla! — der Imperativ",                                 "imperativo-afirmativo"),
    ("condicional-simple",             "B1", "Condicional Simple",
     "hablaría — der Konditional",                              "condicional-simple"),
    # ---- B2 ----
    ("preterito-perfecto-compuesto",   "B2", "Pretérito Perfecto Compuesto",
     "he hablado — das zusammengesetzte Perfekt",               "perfecto"),
    ("preterito-pluscuamperfecto",     "B2", "Pretérito Pluscuamperfecto",
     "había hablado — die Vorvergangenheit",                    "pluscuamperfecto"),
    ("subjuntivo-presente",            "B2", "Subjuntivo (Presente)",
     "Der Subjuntivo im Präsens",                               "subjuntivo-presente"),
    ("imperfecto-subjuntivo",          "B2", "Imperfecto de Subjuntivo",
     "hablara / hablase — Subjuntivo der Vergangenheit",        "subjuntivo-imperfecto"),
    ("oraciones-condicionales",        "B2", "Oraciones Condicionales",
     "si-Sätze: real und irreal",                               "condicional-irreal"),
    ("perifrasis-verbales",            "B2", "Perífrasis Verbales",
     "volver a, seguir + gerundio …",                           "perifrasis-verbales"),
    ("marcadores-temporales",          "B2", "Marcadores Temporales",
     "desde, hace, durante — Zeitangaben",                      "desde-hace-durante"),
    ("voz-pasiva-refleja",             "B2", "Voz Pasiva y Pasiva Refleja",
     "ser + participio und das Reflexivpassiv",                 "voz-pasiva"),
    ("estilo-indirecto",               "B2", "Estilo Indirecto",
     "dijo que … — die indirekte Rede",                         "estilo-indirecto"),
]

# --------------------------------------------------------------------------------------
# Konzept → Topic für Konzepte OHNE eigenes Thema, deren Inhalt eine Lektion mit abdeckt.
# Der Temario ist das führende Lese-Medium: Links aus Inicio/Capturar tragen Konzept-Slugs,
# die hier auf die passende Lektion aufgelöst werden (db.get_grammar_topic_detail).
# Kuratiert wie das Curriculum — nur eintragen, was die Lektion wirklich behandelt.
# --------------------------------------------------------------------------------------
CONCEPT_ALIASES: dict[str, str] = {
    "por-vs-para":              "preposiciones",           # eigene por/para-Tabelle
    "tuteo-vs-usted":           "pronombres-personales",   # tú/usted-Abschnitt
    "vosotros-vs-ustedes":      "pronombres-personales",   # Anrede-Tabelle
    "estar-gerundio":           "gerundio",                # estar + gerundio ist der Kern der Lektion
    "imperativo-negativo":      "imperativo",              # verneinte Formen enthalten
    "condicional-real":         "oraciones-condicionales", # realer si-Satz = Typ 1
    "desencadenantes-subjuntivo": "subjuntivo-presente",   # Auslöser-Liste in "Verwendung"
}

# --------------------------------------------------------------------------------------
# Block-Schema (Structured Output): das LLM füllt Inhalt, nie Struktur.
# Spiegelbild des TS-Typs Block in frontend/components/LessonBlocks.tsx — synchron halten.
# --------------------------------------------------------------------------------------
def _block(props: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": props, "required": required,
            "additionalProperties": False}

_ES_DE = _block({"es": {"type": "string"}, "de": {"type": "string"}}, ["es", "de"])
_USECASE = _block({"title": {"type": "string"}, "es": {"type": "string"},
                   "de": {"type": "string"}}, ["title", "es", "de"])

BLOCK_SCHEMA = {"anyOf": [
    _block({"type": {"enum": ["paragraph"]}, "text": {"type": "string"}}, ["type", "text"]),
    _block({"type": {"enum": ["heading"]}, "text": {"type": "string"}}, ["type", "text"]),
    _block({"type": {"enum": ["table"]}, "caption": {"type": "string"},
            "headers": {"type": "array", "items": {"type": "string"}},
            "rows": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}},
           ["type", "caption", "headers", "rows"]),
    _block({"type": {"enum": ["usecases"]},
            "items": {"type": "array", "items": _USECASE}}, ["type", "items"]),
    _block({"type": {"enum": ["examples"]},
            "items": {"type": "array", "items": _ES_DE}}, ["type", "items"]),
    _block({"type": {"enum": ["note"]}, "variant": {"enum": ["tip", "warning"]},
            "text": {"type": "string"}}, ["type", "variant", "text"]),
]}

LESSON_SCHEMA = {
    "type": "object",
    "properties": {"blocks": {"type": "array", "items": BLOCK_SCHEMA}},
    "required": ["blocks"],
    "additionalProperties": False,
}

SYSTEM = """Du schreibst Lektionen für eine Spanisch-Lern-App. Zielgruppe: deutschsprachige
Erwachsene, die in Spanien leben.

Sprache: Erklärungen auf Deutsch. Alle Beispielsätze auf Spanisch, die deutsche Übersetzung
steht im jeweiligen "de"-Feld. Grammatische Fachbegriffe auf Deutsch, der Themenname bleibt
spanisch. Überschriften ("heading") auf Deutsch.

Varietät: europäisches Spanisch (Spanien). Vosotros-Formen immer mitführen.

Aufbau jeder Lektion, in dieser Reihenfolge:
1. Ein paragraph: was das Thema ist und wozu man es braucht (max. 60 Wörter).
2. heading + table(s): die Formen oder Regeln. Bei Konjugations- und Formentabellen enthält
   die ERSTE Spalte immer die Person (yo / tú / él, ella, usted / nosotros, nosotras /
   vosotros, vosotras / ellos, ellas, ustedes), der erste header ist "" (leer), weitere
   Spalten sind die Verben oder Endungen. Alle rows haben exakt so viele Einträge wie headers.
3. heading "Verwendung" + ein usecases-Block mit 3-5 Einträgen (title = der Verwendungsfall
   auf Deutsch, es = spanisches Beispiel, de = deutsche Übersetzung).
4. Optional: heading + table für Unregelmäßigkeiten oder Ausnahmen — nur belegte, echte
   Formen, keine erfundenen.
5. Genau EIN note-Block (variant "warning"): der häufigste Fehler deutscher Muttersprachler
   bei diesem Thema — konkret, nicht generisch.

Gesamtlänge 6-12 Blöcke. Keine Übungen, keine Aufgaben, keine Anrede des Lesers mit "Sie".
Duzen oder unpersönlich formulieren. Genauigkeit vor Fülle — die Texte werden von einem
Menschen gegengelesen und dann eingefroren."""


def _user_prompt(topic: tuple, covered: list[str]) -> str:
    slug, level, title, subtitle, _ = topic
    prev = "\n".join(f"- {t}" for t in covered) if covered else "- (noch keine)"
    return (f"Thema: {title}\nNiveau: {level}\nKurzbeschreibung: {subtitle}\n"
            f"Vorher behandelte Themen (nicht erneut von null erklären):\n{prev}")


def _validate_lesson(lesson: dict) -> None:
    """Strukturprüfung beim Generieren, nicht erst beim Rendern. Das JSON-Schema sichert
    die Blocktypen; hier kommen die Invarianten, die ein Schema nicht ausdrücken kann."""
    blocks = lesson["blocks"]
    if not 6 <= len(blocks) <= 12:
        raise ValueError(f"{len(blocks)} Blöcke (erlaubt: 6-12)")
    if blocks[0]["type"] != "paragraph":
        raise ValueError("Lektion beginnt nicht mit einem paragraph")
    notes = [b for b in blocks if b["type"] == "note"]
    if len(notes) != 1:
        raise ValueError(f"{len(notes)} note-Blöcke (erwartet: genau 1)")
    if not any(b["type"] == "table" for b in blocks):
        raise ValueError("keine Tabelle")
    usecases = [b for b in blocks if b["type"] == "usecases"]
    if len(usecases) != 1 or not 3 <= len(usecases[0]["items"]) <= 5:
        raise ValueError("usecases fehlen oder haben nicht 3-5 Einträge")
    for b in blocks:
        if b["type"] == "table":
            for row in b["rows"]:
                if len(row) != len(b["headers"]):
                    raise ValueError(f"Tabellenzeile mit {len(row)} Zellen, "
                                     f"headers haben {len(b['headers'])}")


def _load() -> dict:
    return json.loads(LESSONS_JSON.read_text()) if LESSONS_JSON.exists() else {}


def _save(data: dict) -> None:
    LESSONS_JSON.parent.mkdir(parents=True, exist_ok=True)
    LESSONS_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def _call(client: Anthropic, prompt: str) -> dict:
    """Netz-Aussetzer (ReadTimeout mitten im Stream) nicht den Lauf kosten lassen:
    bis zu 3 Versuche mit Backoff, dann wirklich aufgeben."""
    import httpx
    for attempt in range(3):
        try:
            return _call_once(client, prompt)
        except (httpx.HTTPError, TimeoutError) as e:
            if attempt == 2:
                raise
            print(f"  … Netzfehler ({type(e).__name__}), neuer Versuch in 15 s")
            time.sleep(15)
    raise AssertionError("unreachable")


def _call_once(client: Anthropic, prompt: str) -> dict:
    with client.messages.stream(
        model=SEED_MODEL,
        max_tokens=8000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        output_config={"format": {"type": "json_schema", "schema": LESSON_SCHEMA}},
    ) as stream:
        resp = stream.get_final_message()
    if resp.stop_reason == "max_tokens":
        raise RuntimeError("Lektion abgeschnitten — max_tokens erhöhen")
    text = next(b.text for b in resp.content if b.type == "text")
    return json.loads(text)


# --------------------------------------------------------------------------------------
def generate() -> None:
    """Sequenziell mit kleinem Delay, nicht parallel — bei 39 Aufrufen ist Geschwindigkeit
    egal, Nachvollziehbarkeit bei Fehlern nicht. Resumable: vorhandene Slugs werden übersprungen."""
    client = Anthropic()
    lessons = _load()
    todo = [t for t in TOPICS if t[0] not in lessons]
    print(f"Lektionen: {len(lessons)} vorhanden, {len(todo)} zu generieren")

    for topic in todo:
        slug = topic[0]
        covered = [f"{t[2]} ({t[1]})" for t in TOPICS[:TOPICS.index(topic)]]
        lesson, last_err = None, None
        for attempt in (1, 2):  # eine strukturell kaputte Lektion einmal neu versuchen
            candidate = _call(client, _user_prompt(topic, covered))
            try:
                _validate_lesson(candidate)
                lesson = candidate
                break
            except ValueError as e:
                last_err = e
                print(f"  ! {slug}: {e} (Versuch {attempt})")
        if lesson is None:
            sys.exit(f"Abbruch bei '{slug}': {last_err} — erneut starten setzt hier fort.")
        lessons[slug] = lesson
        _save(lessons)
        print(f"  ✓ {slug} ({len(lessons)}/{len(TOPICS)})")
        time.sleep(2)

    write_review(lessons)
    print(f"\nFertig. Gegenlesen: {REVIEW_MD}")
    print("Danach: python grammar_catalog.py push  →  approve")


def write_review(lessons: dict) -> None:
    lines = [
        "# GRAMMAR_REVIEW — Temario-Lektionen zum Gegenlesen",
        "",
        "Von Opus generiert, von dir eingefroren. Korrigiere direkt in",
        "`db/seed/grammar_lessons.json` (diese Datei ist nur die Leseansicht). Erfahrungsgemäß",
        "prüfen: erfundene unregelmäßige Formen, fehlende vosotros-Spalte, generische",
        "note-Blöcke, und das concept_slug-Mapping in grammar_catalog.py. Wenn alles stimmt:",
        "`python grammar_catalog.py push` und danach `python grammar_catalog.py approve`.",
        "",
        f"**{len(lessons)}/{len(TOPICS)} Lektionen**",
        "",
    ]
    for slug, level, title, subtitle, concept in TOPICS:
        lesson = lessons.get(slug)
        if not lesson:
            continue
        lines += [f"## `{slug}` — {title}  ({level})",
                  f"*{subtitle}* · Konzept: `{concept or '—'}`", ""]
        for b in lesson["blocks"]:
            if b["type"] == "paragraph":
                lines.append(b["text"])
            elif b["type"] == "heading":
                lines.append(f"### {b['text']}")
            elif b["type"] == "table":
                lines.append(f"**{b['caption']}**" if b.get("caption") else "")
                lines.append("| " + " | ".join(b["headers"]) + " |")
                lines.append("|" + "---|" * len(b["headers"]))
                lines += ["| " + " | ".join(r) + " |" for r in b["rows"]]
            elif b["type"] == "usecases":
                lines += [f"- **{i['title']}** — _{i['es']}_ ({i['de']})" for i in b["items"]]
            elif b["type"] == "examples":
                lines += [f"- _{i['es']}_ ({i['de']})" for i in b["items"]]
            elif b["type"] == "note":
                icon = "⚠️" if b["variant"] == "warning" else "💡"
                lines.append(f"> {icon} {b['text']}")
            lines.append("")
    REVIEW_MD.write_text("\n".join(lines))


def push() -> None:
    from db import get_db
    db = get_db()
    lessons = _load()
    if not lessons:
        sys.exit("Nichts zu pushen — erst `generate` laufen lassen.")

    order: dict[str, int] = {}
    for slug, level, title, subtitle, concept in TOPICS:
        order[level] = order.get(level, 0) + 1
        db.c.table("grammar_topics").upsert({
            "slug": slug, "level": level, "title_es": title, "subtitle_de": subtitle,
            "order_index": order[level], "concept_slug": concept,
        }, on_conflict="slug").execute()

    ids = {r["slug"]: r["id"] for r in
           db.c.table("grammar_topics").select("id, slug").execute().data}
    pushed = 0
    for slug, lesson in lessons.items():
        if slug not in ids:
            print(f"  ! Lektion ohne Topic übersprungen: {slug}")
            continue
        db.c.table("grammar_lessons").upsert({
            "topic_id": ids[slug], "version": 1, "blocks": lesson["blocks"],
            "reviewed": False,  # eingefroren wird nur durch den menschlichen approve-Schritt
        }, on_conflict="topic_id,version").execute()
        pushed += 1
    print(f"Gepusht: {len(TOPICS)} Topics, {pushed} Lektionen (reviewed=false).")
    print("Nach dem Gegenlesen von GRAMMAR_REVIEW.md: python grammar_catalog.py approve")


def approve() -> None:
    from db import get_db
    db = get_db()
    slugs = [t[0] for t in TOPICS]
    topics = (db.c.table("grammar_topics").select("id").in_("slug", slugs).execute().data)
    (db.c.table("grammar_lessons").update({"reviewed": True})
     .in_("topic_id", [t["id"] for t in topics]).execute())
    print(f"Eingefroren: Lektionen von {len(topics)} Topics → reviewed=true.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "generate":
        generate()
    elif cmd == "push":
        push()
    elif cmd == "approve":
        approve()
    else:
        sys.exit(__doc__)
