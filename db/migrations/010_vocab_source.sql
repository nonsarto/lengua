-- Herkunft eines Vokabel-Items explizit machen. Bisher war die Quelle nur implizit
-- ableitbar (source_capture_id gesetzt = aus Capture, Tag 'seed' = Grundwortschatz).
-- Der Upload-Eingang bringt eine dritte Herkunft (Import) ins Spiel, und der
-- Session-Generator muss nach Herkunft gewichten (selbst eingefangen VOR importiert).
-- Darum: eine benannte, nachvollziehbare Spalte statt Heuristik zur Laufzeit.
--   'capture' = aus einer eigenen Capture (Default, dein persönlicher Vorsprung)
--   'seed'    = Grundwortschatz, automatisch nachgerückt (geteilt, kein Vorsprung)
--   'import'  = per Datei hochgeladen (fremdes Material, startet kalt)
-- Auf BEIDEN Instanzen ausführen (lengua/es UND llengua/ca).
alter table vocab_items add column if not exists source text not null default 'capture';

-- Bestandszeilen rückwirkend einordnen: Grundwortschatz-Wörter tragen den Tag 'seed'.
update vocab_items set source = 'seed'
  where source = 'capture' and 'seed' = any(tags);

create index if not exists vocab_items_user_source_idx on vocab_items (user_id, source);
