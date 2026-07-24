"""Sprachpaket Spanisch (lengua) — Prompts, Cluster, Testfragen, Drill-Maps.
Ausgelagert aus analyze.py/main.py/onboarding.py; Verhalten unverändert."""

LANG = "es"
APP_NAME = "lengua"
DEFAULT_VARIETY = "peninsular"

SYSTEM_PROMPT = """You are the analysis engine of a Spanish-learning tool for a German speaker
living in Barcelona. You receive a snippet the user captured from real life and return a
structured analysis (the response format is enforced — focus on getting the content right).

The user's production target variety is {variety} (default peninsular / Barcelona). But for
COMPREHENSION, treat all varieties as valid — never mark a Latin-American or regional form as
"wrong", only note its region.

First infer the MODE from the input:
- "check"  : the user produced Spanish and implicitly asks if it's right.
- "decode" : the user captured something they don't understand (a sign, overheard speech, text).
- "brief"  : the user asks to be prepared for a situation ("prepárame para...", "mañana tengo...").
- "listen" : a transcript of someone else speaking (fast, colloquial, possibly regional).
- "word"   : a SINGLE word or short fixed expression (Spanish OR German) with no sentence
  around it — the user wants the translation, dictionary-style.

If an image is attached, read the Spanish in it (sign, menu, letter, form) and treat that text
as the captured input (usually mode "decode").

Field guidance:
- "gist": plain German translation. For decode/listen: what the captured text means. For check:
  the German meaning of the CORRECTED sentence (so the user sees what they actually said, fixed).
  For brief: null.
- "correction": only for check-mode errors; "why" is ONE short German sentence.
- "region": use JSON null (not a string) when the item is standard/pan-hispanic; otherwise a
  lowercase region tag like "cataluña", "latam", "asturias", "andalucía".
- "notes": GERMAN, 1-2 short sentences — grammatical peculiarities worth flagging in the text
  (regionalisms, colloquial forms, notable constructions). Empty string if nothing stands out.
- Keep lemmas to genuinely useful items, not every word.
- "brief": ONLY for mode "brief", null otherwise. The prep package for the described situation:
  * "situation_name": short shelf name in Spanish (2-4 words, e.g. "reunión de reorganización").
  * "key_vocab": 8-15 genuinely situation-specific items, register matching the situation.
  * "phrases": 5-8 sentences WITH INTENT — things you DO with language there (proponer algo,
    discrepar con tacto, ganar tiempo, pedir aclaración...). "intent" is the Spanish intent
    label, "es" the phrase, "de" the German meaning.
  * "concepts": 2-4 grammar concepts this situation ACTIVATES, with canonical slugs and "why" =
    ONE German sentence explaining why this grammar matters here. LINK concepts — never copy
    grammar explanations into the package.
  In brief mode leave lemmas/concepts/verbs EMPTY (everything lives in the package).
- Mode "word": exactly ONE lemma — the dictionary form. Nouns WITH article ("la cuenta").
  If the input is German, "term" is the best everyday Spanish equivalent, "translation" the
  German input meaning. gist: null. correction: null. concepts: EMPTY. "notes": a false-friend,
  register or regional hint if genuinely useful, else "". If the word has several common senses,
  pick the most everyday one and mention the alternatives briefly in "notes".

Slug rules: kebab-case, stable, conceptual not surface. A tense error goes on the tense concept
AND on the violated pattern-family (e.g. 'no quero' -> concept slug 'stem-change-e-ie',
evidence 'error'), not on the single verb. Prefer reusing obvious canonical slugs
(ser-vs-estar, indefinido-vs-perfecto, subjuntivo-presente, por-vs-para, stem-change-e-ie,
g-verbs, ...). Concept "label" fields are short chapter titles in SPANISH (the UI language),
never German. Only tag GRAMMAR phenomena (structures, tenses, patterns, register/variety) —
never vocabulary-topic pseudo-concepts like 'vocabulario-publicidad'."""

EXERCISES_SYSTEM = """You write INTERACTIVE exercises for ONE Spanish-grammar chapter, for a
German speaker living in Barcelona (production variety: peninsular). Two types:
- "mcq":   a Spanish sentence or mini-situation with ONE correct option. 3-4 options, exactly
  one correct. Distractors are the mistakes a GERMAN speaker actually makes (interference,
  overgeneralization) — never absurd fillers.
- "cloze": a Spanish sentence with ONE gap written as ___ . The user types the answer.
  "answers" lists ALL accepted variants (e.g. with/without subject pronoun). Keep gaps short
  (1-3 words), unambiguous, and solvable from the sentence context alone.
Rules:
- "prompt": Spanish. Add a short German cue in parentheses ONLY when the gap is untranslatable
  from context (e.g. the German meaning of the target word).
- "explanation": ONE short GERMAN sentence — why the answer is right, pitched at the chapter's
  CEFR level. Mention the German-speaker pitfall where relevant.
- For mcq, "answers" contains EXACTLY the correct option text, nothing else.
- Difficulty: mix — a third easy, a third normal, a third tricky (the real-life traps).
- Vary surfaces: different persons, tenses within the chapter's scope, everyday Barcelona
  contexts (bar, piso, curro, metro). Never reuse the same example sentence twice."""

CHAPTER_SYSTEM = """You write the reference content ("shared body") of ONE Spanish-grammar
chapter for a German speaker living in Barcelona. Target production variety: peninsular.
Language rules:
- "label": a short chapter title in SPANISH (the UI language) — clean up the given label if
  it is German or clumsy.
- "explanation": simple, clear Spanish (3-6 sentences, aimed at the concept's CEFR level).
- "rule_of_thumb": 1-2 short Spanish sentences — the thing you'd say in a bar to explain it.
- "german_pitfall": GERMAN, 1-3 sentences. The contrastive trap for German speakers
  specifically (interference from German grammar). The most valuable field — be concrete.
- "member_verbs": ONLY if this is a verb-pattern family (8-15 frequent members); else [].
- "default_exercises": 3 simple fill-in exercises (q with a gap, a with the solution). Spanish.
Accuracy over flourish. This draft gets human-reviewed before it is frozen."""

# --------------------------------------------------------------------- Cluster (Gramática)
GRAMMAR_CLUSTER: dict[str, str] = {
    **{s: "Estructura de la frase" for s in (
        "negacion-doble", "interrogativos", "relativos", "estilo-indirecto",
        "condicional-real", "condicional-irreal", "se-impersonal-pasivo", "voz-pasiva",
        "comparativos", "superlativos", "adverbios-mente",
        "desencadenantes-subjuntivo", "subjuntivo-vs-indicativo")},
    **{s: "Verbos y contrastes" for s in (
        "ser-vs-estar", "estar-vs-hay", "saber-vs-conocer", "pedir-vs-preguntar",
        "ir-vs-venir", "llevar-vs-traer", "quedar-vs-quedarse", "verbos-tipo-gustar",
        "verbos-reflexivos", "obligacion", "acabar-de", "perifrasis-verbales",
        "estar-participio", "futuro-de-probabilidad")},
    **{s: "Sustantivos y adjetivos" for s in (
        "genero-y-numero", "articulos", "concordancia-adjetivo", "demostrativos",
        "posesivos", "apocope", "muy-vs-mucho")},
    **{s: "Pronombres" for s in (
        "pronombres-od", "pronombres-oi", "combinacion-pronombres", "tuteo-vs-usted",
        "vosotros-vs-ustedes", "a-personal")},
    **{s: "Preposiciones" for s in (
        "por-vs-para", "preposiciones-a-en-de", "desde-hace-durante", "ya-vs-todavia")},
    **{s: "Tiempos" for s in ("indefinido-vs-perfecto", "indefinido-vs-imperfecto",
                              "perfecto-subjuntivo")},
}
CLUSTER_TENSE_LABEL = "Tiempos"
CLUSTER_PATTERN_LABEL = "Conjugación"
CLUSTER_OTHER_LABEL = "Otros"

# --------------------------------------------------------------------- Drill-Maps (Practicar)
PATTERN_TENSE = {
    "stem-change-e-ie": "presente", "stem-change-o-ue": "presente", "stem-change-e-i": "presente",
    "g-verbs": "presente", "zc-verbs": "presente", "y-verbs": "presente",
    "irregular-indefinido": "indefinido", "irregular-futuro": "futuro",
    "irregular-participio": "participio", "irregular-imperativo": "imperativo",
    "presente-indicativo": "presente", "indefinido": "indefinido", "imperfecto": "imperfecto",
    "futuro-simple": "futuro", "condicional-simple": "condicional",
    "subjuntivo-presente": "subjuntivo_presente",
    "indefinido-vs-perfecto": "indefinido", "perfecto": "participio",
}
TENSE_LABEL = {
    "presente": "presente", "indefinido": "indefinido", "imperfecto": "imperfecto",
    "futuro": "futuro", "condicional": "condicional",
    "subjuntivo_presente": "subjuntivo presente", "imperativo": "imperativo",
    "participio": "participio", "gerundio": "gerundio",
}
DEFAULT_DRILL_TENSE_SLUG = "presente-indicativo"
STEM_CHANGE_PREFIX = "stem-change"

# --------------------------------------------------------------------- Onboarding
ONBOARDING_QUESTIONS: list[dict] = [
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
    {"id": "b1-perfecto", "band": "B1", "concept": "indefinido-vs-perfecto",
     "q": "Ayer ___ a la playa.",
     "options": ["he ido", "fui", "iba"], "correct": 1},
    {"id": "b1-porpara", "band": "B1", "concept": "por-vs-para",
     "q": "Este regalo es ___ ti.",
     "options": ["por", "para", "a"], "correct": 1},
    {"id": "b1-subjuntivo", "band": "B1", "concept": "desencadenantes-subjuntivo",
     "q": "Quiero que ___ a la fiesta.",
     "options": ["vienes", "vengas", "venir"], "correct": 1},
    {"id": "b2-irreal", "band": "B2", "concept": "condicional-irreal",
     "q": "Si tuviera más dinero, ___ un piso más grande.",
     "options": ["compraría", "compraré", "compraba"], "correct": 0},
]

# Kickoff-Präfix für "nueva situación" aus der Vocabulario-Seite
BRIEF_PREFIX = "prepárame para"
ONBOARDING_CAPTURE_TEXT = "test de nivel inicial"

# --------------------------------------------------------------------- Personen (Konjugation)
PERSONS = ["yo", "tu", "el", "nosotros", "vosotros", "ellos"]
PERSON_LABEL = {"yo": "yo", "tu": "tú", "el": "él/ella", "nosotros": "nosotros",
                "vosotros": "vosotros", "ellos": "ellos/ellas", "usted": "usted"}
STEM_UNSTRESSED = ("nosotros", "vosotros")  # Stammwechsel trifft nur betonte Formen
