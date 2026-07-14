"""Sprachpaket Katalanisch (llengua) — Prompts, Cluster, Testfragen, Drill-Maps.
Rückgrat verankert an den CEFR-Programmen der Direcció General de Política Lingüística.
Besonderheit gegenüber Spanisch: der Lerner lebt in Barcelona und spricht Deutsch UND
(etwas) Spanisch — beide Interferenzen werden getaggt."""

LANG = "ca"
APP_NAME = "llengua"
DEFAULT_VARIETY = "central"

SYSTEM_PROMPT = """You are the analysis engine of a Catalan-learning tool for a German speaker
living in Barcelona who also speaks some Spanish. You receive a snippet the user captured from
real life and return a structured analysis (the response format is enforced — focus on content).

The user's production target variety is {variety} (default català central / Barcelona). But for
COMPREHENSION, treat all varieties as valid — never mark a Valencian, Balearic or other regional
form as "wrong", only note its region.

First infer the MODE from the input:
- "check"  : the user produced Catalan and implicitly asks if it's right.
- "decode" : the user captured something they don't understand (a sign, overheard speech, text).
- "brief"  : the user asks to be prepared for a situation ("prepara'm per a...", "demà tinc...").
- "listen" : a transcript of someone else speaking (fast, colloquial, possibly regional).

If an image is attached, read the Catalan in it (sign, menu, letter, form) and treat that text
as the captured input (usually mode "decode"). Barcelona signage mixes Catalan and Spanish —
if the captured text is actually Spanish, say so in "notes" and decode it anyway.

Field guidance:
- "gist": plain German translation. For decode/listen: what the captured text means. For check:
  the German meaning of the CORRECTED sentence. For brief: null.
- "correction": only for check-mode errors; "why" is ONE short German sentence. Castilianisms
  (using Spanish words/structures in Catalan: *bueno, *entonces, *tengo que, *lo que) count as
  errors in production — correct them and tag the concept.
- "region": use JSON null (not a string) when the item is standard; otherwise a lowercase tag
  like "valencià", "balear", "nord-occidental", "alguerès".
- "notes": GERMAN, 1-2 short sentences — grammatical peculiarities worth flagging (regionalisms,
  colloquial forms, castilianisms, notable constructions). Empty string if nothing stands out.
- Keep lemmas to genuinely useful items, not every word.
- "brief": ONLY for mode "brief", null otherwise. The prep package for the described situation:
  * "situation_name": short shelf name in Catalan (2-4 words, e.g. "reunió amb la casera").
  * "key_vocab": 8-15 genuinely situation-specific items, register matching the situation.
  * "phrases": 5-8 sentences WITH INTENT — things you DO with language there (proposar una
    solució, discrepar amb tacte, guanyar temps, demanar aclariments...). "intent" is the
    Catalan intent label, "es" the CATALAN phrase, "de" the German meaning.
  * "concepts": 2-4 grammar concepts this situation ACTIVATES, with canonical slugs and "why" =
    ONE German sentence explaining why this grammar matters here. LINK concepts — never copy
    grammar explanations into the package.
  In brief mode leave lemmas/concepts/verbs EMPTY (everything lives in the package).

Slug rules: kebab-case, stable, conceptual not surface. Prefer reusing obvious canonical slugs
(passat-perifrastic, pronoms-febles-od, pronom-en, pronom-hi, per-vs-per-a, ser-vs-estar-ca,
verbs-incoatius, apostrofacio, perifrasis-obligacio, ...). An error goes on the concept AND on
the violated pattern-family, not on the single verb. Concept "label" fields are short chapter
titles in CATALAN (the UI language), never German or Spanish. Only tag GRAMMAR phenomena
(structures, tenses, patterns, register/variety, castilianism-classes) — never vocabulary-topic
pseudo-concepts."""

CHAPTER_SYSTEM = """You write the reference content ("shared body") of ONE Catalan-grammar
chapter for a German speaker living in Barcelona who also speaks some Spanish. Target variety:
català central. Language rules:
- "label": a short chapter title in CATALAN (the UI language) — clean up the given label if
  it is German, Spanish or clumsy.
- "explanation": simple, clear Catalan (3-6 sentences, aimed at the concept's CEFR level).
- "rule_of_thumb": 1-2 short Catalan sentences — the thing you'd say in a bar to explain it.
- "german_pitfall": GERMAN, 1-3 sentences. The contrastive trap — from German AND from Spanish
  where relevant (the learner knows some Spanish; Spanish interference is the #1 error source
  in Catalan). Be concrete.
- "member_verbs": ONLY if this is a verb-pattern family (8-15 frequent members); else [].
- "default_exercises": 3 simple fill-in exercises (q with a gap, a with the solution). Catalan.
Accuracy over flourish. This draft gets human-reviewed before it is frozen."""

# --------------------------------------------------------------------- Cluster (Gramàtica)
GRAMMAR_CLUSTER: dict[str, str] = {
    **{s: "Estructura de la frase" for s in (
        "negacio", "interrogatius", "relatives", "estil-indirecte",
        "condicional-real", "condicional-irreal", "passiva-pronominal",
        "comparatius", "superlatius", "adverbis-ment",
        "subjuntiu-desencadenants", "caiguda-preposicions", "el-que-neutre",
        "expressio-hores")},
    **{s: "Verbs i contrastos" for s in (
        "ser-vs-estar-ca", "haver-hi", "verbs-tipus-agradar", "verbs-reflexius",
        "perifrasis-obligacio", "acabar-de", "estar-gerundi", "expressar-futur",
        "passat-perifrastic-vs-perfet", "imperfet-vs-passat")},
    **{s: "Substantius i adjectius" for s in (
        "genere-i-nombre", "articles-definits", "apostrofacio", "contraccions",
        "article-personal", "demostratius", "possessius", "quantitatius")},
    **{s: "Pronoms" for s in (
        "pronoms-febles-od", "pronoms-febles-oi", "combinacio-pronoms-febles",
        "pronom-en", "pronom-hi", "pronoms-forts", "tu-vs-voste")},
    **{s: "Preposicions" for s in (
        "per-vs-per-a", "preposicions-a-en-amb", "des-de-fa-durant")},
}
CLUSTER_TENSE_LABEL = "Temps"
CLUSTER_PATTERN_LABEL = "Conjugació"
CLUSTER_OTHER_LABEL = "Altres"

# --------------------------------------------------------------------- Drill-Maps (Practicar)
PATTERN_TENSE = {
    "verbs-incoatius": "present", "verbs-velaritzats": "present",
    "canvi-ortografic": "present", "alternanca-o-u": "present",
    "participis-irregulars": "participi", "imperatius-irregulars": "imperatiu",
    "futurs-irregulars": "futur",
    "present-indicatiu": "present", "imperfet": "imperfet",
    "futur-simple": "futur", "condicional-simple": "condicional",
    "subjuntiu-present": "subjuntiu_present",
    "passat-perifrastic-vs-perfet": "participi", "perfet": "participi",
}
TENSE_LABEL = {
    "present": "present", "imperfet": "imperfet", "futur": "futur",
    "condicional": "condicional", "subjuntiu_present": "subjuntiu present",
    "imperatiu": "imperatiu", "participi": "participi", "gerundi": "gerundi",
}
DEFAULT_DRILL_TENSE_SLUG = "present-indicatiu"
STEM_CHANGE_PREFIX = "alternanca"  # o/u-Wechsel trifft nur betonte Formen — wie stem-change im Spanischen

ONBOARDING_QUESTIONS: list[dict] = [
    # ---- A1 ----
    {"id": "a1-haverhi", "band": "A1", "concept": "haver-hi",
     "q": "___ molta gent al carrer.",
     "options": ["Està", "Hi ha", "És"], "correct": 1},
    {"id": "a1-apostrof", "band": "A1", "concept": "apostrofacio",
     "q": "___ escola és nova.",
     "options": ["La", "L'", "El"], "correct": 1},
    {"id": "a1-present", "band": "A1", "concept": "present-indicatiu",
     "q": "Nosaltres ___ a Barcelona.",
     "options": ["viu", "vivim", "viuen"], "correct": 1},
    {"id": "a1-contraccio", "band": "A1", "concept": "contraccions",
     "q": "Vinc ___ mercat de la Boqueria.",
     "options": ["de el", "del", "d'el"], "correct": 1},
    # ---- A2 ----
    {"id": "a2-incoatiu", "band": "A2", "concept": "verbs-incoatius",
     "q": "En aquest bar ___ menjar vegetarià.",
     "options": ["serveixen", "serven", "servixen"], "correct": 0},
    {"id": "a2-perifrastic", "band": "A2", "concept": "passat-perifrastic",
     "q": "Ahir ___ al cinema amb uns amics.",
     "options": ["vaig anar", "anava", "he anat"], "correct": 0},
    {"id": "a2-obligacio", "band": "A2", "concept": "perifrasis-obligacio",
     "q": "Demà ___ pagar el lloguer.",
     "options": ["he de", "tinc que", "dec"], "correct": 0},
    {"id": "a2-agradar", "band": "A2", "concept": "verbs-tipus-agradar",
     "q": "M'___ molt les tapes d'aquest bar.",
     "options": ["agrada", "agraden", "agrado"], "correct": 1},
    # ---- B1 ----
    {"id": "b1-perfet", "band": "B1", "concept": "passat-perifrastic-vs-perfet",
     "q": "Avui ___ molta feina a l'oficina.",
     "options": ["vaig tenir", "he tingut", "tenia"], "correct": 1},
    {"id": "b1-perpera", "band": "B1", "concept": "per-vs-per-a",
     "q": "Aquest regal és ___ tu.",
     "options": ["per", "per a", "a"], "correct": 1},
    {"id": "b1-en", "band": "B1", "concept": "pronom-en",
     "q": "—Vols cafè? —Sí, ___ vull una mica.",
     "options": ["en", "hi", "el"], "correct": 0},
    # ---- B2 ----
    {"id": "b2-irreal", "band": "B2", "concept": "condicional-irreal",
     "q": "Si tingués més diners, ___ un pis més gran.",
     "options": ["compraria", "compraré", "comprava"], "correct": 0},
]

BRIEF_PREFIX = "prepara'm per a"
ONBOARDING_CAPTURE_TEXT = "test de nivell inicial"

# --------------------------------------------------------------------- Personen (Konjugation)
PERSONS = ["jo", "tu", "ell", "nosaltres", "vosaltres", "ells"]
PERSON_LABEL = {"jo": "jo", "tu": "tu", "ell": "ell/ella", "nosaltres": "nosaltres",
                "vosaltres": "vosaltres", "ells": "ells/elles", "voste": "vostè"}
STEM_UNSTRESSED = ("nosaltres", "vosaltres")  # o/u-Alternanz trifft nur betonte Formen
