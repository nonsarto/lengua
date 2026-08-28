-- 017 · Temario: der browsbare Grammatik-Katalog (A1-B2).
-- Zwei geteilte Tabellen ohne Lernstand: grammar_topics (das Curriculum, kuratierter Code
-- wie die Konzept-Slugs) und grammar_lessons (LLM-generierte Lektionen als typisierte
-- Blöcke, Review-Gate über `reviewed`). Der Status pro Thema kommt NIE von hier — er wird
-- im Backend aus concept_state über concept_slug gejoint (Connect Layer, einzige Wahrheit).
--
-- Befüllung: backend/app/grammar_catalog.py (generate → push → approve).

create type grammar_level as enum ('A1', 'A2', 'B1', 'B2');

create table grammar_topics (
  id             uuid primary key default gen_random_uuid(),
  slug           text not null unique,
  level          grammar_level not null,
  title_es       text not null,             -- "Presente de Indicativo I"
  subtitle_de    text,                      -- "Regelmäßige Verben im Präsens"
  order_index    int not null,              -- Reihenfolge innerhalb des Niveaus
  hero_image_url text,                      -- nice-to-have, Runde zwei
  -- Slug statt uuid als FK: Slugs sind die stabilen Identitäten des Konzept-Rückgrats
  -- (goldene Regel #3), und der Seed bleibt so pure, gegenlesbare Daten.
  -- Nullable: nicht jedes Thema hat ein Konzept (Acentuación, Conjunciones ...).
  concept_slug   text references concepts(slug),
  created_at     timestamptz not null default now()
);

create unique index grammar_topics_level_order_idx
  on grammar_topics (level, order_index);

create table grammar_lessons (
  id            uuid primary key default gen_random_uuid(),
  topic_id      uuid not null references grammar_topics(id) on delete cascade,
  version       int not null default 1,
  blocks        jsonb not null,             -- Block[] — Schema in grammar_catalog.py
  reviewed      boolean not null default false,  -- Gate: unreviewte Lektionen sind unsichtbar
  generated_at  timestamptz not null default now(),
  unique (topic_id, version)
);

create index grammar_lessons_topic_idx on grammar_lessons (topic_id, version desc);

-- RLS wie überall: an, ohne Policies. Der Browser spricht nie mit Supabase — nur das
-- Backend liest (Service-Key), und dessen Query filtert reviewed=true (Review-Gate).
alter table grammar_topics  enable row level security;
alter table grammar_lessons enable row level security;
