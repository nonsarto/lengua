#!/bin/sh
# Spanisch-Instanz deployen: Backend (Railway service lengua) + Frontend (Vercel lengua)
set -e
cd "$(dirname "$0")/.."
railway up --detach --service lengua
cd frontend && vercel deploy --prod --yes
