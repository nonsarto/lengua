-- 016_llm_usage.sql — Verbrauchs-Log pro LLM-Aufruf, Grundlage fürs Admin-Dashboard
-- (Perfil → panel de uso). Webapp-Backend (source 'web') und Speaking-Bot (source 'bot')
-- schreiben per Service-Key; gelesen wird nur vom /admin/stats-Endpoint.
-- RLS an, keine Policies (Konvention). Logging ist best-effort: fehlt die Tabelle,
-- loggen Backend/Bot einen Fehler und der Request läuft normal weiter.
-- Jetzt auf der es-Instanz (lengua) ausführen; llengua/ca folgt im eigenen ca-Durchgang.

create table if not exists llm_usage (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid references user_settings(user_id) on delete cascade,  -- null = kein Nutzerbezug
  source        text not null check (source in ('web', 'bot')),
  kind          text not null,   -- Call-Site, z.B. analyze/micro/document/chapter/exercises/
                                 -- listening/chat/transcribe (web) bzw. analysis/questions/transcribe (bot)
  model         text not null,
  input_tokens  integer not null default 0,
  output_tokens integer not null default 0,
  cache_read_tokens  integer not null default 0,
  cache_write_tokens integer not null default 0,
  audio_seconds integer not null default 0,  -- Transkription: Audiolänge in Sekunden
  created_at    timestamptz not null default now()
);

create index if not exists llm_usage_user_created_idx on llm_usage (user_id, created_at desc);
create index if not exists llm_usage_created_idx on llm_usage (created_at desc);

alter table llm_usage enable row level security;
