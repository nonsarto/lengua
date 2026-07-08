"""Slice 0 runner. Usage: python run.py "ayer he ido a la playa"
Braucht nur ANTHROPIC_API_KEY in der Umgebung (oder .env). Kein DB, kein Server."""
import sys, json
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, "backend/app")
from analyze import analyze

if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) or sys.stdin.read().strip()
    print(json.dumps(analyze(text), ensure_ascii=False, indent=2))
