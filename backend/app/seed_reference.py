"""
seed_reference.py — Slice 2: the concept backbone + the frequent irregular verbs.

Golden rules honored:
- SLUGS ARE CURATED CODE, not LLM output. The lists below are hand-anchored to the
  inventory of the Plan Curricular del Instituto Cervantes (A1-B2). analyze() tags
  against these slugs instead of inventing new ones.
- The LLM only writes CONTENT (explanations, paradigms, conjugations). Structure is code.
- Nothing is frozen automatically: push writes reviewed=false; `approve` is a separate,
  human-triggered step AFTER you read SEED_REVIEW.md.

Usage (from backend/app/):
  python seed_reference.py generate   # LLM → db/seed/*.json + SEED_REVIEW.md (nur ANTHROPIC_API_KEY nötig)
  python seed_reference.py push       # JSON → Supabase, reviewed=false      (braucht SUPABASE_* in .env)
  python seed_reference.py approve    # reviewed=true für alle Seed-Slugs    (erst NACH dem Gegenlesen!)

`generate` is resumable: existing entries in the JSON files are skipped.
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

from anthropic import Anthropic  # noqa: E402

SEED_DIR = ROOT / "db" / "seed"
CONCEPTS_JSON = SEED_DIR / "concepts.json"
VERBS_JSON = SEED_DIR / "verbs.json"
REVIEW_MD = ROOT / "SEED_REVIEW.md"

# Seed generation is one-time content work — use the strongest model, quality over cost.
SEED_MODEL = "claude-opus-4-8"

# --------------------------------------------------------------------------------------
# THE BACKBONE — curated by hand, anchored to the Plan Curricular (A1-B2). Slugs are
# stable identities: never rename, never regenerate. (slug, label_es, ctype, cefr)
# --------------------------------------------------------------------------------------
CONCEPTS: list[tuple[str, str, str, str]] = [
    # ---- tiempos verbales (ctype: tense) ----
    ("presente-indicativo",      "Presente de indicativo",              "tense", "A1"),
    ("futuro-proximo",           "Futuro próximo (ir a + infinitivo)",  "tense", "A1"),
    ("estar-gerundio",           "Estar + gerundio",                    "tense", "A2"),
    ("perfecto",                 "Pretérito perfecto",                  "tense", "A2"),
    ("indefinido",               "Pretérito indefinido",                "tense", "A2"),
    ("imperfecto",               "Pretérito imperfecto",                "tense", "B1"),
    ("pluscuamperfecto",         "Pretérito pluscuamperfecto",          "tense", "B1"),
    ("futuro-simple",            "Futuro simple",                       "tense", "B1"),
    ("condicional-simple",       "Condicional simple",                  "tense", "B1"),
    ("imperativo-afirmativo",    "Imperativo afirmativo",               "tense", "A2"),
    ("imperativo-negativo",      "Imperativo negativo",                 "tense", "B1"),
    ("subjuntivo-presente",      "Presente de subjuntivo",              "tense", "B1"),
    ("subjuntivo-imperfecto",    "Imperfecto de subjuntivo",            "tense", "B2"),
    ("gerundio",                 "El gerundio",                         "tense", "A2"),
    ("participio",               "El participio",                       "tense", "A2"),
    # ---- conceptos gramaticales (ctype: grammar) ----
    ("ser-vs-estar",             "Ser vs. estar",                       "grammar", "A1"),
    ("estar-vs-hay",             "Estar vs. hay",                       "grammar", "A1"),
    ("genero-y-numero",          "Género y número del sustantivo",      "grammar", "A1"),
    ("articulos",                "Artículos determinados e indeterminados", "grammar", "A1"),
    ("concordancia-adjetivo",    "Concordancia del adjetivo",           "grammar", "A1"),
    ("demostrativos",            "Demostrativos (este/ese/aquel)",      "grammar", "A1"),
    ("posesivos",                "Posesivos",                           "grammar", "A1"),
    ("muy-vs-mucho",             "Muy vs. mucho",                       "grammar", "A1"),
    ("negacion-doble",           "Negación (no ... nada/nadie/nunca)",  "grammar", "A1"),
    ("interrogativos",           "Interrogativos (qué/cuál/quién...)",  "grammar", "A1"),
    ("tuteo-vs-usted",           "Tú vs. usted",                        "grammar", "A1"),
    ("verbos-tipo-gustar",       "Verbos tipo gustar",                  "grammar", "A2"),
    ("verbos-reflexivos",        "Verbos reflexivos",                   "grammar", "A2"),
    ("a-personal",               "La a personal",                       "grammar", "A2"),
    ("preposiciones-a-en-de",    "Preposiciones básicas (a/en/de)",     "grammar", "A2"),
    ("comparativos",             "Comparativos",                        "grammar", "A2"),
    ("superlativos",             "Superlativos",                        "grammar", "A2"),
    ("pronombres-od",            "Pronombres de objeto directo",        "grammar", "A2"),
    ("pronombres-oi",            "Pronombres de objeto indirecto",      "grammar", "A2"),
    ("saber-vs-conocer",         "Saber vs. conocer",                   "grammar", "A2"),
    ("pedir-vs-preguntar",       "Pedir vs. preguntar",                 "grammar", "A2"),
    ("ir-vs-venir",              "Ir vs. venir",                        "grammar", "A2"),
    ("llevar-vs-traer",          "Llevar vs. traer",                    "grammar", "A2"),
    ("obligacion",               "Expresar obligación (tener que / hay que / deber)", "grammar", "A2"),
    ("acabar-de",                "Acabar de + infinitivo",              "grammar", "A2"),
    ("desde-hace-durante",       "Desde / hace / durante",              "grammar", "A2"),
    ("ya-vs-todavia",            "Ya vs. todavía",                      "grammar", "A2"),
    ("apocope",                  "Apócope (buen, gran, primer...)",     "grammar", "A2"),
    ("adverbios-mente",          "Adverbios en -mente",                 "grammar", "A2"),
    ("vosotros-vs-ustedes",      "Vosotros vs. ustedes",                "grammar", "A2"),
    ("indefinido-vs-perfecto",   "Indefinido vs. perfecto",             "grammar", "B1"),
    ("indefinido-vs-imperfecto", "Indefinido vs. imperfecto",           "grammar", "B1"),
    ("por-vs-para",              "Por vs. para",                        "grammar", "B1"),
    ("combinacion-pronombres",   "Combinación de pronombres (se lo)",   "grammar", "B1"),
    ("se-impersonal-pasivo",     "Se impersonal y pasivo",              "grammar", "B1"),
    ("desencadenantes-subjuntivo", "Desencadenantes del subjuntivo (quiero que, es importante que...)", "grammar", "B1"),
    ("subjuntivo-vs-indicativo", "Subjuntivo vs. indicativo (creo que / no creo que)", "grammar", "B1"),
    ("condicional-real",         "Oraciones condicionales reales (si + presente)", "grammar", "B1"),
    ("relativos",                "Oraciones de relativo (que/donde/el que)", "grammar", "B1"),
    ("estar-participio",         "Estar + participio (resultado)",      "grammar", "B1"),
    ("perifrasis-verbales",      "Perífrasis verbales (volver a, seguir + gerundio, llevar + gerundio)", "grammar", "B1"),
    ("quedar-vs-quedarse",       "Quedar vs. quedarse",                 "grammar", "B1"),
    ("condicional-irreal",       "Oraciones condicionales irreales (si + imperfecto de subjuntivo)", "grammar", "B2"),
    ("estilo-indirecto",         "Estilo indirecto",                    "grammar", "B2"),
    ("futuro-de-probabilidad",   "Futuro de probabilidad",              "grammar", "B2"),
    ("voz-pasiva",               "Voz pasiva",                          "grammar", "B2"),
    # ---- familias de patrones (ctype: pattern_family) ----
    ("stem-change-e-ie",         "Cambio de raíz e→ie (querer, pensar...)",   "pattern_family", "A2"),
    ("stem-change-o-ue",         "Cambio de raíz o→ue (poder, dormir...)",    "pattern_family", "A2"),
    ("stem-change-e-i",          "Cambio de raíz e→i (pedir, servir...)",     "pattern_family", "A2"),
    ("g-verbs",                  "Verbos en -go (tengo, pongo, salgo...)",    "pattern_family", "A2"),
    ("zc-verbs",                 "Verbos en -zco (conozco, conduzco...)",     "pattern_family", "A2"),
    ("y-verbs",                  "Verbos en -uir con y (construyo, huyo...)", "pattern_family", "B1"),
    ("irregular-indefinido",     "Indefinidos fuertes (estuve, tuve, pude...)", "pattern_family", "A2"),
    ("irregular-futuro",         "Futuros irregulares (tendré, saldré...)",   "pattern_family", "B1"),
    ("irregular-participio",     "Participios irregulares (hecho, visto...)", "pattern_family", "A2"),
    ("irregular-imperativo",     "Imperativos irregulares (pon, ten, ven, sal...)", "pattern_family", "A2"),
]

# ~60 most frequent irregular / stem-changing verbs, roughly by frequency (rank = index+1).
# Regular verbs are conjugated on the fly from tense paradigms — they are NOT stored.
VERBS: list[str] = [
    "ser", "estar", "haber", "tener", "hacer", "poder", "decir", "ir", "ver", "dar",
    "saber", "querer", "poner", "venir", "salir", "volver", "conocer", "sentir", "traer",
    "pensar", "seguir", "encontrar", "empezar", "entender", "pedir", "recordar", "contar",
    "dormir", "morir", "oír", "caer", "leer", "creer", "construir", "huir", "jugar",
    "servir", "repetir", "vestirse", "reír", "comenzar", "perder", "mover", "llover",
    "probar", "mostrar", "soler", "costar", "acostarse", "despertarse", "cerrar",
    "sentarse", "preferir", "mentir", "divertirse", "elegir", "corregir", "conducir",
    "traducir", "producir", "caber", "valer", "andar",
]

# --------------------------------------------------------------------------------------
# Structured-output schemas: the LLM fills content, never invents structure.
# --------------------------------------------------------------------------------------
_EXERCISE = {
    "type": "object",
    "properties": {"q": {"type": "string"}, "a": {"type": "string"}},
    "required": ["q", "a"],
    "additionalProperties": False,
}

CONCEPT_BATCH_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "slug": {"type": "string"},
                    "explanation": {"type": "string"},
                    "rule_of_thumb": {"type": "string"},
                    "german_pitfall": {"type": "string"},
                    "paradigm": {
                        "anyOf": [
                            {
                                "type": "object",
                                "properties": {
                                    "ar": {"type": "object", "additionalProperties": False,
                                           "properties": {p: {"type": "string"} for p in
                                                          ("yo", "tu", "el", "nosotros", "vosotros", "ellos")},
                                           "required": ["yo", "tu", "el", "nosotros", "vosotros", "ellos"]},
                                    "er": {"type": "object", "additionalProperties": False,
                                           "properties": {p: {"type": "string"} for p in
                                                          ("yo", "tu", "el", "nosotros", "vosotros", "ellos")},
                                           "required": ["yo", "tu", "el", "nosotros", "vosotros", "ellos"]},
                                    "ir": {"type": "object", "additionalProperties": False,
                                           "properties": {p: {"type": "string"} for p in
                                                          ("yo", "tu", "el", "nosotros", "vosotros", "ellos")},
                                           "required": ["yo", "tu", "el", "nosotros", "vosotros", "ellos"]},
                                },
                                "required": ["ar", "er", "ir"],
                                "additionalProperties": False,
                            },
                            {"type": "null"},
                        ]
                    },
                    "member_verbs": {"type": "array", "items": {"type": "string"}},
                    "default_exercises": {"type": "array", "items": _EXERCISE},
                },
                "required": ["slug", "explanation", "rule_of_thumb", "german_pitfall",
                             "paradigm", "member_verbs", "default_exercises"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["items"],
    "additionalProperties": False,
}

_PERSONS = {p: {"type": "string"} for p in ("yo", "tu", "el", "nosotros", "vosotros", "ellos")}
_TENSE_TABLE = {"type": "object", "properties": _PERSONS,
                "required": list(_PERSONS), "additionalProperties": False}

VERB_BATCH_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "infinitive": {"type": "string"},
                    "translation": {"type": "string"},
                    "cefr": {"anyOf": [{"type": "string", "enum": ["A1", "A2", "B1", "B2", "C1", "C2"]},
                                       {"type": "null"}]},
                    "pattern_tags": {"type": "array", "items": {"type": "string"}},
                    "irregularity_note": {"type": "string"},
                    "conjugations": {
                        "type": "object",
                        "properties": {
                            "presente": _TENSE_TABLE,
                            "indefinido": _TENSE_TABLE,
                            "imperfecto": _TENSE_TABLE,
                            "futuro": _TENSE_TABLE,
                            "condicional": _TENSE_TABLE,
                            "subjuntivo_presente": _TENSE_TABLE,
                            "imperativo": {
                                "type": "object",
                                "properties": {"tu": {"type": "string"}, "usted": {"type": "string"},
                                               "vosotros": {"type": "string"}},
                                "required": ["tu", "usted", "vosotros"],
                                "additionalProperties": False,
                            },
                            "gerundio": {"type": "string"},
                            "participio": {"type": "string"},
                        },
                        "required": ["presente", "indefinido", "imperfecto", "futuro", "condicional",
                                     "subjuntivo_presente", "imperativo", "gerundio", "participio"],
                        "additionalProperties": False,
                    },
                },
                "required": ["infinitive", "translation", "cefr", "pattern_tags",
                             "irregularity_note", "conjugations"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["items"],
    "additionalProperties": False,
}

CONCEPT_SYSTEM = """You write the reference content ("shared body") of a Spanish-grammar chapter
for a German speaker living in Barcelona. Target production variety: peninsular Spanish
(vosotros exists, distinción irrelevant in writing). Language rules:
- "explanation": simple, clear Spanish (3-6 sentences, aimed at the concept's CEFR level).
- "rule_of_thumb": 1-2 short Spanish sentences — the thing you'd say in a bar to explain it.
- "german_pitfall": GERMAN, 1-3 sentences. The contrastive trap for German speakers specifically
  (interference from German grammar). This is the most valuable field — be concrete.
- "paradigm": ONLY for tense concepts — the REGULAR endings table for -ar/-er/-ir model verbs
  (hablar/comer/vivir), fully conjugated forms. null for everything else.
- "member_verbs": ONLY for pattern-family concepts — 8-15 frequent members. Empty array otherwise.
- "default_exercises": 3 simple fill-in exercises (q with a gap, a with the solution). Spanish.
Accuracy over flourish. These texts get human-reviewed and then frozen."""

VERB_SYSTEM = """You produce reference conjugation data for frequent irregular Spanish verbs, for a
German learner in Barcelona (peninsular forms, vosotros included). Rules:
- "translation": German infinitive translation (e.g. "sein", "gehen").
- "pattern_tags": which of these pattern-family slugs apply (empty if none):
  stem-change-e-ie, stem-change-o-ue, stem-change-e-i, g-verbs, zc-verbs, y-verbs,
  irregular-indefinido, irregular-futuro, irregular-participio, irregular-imperativo
- "irregularity_note": ONE short Spanish sentence naming what's irregular.
- "conjugations": complete and exact. Reflexive verbs: include the pronoun (me acuesto).
  Defective verbs (llover, soler): use the forms that exist; repeat the 3rd person where a
  person doesn't apply is WRONG — instead write "—" for non-existent forms.
Accuracy is everything here; these tables get human-reviewed and then frozen."""


def _chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def _load(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def _save(path: Path, data: dict) -> None:
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def _call(client: Anthropic, system: str, prompt: str, schema: dict) -> list[dict]:
    with client.messages.stream(
        model=SEED_MODEL,
        max_tokens=16000,
        system=system,
        messages=[{"role": "user", "content": prompt}],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    ) as stream:
        resp = stream.get_final_message()
    if resp.stop_reason == "max_tokens":
        raise RuntimeError("seed batch truncated — shrink the chunk size")
    text = next(b.text for b in resp.content if b.type == "text")
    return json.loads(text)["items"]


# --------------------------------------------------------------------------------------
def generate() -> None:
    client = Anthropic()
    concepts = _load(CONCEPTS_JSON)
    verbs = _load(VERBS_JSON)

    todo_c = [(s, l, t, c) for (s, l, t, c) in CONCEPTS if s not in concepts]
    print(f"Konzepte: {len(concepts)} vorhanden, {len(todo_c)} zu generieren")
    for batch in _chunks(todo_c, 8):
        listing = "\n".join(f"- slug: {s} | label: {l} | tipo: {t} | nivel: {c}"
                            for (s, l, t, c) in batch)
        items = _call(client, CONCEPT_SYSTEM,
                      f"Write the reference content for these concepts:\n{listing}", CONCEPT_BATCH_SCHEMA)
        meta = {s: (l, t, c) for (s, l, t, c) in batch}
        for item in items:
            if item["slug"] not in meta:
                print(f"  ! unbekannter slug ignoriert: {item['slug']}")
                continue
            label, ctype, cefr = meta[item["slug"]]
            item.update({"label": label, "ctype": ctype, "cefr": cefr})
            concepts[item["slug"]] = item
        _save(CONCEPTS_JSON, concepts)
        print(f"  ✓ {len(concepts)}/{len(CONCEPTS)} Konzepte")

    todo_v = [v for v in VERBS if v not in verbs]
    print(f"Verben: {len(verbs)} vorhanden, {len(todo_v)} zu generieren")
    for batch in _chunks(todo_v, 5):
        items = _call(client, VERB_SYSTEM,
                      "Produce the full data for these verbs:\n" + "\n".join(f"- {v}" for v in batch),
                      VERB_BATCH_SCHEMA)
        for item in items:
            if item["infinitive"] not in VERBS:
                print(f"  ! unbekanntes Verb ignoriert: {item['infinitive']}")
                continue
            item["freq_rank"] = VERBS.index(item["infinitive"]) + 1
            verbs[item["infinitive"]] = item
        _save(VERBS_JSON, verbs)
        print(f"  ✓ {len(verbs)}/{len(VERBS)} Verben")

    write_review(concepts, verbs)
    print(f"\nFertig. Gegenlesen: {REVIEW_MD}")
    print("Danach: python seed_reference.py push  →  approve")


def write_review(concepts: dict, verbs: dict) -> None:
    lines = [
        "# SEED_REVIEW — Konzept-Rückgrat zum Gegenlesen",
        "",
        "Von Opus generiert, von dir eingefroren. Korrigiere direkt in `db/seed/*.json`",
        "(diese Datei ist nur die Leseansicht). Wenn alles stimmt:",
        "`python seed_reference.py push` und danach `python seed_reference.py approve`.",
        "",
        f"**{len(concepts)} Konzepte · {len(verbs)} Verben**",
        "",
        "## Konzepte",
    ]
    for slug, _, _, _ in CONCEPTS:
        it = concepts.get(slug)
        if not it:
            continue
        lines += [
            f"### `{slug}` — {it['label']}  ({it['ctype']}, {it['cefr']})",
            f"**Explicación:** {it['explanation']}",
            f"**Regla de oro:** {it['rule_of_thumb']}",
            f"**⚠️ Deutsche Falle:** {it['german_pitfall']}",
        ]
        if it.get("paradigm"):
            p = it["paradigm"]
            lines.append("**Paradigma (regular):** " + " · ".join(
                f"-{k}: {' / '.join(v.values())}" for k, v in p.items()))
        if it.get("member_verbs"):
            lines.append("**Verbos del patrón:** " + ", ".join(it["member_verbs"]))
        for ex in it.get("default_exercises", []):
            lines.append(f"- _{ex['q']}_ → **{ex['a']}**")
        lines.append("")
    lines.append("## Verben")
    for inf in VERBS:
        it = verbs.get(inf)
        if not it:
            continue
        c = it["conjugations"]
        lines += [
            f"### `{inf}` — {it['translation']}  ({it['cefr']}, rank {it['freq_rank']})",
            f"_{it['irregularity_note']}_  · patrones: {', '.join(it['pattern_tags']) or '—'}",
            f"- presente: {' / '.join(c['presente'].values())}",
            f"- indefinido: {' / '.join(c['indefinido'].values())}",
            f"- subj. presente: {' / '.join(c['subjuntivo_presente'].values())}",
            f"- futuro: {c['futuro']['yo']}… · imperativo tú: {c['imperativo']['tu']}"
            f" · gerundio: {c['gerundio']} · participio: {c['participio']}",
            "",
        ]
    REVIEW_MD.write_text("\n".join(lines))


def push() -> None:
    from db import get_db
    db = get_db()
    concepts, verbs = _load(CONCEPTS_JSON), _load(VERBS_JSON)
    if not concepts or not verbs:
        sys.exit("Nichts zu pushen — erst `generate` laufen lassen.")
    for slug, it in concepts.items():
        db.c.table("concepts").upsert({
            "slug": slug, "label": it["label"], "ctype": it["ctype"], "cefr": it["cefr"],
            "explanation": it["explanation"], "rule_of_thumb": it["rule_of_thumb"],
            "german_pitfall": it["german_pitfall"], "paradigm": it["paradigm"],
            "default_exercises": it["default_exercises"],
            "member_verbs": it["member_verbs"] or None,
            "reviewed": False,  # frozen only by the human `approve` step
        }, on_conflict="slug").execute()
    for inf, it in verbs.items():
        db.c.table("verbs").upsert({
            "infinitive": inf, "translation": it["translation"], "cefr": it["cefr"],
            "freq_rank": it["freq_rank"], "pattern_tags": it["pattern_tags"],
            "conjugations": it["conjugations"], "irregularity_note": it["irregularity_note"],
            "reviewed": False,
        }, on_conflict="infinitive").execute()
    print(f"Gepusht: {len(concepts)} Konzepte, {len(verbs)} Verben (alle reviewed=false).")
    print("Nach dem Gegenlesen von SEED_REVIEW.md: python seed_reference.py approve")


def approve() -> None:
    from db import get_db
    db = get_db()
    slugs = [s for (s, _, _, _) in CONCEPTS]
    db.c.table("concepts").update({"reviewed": True}).in_("slug", slugs).execute()
    db.c.table("verbs").update({"reviewed": True}).in_("infinitive", VERBS).execute()
    print(f"Eingefroren: {len(slugs)} Konzepte + {len(VERBS)} Verben → reviewed=true.")


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
