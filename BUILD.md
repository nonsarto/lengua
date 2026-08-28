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

## Slice 0 — die nackte Brain
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

## Slice 8 — Capturar antwortet sofort
Die Mikro-Dosis geht direkt nach `analyze()` raus; `create_capture` + `apply_analysis` laufen
als Background-Task nach (capture_id vorab als uuid4). Briefs bleiben synchron — der
Paket-Link braucht die Situation-ID.
**Fertig, wenn:** die gefühlte Wartezeit nur noch der LLM-Call ist, nicht die DB-Writes.

## Slice 9 — Grundwortschatz + Standardformulierungen (es)
`seed_vocab` gefüllt: 12 Themen, ~740 Einträge, davon ~190 Formulierungen (💬, mit wörtlicher
Glosse — *me pones*, *tengo 34 años*, *hace calor*). `is_phrase`/`note` (Migration 004);
Phrasen fließen beim Promoten als Tag `frase` ins SRS → Practicar-Modus "frases".
Inhalte in-Session geschrieben, Review-Gate: `SEED_REVIEW_WORDS.md` → `approve-words`.
**Fertig, wenn:** das Diccionario browsbar ist und täglich Wörter ins Repaso nachrücken.

## Slice 10 — Word-Lookup in Capturar
Einzelwort (es ODER de) → `analyze()` erkennt Modus `word` (Migration 005): Wörterbucheintrag
als Mikro-Dosis + Übernahme ins Vokabular, mit Dedup-Check ("ya en tu vocabulario").
**Fertig, wenn:** "Rechnung" eintippen *la cuenta* liefert und im Vokabular landet — einmal.

## Slice 11 — Gramática interaktiv: Ejercicios + Dudas
Pro Kapitel ein Übungs-Runner (mcq + cloze, Migration 006): Generierung ist LLM-Seam
(`generate_exercises`, Distraktoren = deutsche Interferenz-Fehler), Auswahl/Grading/State
sind CODE — Ergebnisse zählen wie Capture-Evidenz (Akzente signifikant). Dazu die Dudas-Box:
Klärungsfragen-Chat (`answer_concept_question`, dritter LLM-Seam), gegroundet in Kapitel +
eigenen Fehlern, antwortet deutsch, bewegt NIE Lernstand.
**Fertig, wenn:** ein Kapitel sich durch Üben promoten/abstufen lässt und Nachfragen sitzt.

## Slice 12 — Voz: Sprach-Transkription
🎤 in Capturar (MediaRecorder, webm/mp4) + `?mode=voz`-Deep-Link. `transcribe()` in analyze.py
(gpt-4o-transcribe, language=es) — danach ist das Transkript eine normale Capture, ein
Trichter. UI zeigt "escuché: …" zur Kontrolle. Braucht `OPENAI_API_KEY`.
**Fertig, wenn:** Overheard-Spanisch als Aufnahme reingeht und als listen-Capture rauskommt.

## Slice 13 — Temario: der Grammatik-Katalog (A1-B2)
Browsbarer Katalog aller Grammatikthemen nach Niveau (Migration 017): 39 kuratierte Topics
(`grammar_catalog.py`), pro Thema eine Lektion aus typisierten Blöcken (Erklärung deutsch,
Konjugationstabellen mit Personenspalte, Verwendungsfälle, „häufigster Fehler"-Note).
Generierung LLM (Opus, Structured Output), Review-Gate über `reviewed` (generate → push →
Gegenlesen GRAMMAR_REVIEW.md → approve). Status pro Thema aus dem Connect Layer via
`concept_slug` — der Katalog verlinkt Kapitel, kopiert nie Lernstand. UI: `/gramatica/temario`
(Sections pro Niveau + StateDots) und `/gramatica/temario/[slug]` (Block-Renderer mit
horizontal scrollbaren Tabellen, sticky Personenspalte).
**Fertig, wenn:** alle 39 Lektionen gegengelesen live sind und ein Thema, das dir in Captures
schon begegnet ist, im Katalog seinen Status zeigt.

## Nachzug llengua (ca) — eigener Durchgang, NICHT nebenbei
Slices 8–12 sind nur auf **lengua (es)** live. Für llengua: Migrationen 004–006 auf der
ca-DB ausführen, ca-Strings/Prompts gegenlesen (Grundgerüst liegt schon in `lang/ca.py` +
`strings.ts`), ca-Grundwortschatz-Phrasen ergänzen, dann `deploy-llengua.sh`.

## Geparkt (verdienen sich später)
- Aussprache-Prüfung (fremder Speech-Stack, v2+)
- Native iOS-Hülle + WidgetKit-Widget + Capture-App-Intent
  — bis dahin: Apple Shortcut → URL `…/capturar?mode=camera|voz`, null Swift

## Die eine Regel
Jede weitere Struktur-Schicht muss sich durch echte Daten verdienen. Erst der Loop, dann die Ontologie.
