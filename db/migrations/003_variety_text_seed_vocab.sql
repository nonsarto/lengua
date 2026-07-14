-- Für die BESTEHENDE lengua-Instanz (Spanisch), damit sie mit schema.sql übereinstimmt.
-- Neue Instanzen (llengua) bekommen das direkt über db/schema.sql.
-- 1) Varietät von enum auf text (sprachneutral):
alter table user_settings alter column production_variety type text
  using production_variety::text;
alter table user_settings alter column production_variety set default 'peninsular';
drop type if exists variety_t;

-- 2) Grundwortschatz-Tabelle (bei lengua vorerst leer — die Mechanik ist inaktiv,
--    solange keine Zeilen drin sind):
create table if not exists seed_vocab (
  id          uuid primary key default gen_random_uuid(),
  term        text unique not null,
  translation text not null,
  register    register_t not null default 'neutral',
  topic       text not null,
  freq_rank   int not null,
  cefr        text,
  reviewed    boolean not null default false,
  created_at  timestamptz not null default now()
);
create index if not exists seed_vocab_topic_idx on seed_vocab (topic);
create index if not exists seed_vocab_freq_idx on seed_vocab (freq_rank);
alter table seed_vocab enable row level security;
