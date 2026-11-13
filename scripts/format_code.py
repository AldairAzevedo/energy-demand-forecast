"""Script automatizado para formatação determinística de código (isort e black)."""

import subprocess
import sys


def main() -> None:
    """Aplica formatação padronizada em todos os arquivos Python do projeto."""
    targets = ["src", "tests", "presentation", "scripts", "streamlit_app.py"]

    print("\n📦 [1/2] Organizando imports com isort...")
    subprocess.run([sys.executable, "-m", "isort"] + targets, check=True)

    print("\n🎨 [2/2] Formatando código com black (PEP 8 / 100 caracteres)...")
    subprocess.run([sys.executable, "-m", "black"] + targets, check=True)

    print("\n✨ Formatação concluída com sucesso em todos os módulos!")


if __name__ == "__main__":
    main()
