"""Script automatizado para verificação rigorosa de qualidade de código.

Executa sequencialmente:
1. Verificação de ordenação de imports (isort)
2. Verificação de formatação de código (black)
3. Análise estática, conformidade PEP 8 e complexidade ciclomática (flake8 / Sonar)
4. Bateria completa de testes unitários e de integração (pytest)

Regra Estrita de Governança:
Zero Warnings e Zero Errors. Qualquer aviso ou falha bloqueia o Quality Gate.
"""

import os
import subprocess
import sys

# Garante que stdout e stderr operem em UTF-8 mesmo em consoles Windows com codepage legado (CP1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def run_step(step_name: str, cmd: list) -> bool:
    """Executa um comando de verificação forçando UTF-8 e tratando warnings como erros."""
    print("\n" + "=" * 56)
    print(f"[Verificação] {step_name}")
    print(f"Comando: {' '.join(cmd)}")
    print("=" * 56)

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    res = subprocess.run(
        cmd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if res.stdout:
        print(res.stdout.strip())
    if res.stderr:
        print(res.stderr.strip())

    if res.returncode != 0:
        print(f"\n[FALHA] {step_name} retornou código de erro: {res.returncode}.")
        return False

    # Política Rigorosa: Zero Warnings tolerados
    stderr_lower = res.stderr.lower()
    if "userwarning:" in stderr_lower or "warning:" in stderr_lower:
        print(f"\n[FALHA] {step_name} emitiu warnings! Política estrita de Zero Warnings violada.")
        return False

    print(f"[SUCESSO] {step_name} aprovado com 100% de conformidade.")
    return True


def main() -> None:
    """Orquestra a validação rigorosa de qualidade pré-commit e pré-push."""
    targets = ["src", "tests", "presentation", "scripts", "streamlit_app.py"]
    py_exec = sys.executable

    steps = [
        (
            "1. Ordenação de Imports (isort --check)",
            [py_exec, "-X", "utf8", "-m", "isort", "--check", "--diff"] + targets,
        ),
        (
            "2. Formatação de Código (black --check)",
            [py_exec, "-X", "utf8", "-m", "black", "--check", "--diff"] + targets,
        ),
        (
            "3. Análise Estática & Sonar Rules (flake8)",
            [py_exec, "-X", "utf8", "-m", "flake8"] + targets,
        ),
        (
            "4. Testes Unitários e de Integração (pytest)",
            [py_exec, "-X", "utf8", "-m", "pytest", "tests/"],
        ),
    ]

    failed_steps = []
    for name, cmd in steps:
        if not run_step(name, cmd):
            failed_steps.append(name)
            break

    if failed_steps:
        print("\n" + "!" * 60)
        print("QUALIDADE REPROVADA! Operação bloqueada.")
        print(f"Motivo / Etapa que falhou: {failed_steps[0]}")
        print("DICA: Para corrigir formatação e imports automaticamente, execute:")
        print("   python scripts/format_code.py")
        print("!" * 60 + "\n")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("PARABÉNS! Código 100% aprovado no Quality Gate:")
    print("   ✓ Formatação Black e isort impecáveis (suporte nativo UTF-8)")
    print("   ✓ Zero warnings e complexidade ciclomática <= 12 no Flake8")
    print("   ✓ 100% dos testes unitários e de integração passando no Pytest")
    print("   ✓ Zero tolerância para warnings ou problemas pendentes")
    print("=" * 60 + "\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
