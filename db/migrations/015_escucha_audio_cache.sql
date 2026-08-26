-- Escucha-Kosten-Fix (UX-Audit B11): Audio wird beim Generieren mit abgelegt und ein
-- unbeantworteter Hörtext beim nächsten Aufruf wiederverwendet, statt pro Seitenbesuch
-- Text (LLM) + Audio (TTS) neu zu erzeugen. answered_at markiert "verbraucht".
-- Auf BEIDEN Instanzen ausführen (lengua/es UND llengua/ca).
-- Der Backend-Code läuft auch OHNE diese Migration (Fallback: altes Verhalten) —
-- aber erst mit ihr greift der Cache.

alter table listening_items add column if not exists audio_b64        text;
alter table listening_items add column if not exists audio_media_type text default 'audio/mpeg';
alter table listening_items add column if not exists answered_at      timestamptz;

create index if not exists listening_items_reuse_idx
  on listening_items (user_id, created_at desc)
  where answered_at is null and audio_b64 is not null;
