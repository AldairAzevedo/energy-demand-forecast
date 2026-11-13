# Claude Code Guidelines & Directives

> **INSTRUÇÃO PRIMÁRIA:**  
> Leia e siga estritamente todas as diretrizes definidas em [**`AGENTS.md`**](AGENTS.md) e no diretório [**`rules/`**](rules/README.md).

## 🚨 REGRA INVIOLÁVEL: PROIBIÇÃO DE `git push`
* **NUNCA EXECUTE `git push`**: Apenas commits locais (`git commit`) são permitidos à IA. O push remoto é exclusivo do usuário (`AldairAzevedo`).

## 📚 Arquivos de Regras Obrigatórios:
- `rules/01_ARCHITECTURE_SOLID.md`: Arquitetura Monolítica em camadas e POO com SOLID.
- `rules/02_CLEAN_CODE_ZERO_TRASH.md`: Clean Code, Zero Trash e foco exclusivo no Zenodo Smart Building.
- `rules/03_SONARQUBE_AND_QUALITY.md`: SonarQube compliance, complexidade <= 15, flake8 zero warnings.
- `rules/04_TESTING_STANDARDS.md`: Testes obrigatórios com pytest (100% passando).
- `rules/05_GIT_AND_COMMIT_POLICY.md`: Conventional Commits em português.

## 🛠️ Comandos Rápidos:
- Testes: `python -m pytest tests/`
- Linter: `python -m flake8 src/ tests/ presentation/ streamlit_app.py`
- Execução: `python -m streamlit run streamlit_app.py`
