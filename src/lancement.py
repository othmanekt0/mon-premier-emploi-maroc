"""Lancement de l’interface depuis le paquet installé."""

import subprocess
import sys
from pathlib import Path


def interface() -> int:
    page = Path(__file__).resolve().parents[1] / "ui/app.py"
    return subprocess.call([sys.executable, "-m", "streamlit", "run", str(page), *sys.argv[1:]])
