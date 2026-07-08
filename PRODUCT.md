# PRODUCT.md — was die App ist und wie sie sich verhält

UI-Sprache: **Spanisch** (Immersion — sogar die Chrome ist Übung). Zielnutzer: ein Deutscher in
Barcelona. Diese Datei beschreibt Verhalten, nicht Code. Datenmodell: `schema.sql`. Regeln: `CLAUDE.md`.

## Prinzip
Das Leben liefert den Content, die App zieht Struktur. Kein Curriculum, das man von A1 durcharbeitet,
sondern ein Werkzeug, das einfängt, was einem im echten Alltag begegnet, und daraus Lernen baut.

## Vier Orte + eine Geste
Untere Navigation = vier ORTE, an denen angesammeltes Lernen wohnt. Capturar = eine persistente
AKTION in der Mitte, von jedem Screen erreichbar. Die vier Capture-Anlässe sind KEINE vier Tabs.

- **Inicio** — der Puls. Drei Bänder: *en caliente* (frisch promotete Konzepte), *para repasar*
  (SRS-fällig), *prep para hoy* (Brief-Prep für Termine heute). In 3 Sekunden weiß man, was dran ist.
- **Gramática** — Kapitel-Liste, sortiert per Score (heiße oben, gemeisterte sinken ins Ruhige).
- **Vocabulario** — nach Situation gegliedert (Regale), nicht flache Wortliste.
- **Practicar** — Drill-Sessions.
- **Capturar** — die eine Geste (s.u.).

## Capturar (das Herzstück)
Eine Eingabefläche, drei Modi (Teclado / Voz / Cámara) + der "jemand spricht"-Fall.
Vier reale Anlässe fließen durch DIESELBE `analyze()`:
1. etwas, das du gesagt hast und überprüfen willst → **check**
2. ein Schild/Text, das du nicht verstehst → **decode**
3. ein Termin, auf den du dich vorbereitest ("prepárame para…") → **brief**
4. jemand anderes, den du nicht verstehst (Transkript) → **listen**

Regeln:
- **Kein Modus-Menü vor dem Einfangen.** Der Nutzer wirft rein; `analyze()` erkennt den Modus danach.
  Reibung beim Einfangen ist der Feind (der Bar-Moment).
- **Ergebnis = Mikro-Dosis, dann Stopp.** Korrektur + ein Satz warum, fertig. KEINE volle Lektion
  ins Gesicht. Ein leiser Ausgang "→ ver lección" ist ein Angebot, kein Zwang.
- **Stilles Ablegen.** Zähler drehen, Evidenz verknüpfen, Konzept aktualisieren — alles unsichtbar.
  Erst wenn Need später die Schwelle reißt, taucht es auf Inicio ("en caliente") auf.
- Foto → Claude-Vision direkt. Sprache → später Transkription (v1: Text/Foto reichen).

## Gramática-Kapitel (zwei Schichten)
- **Geteilter Körper** (für alle gleich, geseedet & eingefroren): explanation, rule_of_thumb,
  german_pitfall, ggf. paradigm, default_exercises. Das ist das Nachschlagewerk.
- **Persönlicher Mantel** (nur du): deine Fehlersätze + aus ihnen generierte Übungen + State.
- Ein ruhiges Kapitel (nie Fehler gemacht) zeigt nur den Körper, ohne Badge — reines Nachschlagen.
- Ein promotetes Kapitel öffnet mit DEINEM Fehler ("das machst du dauernd falsch"), die Regel
  rutscht dahinter als Erklärung für dein Problem. Es steigt auch im Rang (Inicio, Listen-Top).
- **Auf UND ab.** Success drückt den State zurück Richtung *dominado*; ein gemeistertes Kapitel
  sinkt zurück ins ruhige Nachschlagewerk. Der Abstieg ist so wichtig wie der Aufstieg.

## Konzept-Zustände (spanische Labels)
`sin ver → visto → flojo → aprendiendo → dominado`
- decode/listen markieren vor allem **visto** (Begegnung/Exposition).
- check markiert **flojo/need** bei Fehler, **success** bei korrekt.

## Zwei Kräfte der Priorität (getrennt halten)
- **need** (aus Fehlern) — dauerhaft, bis gemeistert.
- **relevance_boost** (aus einer datierten Situation) — befristet, klingt nach dem Termin ab.
Priorität eines Kapitels = need_score + relevance_boost(mit Verfall). Nie vermischen.

## Vocabulario nach Situation
- Regale = Situationen. **Estándar** (endliche Expat-Menge, geseedet) + **Tuyas** (aus deinem
  Leben gewachsen, z.B. "fútbol y camisetas", "en la sidrería").
- "Nueva situación" erzeugt ein Regal on-demand (KI befüllt, getaggt, register-passend).
- Eine Situation ist eine Gruppierung über `vocab_items`, kein neues Objekt.

## Brief-Prep (Situation, die Vokabel UND Grammatik pusht)
Eingabe: eine beschriebene Situation ("mañana reunión sobre la reorganización").
Ausgabe: ein Paket aus drei Blöcken —
1. **Vocabulario clave** (neue + bekannte Items, register-getaggt)
2. **Frases con intención** (Vorschlagen / mit Takt widersprechen / Zeit gewinnen …)
3. **Grammatik, die das aktiviert** — LINKS auf bestehende Konzept-Kapitel + ein Satz "warum hier",
   plus ein befristeter relevance_boost. **Grammatik wird verlinkt, nie ins Prep kopiert.**
Vokabeln darf die Situation erzeugen & besitzen; Grammatik gehört immer dem Konzept-Rückgrat.
Nach dem Termin: "¿cómo fue?" → captura → Fehler werden zu need → nächstes Prep ist schärfer.

## Region (zweistufig)
- **Verstehen ist allesfressend:** alle Varietäten gültig, nur getaggt (cataluña/latam/asturias…).
  Nie eine korrekte regionale Form als Fehler markieren.
- **Produzieren folgt einer gewählten Spur:** `user_settings.production_variety`, Default
  **peninsular** (Barcelona). Steuert Generierung & Gewichtung, nicht das Verstehen.

## Practicar (drei Drill-Typen, ein Store)
1. Vokabel-Recall (SRS über vocab_items; Herkunft seedet die Startposition).
2. Konzept-Anwendung (generierte Übung aus deinen echten Fehlern — nicht generisch).
3. Konjugations-Drill (Verb + Tempus + Person → Form; aus wackligen Verben/Mustern).

## PWA
Installierbar auf dem iPhone-Homescreen; deep-link `/capturar?mode=camera|voz|texto`; ein Apple
Shortcut auf dem Action Button zeigt später einfach auf diese URL. Kamera/Mikro im Browser
brauchen einen Erlaubnis-Tap — Capture-Seite landet im Kamera-Modus mit großem Auslöser.
