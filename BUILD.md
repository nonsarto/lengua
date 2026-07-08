# lengua — Build-Sequenz (Web-App)

Prinzip: **dünne vertikale Scheiben.** Jede läuft end-to-end und beweist genau eine Sache.
Keine Scheibe startet, bevor die vorige an *echten* Daten läuft. Time-to-first-loop zählt.
Screens sind die Belohnung, nicht der Anfang.

## Stack (steht)
- Backend: FastAPI (Python 3.13) — hier lebt `analyze()`
- Frontend: Next.js 15 + Tailwind, als PWA installierbar (der einzige Client)
- DB/Auth: Supabase (Frankfurt), RLS von Anfang an
- KI: Claude API — eine zentrale `analyze()` (siehe backend/app/analyze.py)
- Deploy: Railway (Backend) + Vercel (Frontend) — wie TwentySix
- Dev: Claude Code (Fable 5)

UX-/Produktverhalten: siehe `PRODUCT.md`. Leitplanken: siehe `CLAUDE.md`.

---

## Slice 0 — die nackte Brain  ⟵ JETZT
Kein UI, keine DB. `analyze()` an 5 echten Barcelona-Schnipseln (CLI: `python run.py "..."`).
**Fertig, wenn:** die JSON-Ausgabe an *deinem* Input sauber & richtig getaggt ist.

## Slice 1 — Persistenz + Backend-Endpunkte
`schema.sql` in Supabase; FastAPI-Endpunkt `POST /capture` ruft `analyze()`, schreibt captures +
evidence + concept_state via `apply_analysis()`.
**Fertig, wenn:** ein Capture per API einen Zähler dreht, den du in der DB abfragen kannst.

## Slice 2 — seed_reference()
Konzept-Rückgrat: Liste am Inventar des *Plan Curricular del Instituto Cervantes* verankert,
Erklärungs-Text LLM-generiert (nicht kopiert), du liest gegen & frierst ein (`reviewed=true`).
~50–70 Konzepte inkl. Tempora + Muster-Familien; ~50–80 häufigste Irregulär-Verben.
**Fertig, wenn:** Slugs existieren und `analyze()` dagegen taggt statt neue zu erfinden.

## Slice 3 — die App-Hülle + Capturar (PWA)
Next.js-Grundgerüst, untere Navigation (Inicio/Gramática/Vocabulario/Practicar) + Capturar als
persistente Aktion. Capturar = eine Fläche, vier Anlässe (Text/Foto/Sprache/jemand-anderes),
Modus wird nach dem Einwurf erkannt (kein Vorab-Menü), Mikro-Dosis-Antwort + stilles Ablegen.
Foto → Claude-Vision direkt (kein extra OCR). Als PWA installierbar; deep-link `/capturar?mode=`.
**Fertig, wenn:** du auf dem iPhone-Homescreen installierst, etwas einwirfst, die Korrektur
kriegst, und es lautlos abgelegt wird. → Ab hier tägliche echte Nutzung.

## Slice 4 — Scoring + Promoting (deterministisch, kein LLM)
Need-Schwelle promotet, Success stuft zurück ab, Relevance-Boost mit Verfallsdatum getrennt.
**Fertig, wenn:** ein Konzept aus echten Captures den State wechselt.

## Slice 5 — Lese-Oberflächen
Inicio (Daily Briefing: en caliente / repasar / prep) + Gramática-Kapitel (Körper + Mantel,
Liste per Score sortiert).
**Fertig, wenn:** du morgens aufmachst und in 3 Sekunden siehst, was heute dran ist.

## Slice 6 — Practicar
Drei Drill-Typen aus einem Store: Vokabel-Recall (SRS), Konzept-Anwendung (Übung aus deinen
Fehlern), Konjugations-Drill.
**Fertig, wenn:** der Drill genau die Items zieht, bei denen dein Scoring wackelt.

## Slice 7 — Vocabulario nach Situation + Brief-Generator
Situationen als Regale (Seed-Expat + Tuyas), "nueva situación", Brief-Prep-Paket
(Vokabel + Grammatik-*Links*, nie kopierte Grammatik; befristeter Boost auf die Konzepte).
**Fertig, wenn:** "prepárame para X" ein Paket erzeugt und passende Kapitel pusht.

## Geparkt (verdienen sich später)
- Sprach-Transkription für den "jemand spricht"-Modus (Whisper o.ä.) — erst wenn der Textkern steht
- Aussprache-Prüfung (fremder Speech-Stack, v2+)
- Native iOS-Hülle + WidgetKit-Widget + Capture-App-Intent
  — bis dahin: Apple Shortcut → URL `…/capturar?mode=camera`, null Swift

## Die eine Regel
Jede weitere Struktur-Schicht muss sich durch echte Daten verdienen. Erst der Loop, dann die Ontologie.
