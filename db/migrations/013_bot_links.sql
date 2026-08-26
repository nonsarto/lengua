-- Speaking Bot, Multi-User-Pivot (ersetzt das Env-Var-Konzept TELEGRAM_ALLOWED_CHAT_ID/
-- LENGUA_USER_ID aus der ursprünglichen Spec): Jeder Lengua-Nutzer kann seinen Telegram-Chat
-- per Pairing-Code verbinden. Onboarding im Chat (Interessen als Freitext, dann Wunschzeit
-- für die täglichen Fragen), Abarbeitung pro Nutzer zur eigenen Zeit.
-- user_id kommt IMMER aus bot_links (chat_id -> user_id), nie aus Nachrichteninhalt.
-- NUR auf der es-Instanz (lengua) ausführen — Feature ist ES-only, NICHT auf llengua/ca.

-- Einmal-Codes, erzeugt vom lengua-Backend (Hablar-Reiter, M6) oder manuell per Service-Key.
-- Der Nutzer schickt den Code via /start <code> (Telegram-Deep-Link) an den Bot.
create table if not exists bot_pairing_codes (
  code        text primary key,
  user_id     uuid not null references user_settings(user_id),
  created_at  timestamptz not null default now(),
  used_at     timestamptz                    -- gesetzt = verbraucht; Codes verfallen nach 24 h
);

-- Eine Zeile pro verbundenem Nutzer. state ist der Onboarding-Zustand (restart-sicher):
-- interests -> time -> active. Erst 'active' bekommt tägliche Fragen.
create table if not exists bot_links (
  user_id       uuid primary key references user_settings(user_id),
  chat_id       bigint not null unique,
  state         text not null default 'interests' check (state in ('interests', 'time', 'active')),
  interests     text,                        -- Freitext aus dem Chat, fließt als {profil} in die Fragen-Generierung
  question_time time not null default '20:00',  -- lokale Wunschzeit (Europe/Madrid für alle, v1)
  created_at    timestamptz not null default now()
);
create index if not exists bot_links_chat_idx on bot_links (chat_id);

alter table bot_pairing_codes enable row level security;
alter table bot_links enable row level security;
