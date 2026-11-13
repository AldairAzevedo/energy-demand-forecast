"""Script automatizado para verificação de qualidade de código.

Executa sequencialmente:
1. Verificação de ordenação de imports (isort)
2. Verificação de formatação de código (black)
3. Análise estática, conformidade PEP 8 e complexidade ciclomática (flake8 / Sonar)
4. Bateria completa de testes unitários e de integração (pytest)
"""

import subprocess
import sys


def run_step(step_name: str, cmd: list) -> bool:
    """Executa um comando de verificação e exibe o status formatado."""
    print("\n" + "=" * 56)
    print(f"🔍 [Verificação] {step_name}")
    print(f"👉 Comando: {' '.join(cmd)}")
    print("=" * 56)

    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"\n❌ [FALHA] {step_name} encontrou problemas (código de saída: {res.returncode}).")
        return False

    print(f"✅ [SUCESSO] {step_name} aprovado com 100% de conformidade.")
    return True


def main() -> None:
    """Orquestra a validação rigorosa de qualidade pré-commit."""
    targets = ["src", "tests", "presentation", "scripts", "streamlit_app.py"]

    steps = [
        (
            "1. Ordenação de Imports (isort --check)",
            [sys.executable, "-m", "isort", "--check", "--diff"] + targets,
        ),
        (
            "2. Formatação de Código (black --check)",
            [sys.executable, "-m", "black", "--check", "--diff"] + targets,
        ),
        (
            "3. Análise Estática & Sonar Rules (flake8)",
            [sys.executable, "-m", "flake8"] + targets,
        ),
        (
            "4. Testes Unitários e de Integração (pytest)",
            [sys.executable, "-m", "pytest", "tests/"],
        ),
    ]

    failed_steps = []
    for name, cmd in steps:
        if not run_step(name, cmd):
            failed_steps.append(name)
            break  # Interrompe na primeira falha para feedback imediato

    if failed_steps:
        print("\n" + "!" * 60)
        print("🚨 QUALIDADE REPROVADA! O commit não pode ser realizado.")
        print(f"Etapa que falhou: {failed_steps[0]}")
        print("💡 DICA: Para corrigir formatação e imports automaticamente, execute:")
        print("   python scripts/format_code.py")
        print("!" * 60 + "\n")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("🏆 PARABÉNS! Código 100% aprovado no Quality Gate:")
    print("   ✓ Formatação Black e isort impecáveis")
    print("   ✓ Zero warnings e complexidade ciclomática <= 12 no Flake8")
    print("   ✓ 100% dos testes unitários e de integração passando no Pytest")
    print("=" * 60 + "\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
