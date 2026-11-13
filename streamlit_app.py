"""Ponto de entrada raiz para o deploy no Streamlit Community Cloud."""

import importlib
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import src.ui.app as app_module  # noqa: E402

if __name__ == "__main__":
    importlib.reload(app_module)
    app_module.main()
