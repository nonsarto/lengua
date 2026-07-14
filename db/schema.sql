-- lengua · schema v0
-- Single-user for now (you), but user_id is carried everywhere so multi-user is a
-- later switch, not a rewrite. Enable RLS on every table before it ever leaves your device.
-- Structure is stable to commit; the CONTENT (which concepts exist) is what emerges & gets reviewed.

create extension if not exists "pgcrypto";

-- ---------- enums ----------
create type capture_kind   as enum ('decode', 'check', 'brief', 'listen');
-- '_t' suffix: a table named concept_state exists below, and Postgres gives every table an
-- implicit composite type of the same name — an enum called plain 'concept_state' collides.
create type concept_state_t as enum ('sin_ver', 'visto', 'flojo', 'aprendiendo', 'dominado');
create type concept_type   as enum ('grammar', 'tense', 'pattern_family');
create type evidence_kind  as enum ('encounter', 'error', 'success');
create type register_t     as enum ('formal', 'neutral', 'coloquial');
create type variety_t      as enum ('peninsular', 'latam');

-- ---------- user settings ----------
-- The production variety is a CHOICE, not an assumption. Comprehension stays omnivorous;
-- generation & scoring lean on this one lane. Barcelona -> peninsular default.
create table user_settings (
  user_id           uuid primary key default gen_random_uuid(),
  production_variety variety_t not null default 'peninsular',
  home_region       text default 'cataluña',
  created_at        timestamptz not null default now()
);

-- ---------- captures (layer 2: the evidence text) ----------
-- Blob (photo/audio) is dropped after analysis; raw_text is kept — cheap, and the
-- raw material for re-analysis when analyze() gets better later.
create table captures (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references user_settings(user_id),
  raw_text    text not null,
  kind        capture_kind not null,
  blob_url    text,                       -- nullable, normally null
  source      text default 'telegram',    -- telegram | web | shortcut | ...
  created_at  timestamptz not null default now()
);

-- ---------- concepts (grammar backbone: has STATE, gets promoted) ----------
-- Covers grammar concepts, tenses, and pattern-families — all promotable.
-- slug is the STABLE identity analyze() tags against. Never regenerate slugs.
-- The static "body" (explanation/rule/pitfall/paradigm) is the reference/Nachschlagewerk,
-- seeded once & frozen. The personal "mantle" lives in concept_state + concept_evidence.
create table concepts (
  id               uuid primary key default gen_random_uuid(),
  slug             text unique not null,        -- e.g. 'ser-vs-estar', 'stem-change-e-ie'
  label            text not null,               -- human label, UI in Spanish
  ctype            concept_type not null default 'grammar',
  cefr             text,                          -- nullable: 'A1' ... 'B2' (priority hint only)
  explanation      text,
  rule_of_thumb    text,
  german_pitfall   text,                          -- the contrastive note — your real edge, LLM-authored
  paradigm         jsonb,                         -- for tenses: the regular conjugation table
  default_exercises jsonb,                        -- generic cold-start exercises (fallback, not the goal)
  member_verbs     text[],                        -- for pattern_family concepts
  reviewed         boolean not null default false, -- flip true after you eyeball the seed
  created_at       timestamptz not null default now()
);

-- ---------- concept_state (your progress per concept) ----------
-- Priority = need_score (durable, from errors) + relevance_boost (temporary, from dated situations).
-- Keep the two forces separate: the boost expires, the need does not until you master it.
create table concept_state (
  id               uuid primary key default gen_random_uuid(),
  user_id          uuid not null references user_settings(user_id),
  concept_id       uuid not null references concepts(id),
  need_count       int not null default 0,
  success_count    int not null default 0,
  state            concept_state_t not null default 'sin_ver',
  relevance_boost  int not null default 0,
  boost_expires_at timestamptz,                    -- after a situation's date passes, boost decays
  last_seen        timestamptz,
  updated_at       timestamptz not null default now(),
  unique (user_id, concept_id)
);

-- ---------- concept_evidence (every counter points at its evidence — never free-floating) ----------
create table concept_evidence (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references user_settings(user_id),
  concept_id  uuid not null references concepts(id),
  capture_id  uuid not null references captures(id),
  kind        evidence_kind not null,
  created_at  timestamptz not null default now()
);

-- ---------- corrections (the explicit wrong->right from a check) ----------
create table corrections (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references user_settings(user_id),
  capture_id  uuid not null references captures(id),
  wrong       text not null,
  correct     text not null,
  concept_id  uuid references concepts(id),
  created_at  timestamptz not null default now()
);

-- ---------- situations (a grouping/lens over vocab + concepts, not a new object) ----------
create table situations (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references user_settings(user_id),
  name        text not null,
  is_seed     boolean not null default false,   -- the finite expat cold-start set
  region      text,
  created_at  timestamptz not null default now()
);

-- ---------- vocab_items (atomic, SRS-scheduled; one store for words AND brief-phrases) ----------
-- source_capture_id SEEDS the initial SRS position: a word from a check (you produced it) starts
-- warmer than a word from a decode (brand new).
create table vocab_items (
  id                uuid primary key default gen_random_uuid(),
  user_id           uuid not null references user_settings(user_id),
  term              text not null,
  translation       text not null,
  register          register_t not null default 'neutral',
  region            text,                          -- 'cataluña','latam','asturias',...
  tags              text[] default '{}',
  situation_id      uuid references situations(id),
  source_capture_id uuid references captures(id),
  srs_due           timestamptz not null default now(),
  srs_interval_days int not null default 0,
  srs_ease          real not null default 2.5,
  srs_reps          int not null default 0,
  created_at        timestamptz not null default now()
);

-- ---------- verbs (the 3rd object type: morphology — part vocab, part pattern) ----------
-- Seed only the ~50-80 most frequent irregulars. Regular verbs are conjugated on the fly
-- from a tense concept's paradigm — no need to store them.
create table verbs (
  id                uuid primary key default gen_random_uuid(),
  infinitive        text unique not null,
  translation       text not null,
  cefr              text,
  freq_rank         int,
  pattern_tags      text[] default '{}',   -- -> slugs of pattern_family concepts (e.g. g-verbs, stem-change-e-ie)
  conjugations      jsonb not null,         -- { "presente": {...}, "indefinido": {...}, ... }
  irregularity_note text,
  reviewed          boolean not null default false,
  created_at        timestamptz not null default now()
);

-- ---------- join tables ----------
create table situation_vocab (
  situation_id uuid not null references situations(id),
  vocab_item_id uuid not null references vocab_items(id),
  primary key (situation_id, vocab_item_id)
);

create table situation_concepts (
  situation_id uuid not null references situations(id),
  concept_id   uuid not null references concepts(id),
  primary key (situation_id, concept_id)
);

-- ---------- indexes that matter ----------
create index on captures (user_id, created_at desc);
create index on concept_state (user_id, state);
create index on vocab_items (user_id, srs_due);
create index on concept_evidence (concept_id);

-- ---------- RLS (on from day one — CLAUDE.md golden rule) ----------
-- The backend writes with the service role key (bypasses RLS); the browser never talks to
-- Supabase directly. No anon policies exist, so with RLS enabled the anon key can read NOTHING.
-- When real multi-user auth arrives, add policies like: using (user_id = auth.uid()).
alter table user_settings      enable row level security;
alter table captures           enable row level security;
alter table concepts           enable row level security;
alter table concept_state      enable row level security;
alter table concept_evidence   enable row level security;
alter table corrections        enable row level security;
alter table situations         enable row level security;
alter table vocab_items        enable row level security;
alter table verbs              enable row level security;
alter table situation_vocab    enable row level security;
alter table situation_concepts enable row level security;
