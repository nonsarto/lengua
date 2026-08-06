-- Tägliche Session: der eingefrorene 15-Minuten-Bogen (Einstieg → ein Grammatikkern →
-- Ausklang). Eine Zeile pro (Nutzer, Tag). Der PLAN wird beim ersten Öffnen des Tages
-- generiert und friert ein — er ändert sich nicht mehr (außer completed oder aktivem
-- "Session ändern"/reroll). Fortschritt (cursor + progress) macht Abbruch/Fortsetzen möglich.
-- Der Generator ist deterministischer Code; Bewertung läuft über die BESTEHENDEN Pfade
-- (SRS bzw. Übungs-Grading), damit sich Lernstand exakt wie bisher bewegt.
-- Auf BEIDEN Instanzen ausführen (lengua/es UND llengua/ca).

create table if not exists daily_sessions (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references user_settings(user_id),
  session_date   date not null,
  plan           jsonb not null,          -- die eingefrorene Item-Liste (der Bauplan)
  headline       text not null,           -- Inhalt für den Knopf ("Vocabulario + ...")
  budget_seconds int not null default 900,
  cursor         int not null default 0,  -- nächstes offenes Item (Fortsetzen)
  progress       jsonb not null default '[]',  -- pro erledigtem Item: {index, correct?}
  status         text not null default 'active' check (status in ('active', 'completed')),
  created_at     timestamptz not null default now(),
  completed_at   timestamptz,
  unique (user_id, session_date)
);
create index if not exists daily_sessions_user_idx on daily_sessions (user_id, session_date desc);

alter table daily_sessions enable row level security;
