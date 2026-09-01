-- Positives Feedback in der Speaking-Analyse (lengua-bot):
--   highlights   = gelungene Stellen        [{text, comment, char_start, char_end}]
--   improvements = angewandte Learnings      [{text, past_original, past_corrected, comment}]
-- highlights-Offsets gegen das ORIGINAL-Transkript (wie error_log); improvements
-- referenzieren frühere error_log-Korrekturen. Der Bot schreibt beide Felder,
-- das Backend liest sie für die Hablar-Detailansicht.
-- NUR auf der es-Instanz (lengua) ausführen — Speaking ist ES-only, NICHT auf llengua/ca.

alter table speaking_sessions
  add column if not exists highlights   jsonb not null default '[]'::jsonb,
  add column if not exists improvements jsonb not null default '[]'::jsonb;
