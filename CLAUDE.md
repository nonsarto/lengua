# CLAUDE.md — Betriebsanleitung für dieses Repo

Du (Claude Code) baust **lengua**, ein In-Country-Spanisch-Lerntool für einen Deutschen in
Barcelona. Lies immer zuerst `BUILD.md` — dort steht die Reihenfolge. Baue **genau die aktuelle
Scheibe und halt dann an.** Nicht vorausscaffolden.

## Was das Tool ist (in einem Satz)
Das Leben liefert den Content, die App zieht Struktur. Vier Capture-Modi (decode/check/brief/
listen) laufen durch EINE `analyze()`-Funktion und speisen zwei Speicher: Grammatik-Konzepte
(mit State/Scoring) und Vokabeln/Verben (mit SRS).

## Stack
FastAPI (Python 3.13) Backend · Next.js 15 + Tailwind Frontend, als PWA installierbar (einziger
Client) · Supabase (Frankfurt, RLS) · Claude API (analyze) · Railway (Backend) + Vercel (Frontend).
Kein Telegram. Produkt-/UX-Verhalten steht in `PRODUCT.md`.

## Goldene Regeln (nicht verletzen)
1. **Loop first.** Eine Scheibe nach der anderen aus BUILD.md. Jede läuft end-to-end an echten
   Daten, bevor die nächste beginnt. Keine Screens, bevor die Brain trägt.
2. **KI nur in `analyze()`.** Scoring, Promoting, State-Übergänge, Ranking sind DETERMINISTISCHER
   Code — nie ein LLM-Aufruf. Siehe die Naht in `backend/app/analyze.py`.
3. **Slugs sind stabil.** Konzept-Slugs (kebab-case) werden nie neu generiert oder umbenannt.
   `analyze()` schlägt Slugs vor; der Aufrufer gleicht gegen `concepts` ab (vorhandene
   wiederverwenden, neue mit `reviewed=false` anlegen). Ohne stabile Slugs bricht der Connect-Layer.
4. **Inhalt emergiert, Struktur wird verdient.** Die Tabellen-*Struktur* (schema.sql) steht.
   Welche Konzepte existieren, ist Seed-Arbeit mit menschlichem Review (`reviewed`-Flag). Keine
   fertige Ontologie erfinden.
5. **Grammatik verlinken, nie kopieren.** Situationen/Preps zeigen auf Konzept-Kapitel, sie
   duplizieren die Erklärung nicht. Das Konzept-Rückgrat ist die einzige Wahrheit.
6. **Region ist zweistufig.** Verstehen ist allesfressend (alle Varietäten gültig, nur getaggt).
   Produzieren folgt EINER gewählten Spur (`user_settings.production_variety`, Default peninsular).

## Wo was liegt
- `BUILD.md` — die Scheiben-Sequenz. Immer zuerst lesen.
- `db/schema.sql` — Datenmodell. In Supabase ausführen (Slice 1).
- `backend/app/analyze.py` — die Brain + die deterministische Naht.
- `.env` — Keys (nie committen; `.env.example` ist die Vorlage).

## Konventionen
- Python 3.13, venv, gepinnte Deps in `requirements.txt`.
- Secrets nur aus Umgebungsvariablen. Niemals Keys in Code oder Git.
- Kleine, überprüfbare Commits pro Scheibe.

## Wenn du eine Scheibe startest
Sag zuerst in einem Satz, welche Scheibe aus BUILD.md du baust und wann sie „fertig" ist.
Dann bau nur die. Danach halt an und lass den Menschen sie an echten Daten testen.
