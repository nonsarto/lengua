-- Escucha (Hörverstehen): generierte Hörtexte + MC-Fragen. Die richtigen Antworten
-- leben serverseitig hier (questions.jsonb), damit der Client sie nicht vorab sieht.
-- Auf BEIDEN Instanzen ausführen (lengua/es UND llengua/ca).
create table if not exists listening_items (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references user_settings(user_id),
  passage     text not null,          -- der gesprochene Text (Transkript)
  gist        text not null,          -- deutscher Ein-Satz-Kontext
  questions   jsonb not null,         -- [{q, options[], answer}] — answer bleibt serverseitig
  created_at  timestamptz not null default now()
);
create index if not exists listening_items_user_idx on listening_items (user_id);
alter table listening_items enable row level security;
