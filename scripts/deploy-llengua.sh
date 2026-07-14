#!/bin/sh
# Katalanisch-Instanz deployen: Backend (Railway service llengua) + Frontend (Vercel llengua).
# Vercel-Links sind verzeichnisbasiert — für llengua kurz umhängen und wieder zurück.
set -e
cd "$(dirname "$0")/.."
railway up --detach --service llengua
cd frontend
mv .vercel .vercel-lengua && mv .vercel-llengua .vercel
trap 'mv .vercel .vercel-llengua; mv .vercel-lengua .vercel' EXIT
vercel deploy --prod --yes
rm -f .env.local
