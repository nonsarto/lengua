-- Interaktive Übungen pro Grammatik-Kapitel (Scheibe: Übungs-Runner).
-- Generierung ist LLM-Arbeit (analyze.py-Seam), Bewertung ist DETERMINISTISCH und
-- bewegt die concept_state-Counter wie echte Captures (success/error).
-- Auf BEIDEN Instanzen ausführen (lengua/es UND llengua/ca).

create table if not exists concept_exercises (
  id          uuid primary key default gen_random_uuid(),
  concept_id  uuid not null references concepts(id),
  etype       text not null check (etype in ('mcq', 'cloze')),
  prompt      text not null,          -- Aufgabe; cloze mit ___ als Lücke
  options     jsonb,                  -- mcq: Antwortoptionen; cloze: null
  answers     jsonb not null,         -- akzeptierte Antworten (mcq: der korrekte Optionstext)
  explanation text not null,          -- EIN deutscher Satz warum
  cefr        text,
  created_at  timestamptz not null default now()
);
create index if not exists concept_exercises_concept_idx on concept_exercises (concept_id);

create table if not exists exercise_attempts (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references user_settings(user_id),
  exercise_id uuid not null references concept_exercises(id),
  correct     boolean not null,
  answered_at timestamptz not null default now()
);
create index if not exists exercise_attempts_user_idx on exercise_attempts (user_id, exercise_id);

alter table concept_exercises enable row level security;
alter table exercise_attempts enable row level security;
