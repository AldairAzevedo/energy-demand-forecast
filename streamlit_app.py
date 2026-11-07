"""Ponto de entrada raiz para o deploy no Streamlit Community Cloud."""

import os
import sys

# Assegura que o diretório raiz está no path do Python
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.ui.app import main  # noqa: E402

if __name__ == "__main__":
    main()
