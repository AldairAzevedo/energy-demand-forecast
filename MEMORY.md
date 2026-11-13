# 🧠 MEMORY.md — Memória de Trabalho e Estado Ativo do Projeto (DOCUMENTO VIVO)

> 🔥 **DOCUMENTO VIVO DE ATUALIZAÇÃO MANDATÓRIA (LIVING MEMORY):**  
> 1. **No Início:** Toda IA **DEVE** ler este arquivo imediatamente para obter consciência situacional instantânea de onde o projeto parou.  
> 2. **A Cada Nova Tarefa:** Este arquivo **NÃO É ESTÁTICO**. Ele **DEVE SER ATUALIZADO VIVAMENTE** ao final de cada tarefa ou ciclo de trabalho, adicionando a nova atividade e rotacionando as antigas (janela deslizante de 3 a 5 itens).  
> 3. **Limite Estrito:** Mantenha o arquivo sempre entre ~50 e 120 linhas (Zero Trash).

---

## 📌 1. Estado Atual do Sistema
* **Escopo Único:** Zenodo 2025 Smart Building (Previsão de Carga, Geração Solar FV, Curva do Pato / Demanda Líquida).
* **Branch Git Ativa:** `main` (Branch de backup completa com CMU: `versao-completa-cmu-zenodo`).
* **Deploy Online:** [energy-demand-forecast-ufam.streamlit.app](https://energy-demand-forecast-ufam.streamlit.app/)
* **Quality Gate:** Flake8 (0 erros, complexidade $\le 12$), Black + isort (100% formatado), Pytest (8/8 testes passando).
* **Git Pre-Commit Hook:** Ativo via `.githooks/pre-commit` executando `scripts/verify_quality.py`.
* **Regras de Git:** A IA está **PROIBIDA de fazer push** e **só faz commit quando o usuário pedir expressamente**.

---

## 🕒 2. Últimas Atividades Realizadas (Janela Deslizante: Últimas 3)

### [Atividade 1] — Governança de Memória Viva, Pre-Commit Hook e Qualidade
* **Data:** 13/11/2026
* **O que foi feito:**
  - Criado o arquivo `MEMORY.md` (documento vivo de janela deslizante) e formalizada a regra `rules/07_AGENT_MEMORY_POLICY.md`.
  - Criados os scripts `scripts/format_code.py` e `scripts/verify_quality.py` com Quality Gate automatizado (flake8, black, isort, pytest).
  - Implementado Git Pre-Commit Hook (`.githooks/pre-commit`) e configurado `git config core.hooksPath .githooks`.
  - Criada a regra `rules/06_DOCUMENTATION_EVOLUTION.md` e sincronizado o `README.md`.
* **Arquivos Chave:** `MEMORY.md`, `rules/06_*`, `rules/07_*`, `scripts/verify_quality.py`, `scripts/format_code.py`, `.githooks/pre-commit`, `README.md`.

### [Atividade 2] — Criação da Governança de Regras e Diretivas de IA
* **Data:** 13/11/2026
* **O que foi feito:**
  - Criado o diretório `rules/` com manuais de SOLID, Clean Code & Zero Trash, SonarQube, Testes e Git Policy.
  - Criados os pontos de entrada `AGENTS.md`, `CLAUDE.md` e `.cursorrules`.
  - Definida a proibição de `git push` pela IA e restrição de commits apenas sob autorização direta do usuário.
* **Arquivos Chave:** `rules/*`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules`.

### [Atividade 3] — Limpeza Completa e Zero Trash dos Desafios CMU
* **Data:** 12/11/2026 - 13/11/2026
* **O que foi feito:**
  - Backup preservado na branch `versao-completa-cmu-zenodo`.
  - Removidos todos os 28 arquivos e pastas legadas da CMU (Q5 e Q6) e código morto (`models.py`, `losses.py`, `preprocessor.py`).
  - Slides e documentação reestruturados em 7 slides focados 100% no Zenodo Smart Building.
* **Arquivos Chave:** `src/pipelines/zenodo_pipeline.py`, `src/ui/app.py`, `presentation/gerar_slides.py`.

---

## 🎯 3. Próximos Passos & Onde Parou
* **Onde parou:** Governança completa implementada, ferramentas de qualidade prontas, pre-commit hook ativo e política de memória viva (`MEMORY.md`) formalizada em todos os pontos de entrada de IA.
* **Pronto para:** Receber novas demandas de modelagem, novos experimentos ou requisitos solicitados pelo professor para o desafio Zenodo Smart Building.
