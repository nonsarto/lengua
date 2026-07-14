-- User-Management: Admin legt Nutzer mit username+password an (kein Self-Signup).
-- Die bestehende user_settings-Zeile (mit all deinen Daten) wird per
-- `python manage.py init-admin <username> <passwort>` zum Admin-Account.
alter table user_settings
  add column if not exists username       text unique,
  add column if not exists password_hash  text,
  add column if not exists display_name   text,
  add column if not exists is_admin       boolean not null default false,
  add column if not exists level_estimate text,
  add column if not exists onboarded_at   timestamptz;
