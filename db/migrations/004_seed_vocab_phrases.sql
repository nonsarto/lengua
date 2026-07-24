-- Standardformulierungen im Grundwortschatz: seed_vocab lernt Phrasen kennen.
-- is_phrase fließt beim Promoten als Tag "frase" ins persönliche SRS (Practicar-Modus
-- "frases" zieht darauf); note trägt die wörtliche Glosse / Gebrauchsnotiz für Idiome.
-- Auf BEIDEN Instanzen ausführen (lengua/es UND llengua/ca), bevor der nächste
-- Backend-Deploy rausgeht.
alter table seed_vocab add column if not exists is_phrase boolean not null default false;
alter table seed_vocab add column if not exists note text;
