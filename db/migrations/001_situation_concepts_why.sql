-- Brief-Prep verlinkt Grammatik-Kapitel mit einem Satz "warum hier" (PRODUCT.md).
-- Einmal im Supabase SQL Editor ausführen. Frische Installationen haben die Spalte
-- schon über db/schema.sql.
alter table situation_concepts add column if not exists why text;
