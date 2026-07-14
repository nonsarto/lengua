"""
manage.py — Admin-Bootstrap von der Kommandozeile (einmalig).

  python manage.py init-admin <username> <passwort> [Anzeigename]

Claimt die bestehende Vor-Auth-Nutzerzeile (mit all deinen Captures/States) als
Admin-Account. Existiert keine, wird eine neue Admin-Zeile angelegt.
Alles Weitere (Nutzer anlegen, Passwörter zurücksetzen) läuft über die App (/perfil).
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from auth import hash_password  # noqa: E402
from db import get_db  # noqa: E402


def init_admin(username: str, password: str, display_name: str | None) -> None:
    username = username.lower().strip()
    if len(password) < 8:
        sys.exit("Passwort bitte mindestens 8 Zeichen.")
    db = get_db()
    if db.get_user_by_username(username):
        sys.exit(f"Nutzer '{username}' existiert schon.")
    hashed = hash_password(password)
    name = display_name or username.capitalize()
    user = db.claim_legacy_user(username, hashed, name)
    if user:
        print(f"Admin '{username}' angelegt — deine bestehenden Lerndaten hängen dran.")
    else:
        db.create_user(username, hashed, name, is_admin=True)
        print(f"Admin '{username}' neu angelegt (keine Alt-Daten gefunden).")


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "init-admin":
        init_admin(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    else:
        sys.exit(__doc__)
