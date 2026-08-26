-- Speaking Bot: Themen für die tägliche Meinungsfrage (Frage 2) werden pro Nutzer
-- im Onboarding festgelegt (max 5, änderbar per /temas). Die Tagesnachricht zeigt
-- Themen-Buttons; die konkrete Frage pro Thema wird morgens vorgeneriert.
-- Onboarding-Flow neu: interests -> topics -> time -> active.
-- topics_edit/time_edit sind die Zustände für nachträgliches Ändern (/temas, /hora).
-- NUR auf der es-Instanz (lengua) ausführen — Feature ist ES-only, NICHT auf llengua/ca.

alter table bot_links add column if not exists topics jsonb not null default '[]';

alter table bot_links drop constraint if exists bot_links_state_check;
alter table bot_links add constraint bot_links_state_check
  check (state in ('interests', 'topics', 'time', 'active', 'topics_edit', 'time_edit'));
