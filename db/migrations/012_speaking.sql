-- Speaking Bot (Produktion): Telegram-Bot stellt abends 3 Fragen, Antworten kommen als
-- Sprachnachricht, werden transkribiert (Code-Switching bleibt erhalten), von Claude
-- analysiert und hier abgelegt. Der Bot (lengua-bot, Railway) schreibt per Service-Key;
-- das lengua-Backend liest für den Hablar-Reiter. RLS an, keine Policies (Konvention).
-- Bewusst GETRENNT vom Connect Layer — Merge-Entscheidung erst nach zwei Wochen Daten.
-- NUR auf der es-Instanz (lengua) ausführen — Feature ist ES-only, NICHT auf llengua/ca.

-- Eine Zeile pro beantworteter Sprachnachricht. question_no/category/question_es sind
-- nullable: Antworten ohne offenes Fragen-Set (oder eine 4. Nachricht) werden als
-- "respuesta libre" gespeichert statt abgelehnt.
create table if not exists speaking_sessions (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references user_settings(user_id),
  created_at    timestamptz not null default now(),
  question_no   smallint check (question_no is null or question_no between 1 and 3),
  category      text check (category is null or category in ('narrar', 'opinar', 'trabajo')),
  question_es   text,
  audio_url     text,                    -- bucket-relativer Pfad in speaking-audio (privat), kein voller URL
  duration_sec  integer,
  transcript    text not null,
  transcript_corrected text,             -- null, wenn die Analyse fehlschlug (Fallback ohne Analyse)
  low_conf_spans jsonb not null default '[]'::jsonb  -- Form modellabhängig, trägt "model"-Key
);
create index if not exists speaking_sessions_user_idx on speaking_sessions (user_id, created_at desc);

-- Quelle des error_type-Enums: lengua-bot/constants.py ERROR_TYPES.
-- Kopien synchron halten: dieses Check-Constraint + frontend/lib/strings.ts errorTypeLabels.
-- Der Bot clampt unbekannte Typen auf 'lexico', bevor sie hier ankommen.
create table if not exists error_log (
  id           uuid primary key default gen_random_uuid(),
  session_id   uuid not null references speaking_sessions(id) on delete cascade,
  user_id      uuid not null references user_settings(user_id),
  created_at   timestamptz not null default now(),
  error_type   text not null check (error_type in (
    'subjuntivo', 'ser_estar', 'indefinido_imperfecto', 'perifrasis',
    'preposicion', 'concordancia', 'genero', 'lexico',
    'orden_palabras', 'germanismo', 'registro', 'conector'
  )),
  original     text not null,
  corrected    text not null,
  explanation  text,
  char_start   integer,                  -- Offsets gegen das ORIGINAL-Transkript; null = Highlight entfällt
  char_end     integer
);
create index if not exists error_log_user_idx on error_log (user_id, created_at desc, error_type);
create index if not exists error_log_user_type_idx on error_log (user_id, error_type);

-- Chunks: deutsche Wörter aus dem Transkript mit spanischer Entsprechung plus umständlich
-- Umschriebenes mit idiomatischer Wendung. Kein SRS — nur erfasst und nach Status gefiltert.
-- activated = chunk_es tauchte in einem späteren Transkript auf; dropped = 14 Tage unbenutzt.
create table if not exists speaking_chunks (
  id           uuid primary key default gen_random_uuid(),
  session_id   uuid references speaking_sessions(id) on delete set null,
  user_id      uuid not null references user_settings(user_id),
  created_at   timestamptz not null default now(),
  chunk_es     text not null,
  example_es   text not null,
  trigger_de   text,
  status       text not null default 'open' check (status in ('open', 'activated', 'dropped')),
  activated_at timestamptz
);
create index if not exists speaking_chunks_user_status_idx on speaking_chunks (user_id, status);

-- Headlines für die opinar-Frage. Morgens per RSS gefüllt, älter als 3 Tage gelöscht. Kein LLM.
create table if not exists news_cache (
  id          uuid primary key default gen_random_uuid(),
  fetched_at  timestamptz not null default now(),
  headline    text not null,
  source      text,
  topic       text
);

-- Das abendliche Fragen-Set (restart-sicher statt Bot-State). answered = Liste der
-- beantworteten question_no; eingehende Antworten bekommen die niedrigste offene Nummer.
create table if not exists pending_questions (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references user_settings(user_id),
  question_date date not null,
  created_at    timestamptz not null default now(),
  questions     jsonb not null,          -- [{no, category, question_es}]
  answered      jsonb not null default '[]'::jsonb,  -- [1, 3]
  unique (user_id, question_date)
);

alter table speaking_sessions enable row level security;
alter table error_log enable row level security;
alter table speaking_chunks enable row level security;
alter table news_cache enable row level security;
alter table pending_questions enable row level security;
