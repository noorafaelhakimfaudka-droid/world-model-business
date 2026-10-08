"""
streamlit_app.py
Titik masuk utama (entry point) untuk deployment Streamlit Community Cloud.
Menjalankan app.main() secara bersih tanpa manipulasi modul internal.
"""

import sys
from pathlib import Path

# Pastikan root direktori proyek selalu ada di sys.path
ROOT_DIR = str(Path(__file__).resolve().parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import app

if __name__ == "__main__":
    app.main()
