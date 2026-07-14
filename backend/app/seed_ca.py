"""
seed_ca.py — Import des katalanischen Seeds (llengua) aus db/seed_ca/*.json.

Die Inhalte wurden in-Session geschrieben (keine API-Kosten) und liegen versioniert im
Repo. Dieses Skript ist reiner Transport: Dateien → Supabase. Menschliches Review bleibt
der Gate: push schreibt reviewed=false, approve friert ein.

Gegen die CA-Datenbank laufen lassen (Env-Variablen überschreiben die .env):
  SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... python seed_ca.py push
  python seed_ca.py review     # erzeugt SEED_REVIEW_CA.md (lokal, ohne DB)
  SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... python seed_ca.py approve
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")  # überschreibt NICHT bereits gesetzte Env-Variablen

SEED_DIR = ROOT / "db" / "seed_ca"
REVIEW_MD = ROOT / "SEED_REVIEW_CA.md"


def _load_concepts() -> dict:
    concepts: dict = {}
    for f in sorted(SEED_DIR.glob("concepts_*.json")):
        concepts.update(json.load(open(f)))
    return concepts


def _load_verbs() -> dict:
    verbs: dict = {}
    for f in sorted(SEED_DIR.glob("verbs_*.json")):
        verbs.update(json.load(open(f)))
    return verbs


def _load_words() -> list[dict]:
    """Flacht die Themen-Blöcke zu einer Rangliste ab; Duplikate zwischen Themen werden
    dedupliziert — die erste Nennung (frühere Datei = häufigeres Thema) gewinnt."""
    words, seen, rank = [], set(), 0
    for f in sorted(SEED_DIR.glob("words_*.json")):
        for block in json.load(open(f))["blocks"]:
            for entry in block["words"]:
                term, translation = entry[0], entry[1]
                register = entry[2] if len(entry) > 2 else "neutral"
                if term in seen:
                    continue
                seen.add(term)
                rank += 1
                words.append({"term": term, "translation": translation,
                              "register": register, "topic": block["topic"],
                              "freq_rank": rank})
    return words


def push() -> None:
    from db import get_db
    db = get_db()
    concepts, verbs, words = _load_concepts(), _load_verbs(), _load_words()

    for slug, it in concepts.items():
        db.c.table("concepts").upsert({
            "slug": slug, "label": it["label"], "ctype": it["ctype"], "cefr": it["cefr"],
            "explanation": it["explanation"], "rule_of_thumb": it["rule_of_thumb"],
            "german_pitfall": it["german_pitfall"], "paradigm": it["paradigm"],
            "default_exercises": it["default_exercises"],
            "member_verbs": it["member_verbs"] or None,
            "reviewed": False,
        }, on_conflict="slug").execute()
    print(f"Konzepte: {len(concepts)}")

    for rank, (inf, it) in enumerate(verbs.items(), start=1):
        db.c.table("verbs").upsert({
            "infinitive": inf, "translation": it["translation"], "cefr": it["cefr"],
            "freq_rank": rank, "pattern_tags": it["pattern_tags"],
            "conjugations": it["conjugations"],
            "irregularity_note": it["irregularity_note"],
            "reviewed": False,
        }, on_conflict="infinitive").execute()
    print(f"Verben: {len(verbs)}")

    for i in range(0, len(words), 200):  # Batch-Upserts, PostgREST-freundlich
        db.c.table("seed_vocab").upsert(words[i:i + 200], on_conflict="term").execute()
    print(f"Grundwortschatz: {len(words)} Wörter (dedupliziert)")
    print("Alles reviewed=false. Gegenlesen: python seed_ca.py review → SEED_REVIEW_CA.md")


def review() -> None:
    concepts, verbs, words = _load_concepts(), _load_verbs(), _load_words()
    lines = [
        "# SEED_REVIEW_CA — llengua: Rückgrat + Grundwortschatz zum Gegenlesen",
        "",
        "In-Session geschrieben, von dir eingefroren. Korrekturen direkt in `db/seed_ca/*.json`,",
        "dann nochmal `push`. Wenn alles stimmt: `python seed_ca.py approve`.",
        "",
        f"**{len(concepts)} Konzepte · {len(verbs)} Verben · {len(words)} Wörter**",
        "",
        "## Konzepte",
    ]
    for slug, it in concepts.items():
        lines += [
            f"### `{slug}` — {it['label']}  ({it['ctype']}, {it['cefr']})",
            f"**Explicació:** {it['explanation']}",
            f"**Regla d'or:** {it['rule_of_thumb']}",
            f"**⚠️ Deutsche Falle:** {it['german_pitfall']}",
        ]
        if it.get("paradigm"):
            lines.append("**Paradigma:** " + " · ".join(
                f"-{k}: {' / '.join(v.values())}" for k, v in it["paradigm"].items()))
        if it.get("member_verbs"):
            lines.append("**Verbs del patró:** " + ", ".join(it["member_verbs"]))
        for ex in it.get("default_exercises", []):
            lines.append(f"- _{ex['q']}_ → **{ex['a']}**")
        lines.append("")

    lines.append("## Verben")
    for inf, it in verbs.items():
        c = it["conjugations"]
        lines += [
            f"### `{inf}` — {it['translation']}  ({it['cefr']})",
            f"_{it['irregularity_note']}_ · patrons: {', '.join(it['pattern_tags']) or '—'}",
            f"- present: {' / '.join(c['present'].values())}",
            f"- imperfet: {' / '.join(c['imperfet'].values())}",
            f"- futur: {c['futur']['jo']}… · subj.: {c['subjuntiu_present']['jo']}…"
            f" · imperatiu tu: {c['imperatiu']['tu']}"
            f" · gerundi: {c['gerundi']} · participi: {c['participi']}",
            "",
        ]

    lines.append("## Grundwortschatz (nach Themen)")
    by_topic: dict[str, list] = {}
    for w in words:
        by_topic.setdefault(w["topic"], []).append(w)
    for topic, items in by_topic.items():
        lines += [f"### {topic} ({len(items)})", ""]
        for w in items:
            reg = f" _{w['register']}_" if w["register"] != "neutral" else ""
            lines.append(f"- **{w['term']}** — {w['translation']}{reg}")
        lines.append("")

    REVIEW_MD.write_text("\n".join(lines))
    print(f"Geschrieben: {REVIEW_MD} ({len(lines)} Zeilen)")


def approve() -> None:
    from db import get_db
    db = get_db()
    concepts, verbs = _load_concepts(), _load_verbs()
    db.c.table("concepts").update({"reviewed": True}).in_("slug", list(concepts)).execute()
    db.c.table("verbs").update({"reviewed": True}).in_("infinitive", list(verbs)).execute()
    db.c.table("seed_vocab").update({"reviewed": True}).neq("term", "").execute()
    print("Eingefroren: Konzepte + Verben + Grundwortschatz → reviewed=true.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "push":
        push()
    elif cmd == "review":
        review()
    elif cmd == "approve":
        approve()
    else:
        sys.exit(__doc__)
