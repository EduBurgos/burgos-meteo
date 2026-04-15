"""Entry point per eseguire l'app direttamente con `python main.py <città>`."""
import sys

# Forza UTF-8 su Windows per supportare emoji e caratteri unicode nel terminale
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

from meteo.cli import app

if __name__ == "__main__":
    app()
