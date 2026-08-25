-- Upload von Lernmaterial: der fünfte Eingang. Ein hochgeladenes Dokument ist FREMDES,
-- redigiertes Material, keine persönliche Evidenz — es sagt nicht "das kann ich nicht",
-- sondern "das ist gerade mein Thema". Darum erzeugt es keinen need_count, sondern einen
-- relevance_boost auf die berührten Konzepte (dieselbe Mechanik wie ein Termin-Boost, nur
-- länger). Das Dokument selbst wird als QUELLE festgehalten, damit später nachvollziehbar
-- ist, woher ein Boost oder eine importierte Vokabel kam.
-- Auf BEIDEN Instanzen ausführen (lengua/es UND llengua/ca).
create table if not exists documents (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references user_settings(user_id),
  filename      text,
  kind          text not null,             -- pdf | image | text | csv
  mode          text not null,             -- grammar | vocab | both (vom Nutzer bestätigt)
  concept_slugs text[] not null default '{}',  -- welche Konzepte geboostet wurden (Herkunft)
  vocab_count   int not null default 0,        -- wie viele Vokabeln übernommen wurden
  created_at    timestamptz not null default now()
);
create index if not exists documents_user_idx on documents (user_id, created_at desc);
alter table documents enable row level security;

-- Herkunft am Vokabel-Item: aus welchem Dokument stammt es (für Nachvollziehbarkeit).
-- Bleibt null bei Capture-/Seed-/CSV-Herkunft; source (Migration 010) bleibt die grobe Achse.
alter table vocab_items add column if not exists source_document_id uuid references documents(id);
