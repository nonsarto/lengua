-- Capture-Detailansicht: die VOLLE analyze()-Ausgabe pro Capture aufheben, damit die
-- Historie anklickbar wird und Korrektur/Erklärung/Konzepte/Vokabeln zeigt — nicht nur die
-- Mikro-Dosis. Alt-Einträge bleiben null; ihre Detailansicht wird aus corrections/
-- concept_evidence/vocab_items rekonstruiert (das, was vorhanden ist).
-- Auf BEIDEN Instanzen ausführen (lengua/es UND llengua/ca).
alter table captures add column if not exists analysis jsonb;
