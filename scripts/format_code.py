"""Script automatizado para formatação determinística de código (isort e black)."""

import os
import subprocess
import sys


def main() -> None:
    """Aplica formatação padronizada em todos os arquivos Python do projeto com suporte a UTF-8."""
    targets = ["src", "tests", "presentation", "scripts", "streamlit_app.py"]

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    print("\n📦 [1/2] Organizando imports com isort...")
    subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "isort"] + targets,
        check=True,
        env=env,
    )

    print("\n🎨 [2/2] Formatando código com black (PEP 8 / 100 caracteres)...")
    subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "black"] + targets,
        check=True,
        env=env,
    )

    print("\n✨ Formatação concluída com sucesso em todos os módulos!")


if __name__ == "__main__":
    main()
