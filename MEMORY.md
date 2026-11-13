# 🧠 MEMORY.md — Memória de Trabalho e Estado Ativo do Projeto (DOCUMENTO VIVO)

> 🔥 **DOCUMENTO VIVO DE ATUALIZAÇÃO MANDATÓRIA (LIVING MEMORY):**  
> 1. **No Início:** Toda IA **DEVE** ler este arquivo imediatamente para obter consciência situacional instantânea de onde o projeto parou.  
> 2. **A Cada Nova Tarefa:** Este arquivo **NÃO É ESTÁTICO**. Ele **DEVE SER ATUALIZADO VIVAMENTE** ao final de cada tarefa ou ciclo de trabalho, adicionando a nova atividade e rotacionando as antigas (janela deslizante de 3 a 5 itens).  
> 3. **Limite Estrito:** Mantenha o arquivo sempre entre ~50 e 120 linhas (Zero Trash).

---

## 📌 1. Estado Atual do Sistema
* **Escopo Único:** Zenodo 2025 Smart Building (Previsão de Carga, Geração Solar FV, Curva do Pato / Demanda Líquida).
* **Branch Git Ativa:** `main` (Pronta para push pelo usuário).
* **Deploy Online:** [energy-demand-forecast-ufam.streamlit.app](https://energy-demand-forecast-ufam.streamlit.app/)
* **Quality Gate:** Flake8 (0 erros, complexidade $\le 12$), Black + isort (100% formatado), Pytest (8/8 testes passando).
* **Tolerância Zero a Warnings:** Qualquer aviso (`UserWarning`, `Warning`) bloqueia commits e pushs automaticamente.
* **Git Hooks Ativos:** `.githooks/pre-commit` e `.githooks/pre-push` forçando `-X utf8` e `scripts/verify_quality.py`.
* **Regras de Git:** A IA está **PROIBIDA de fazer push** e **só faz commit quando o usuário pedir expressamente**.

---

## 🕒 2. Últimas Atividades Realizadas (Janela Deslizante: Últimas 3)

### [Atividade 1] — Resolução de Warnings de Encoding CP1252 e Blindagem Zero Warnings
* **Data:** 13/11/2026
* **O que foi feito:**
  - Identificada a causa raiz dos `UserWarning: Unable to parse file ... due to 'charmap' codec`: o `isort` rodando no Windows sob codepage legado CP1252.
  - Substituído o operador matemático unificado `−` (`\u2212`) por `-` ASCII padrão em `presentation/gerar_slides.py`.
  - Configurado `sys.stdout.reconfigure(encoding="utf-8")` e execução de subprocessos com `-X utf8`, `PYTHONUTF8=1` e `PYTHONIOENCODING=utf-8` em `verify_quality.py` e `format_code.py`.
  - Atualizados `.githooks/pre-commit` e `.githooks/pre-push` com `export PYTHONUTF8=1`.
  - Adicionada regra estrita em `scripts/verify_quality.py`: qualquer warning emitido em stderr falha o Quality Gate (código pleno).
* **Arquivos Chave:** `scripts/verify_quality.py`, `scripts/format_code.py`, `.githooks/*`, `presentation/gerar_slides.py`.

### [Atividade 2] — Implementação do Git Pre-Push Hook e Atualização do README
* **Data:** 13/11/2026
* **O que foi feito:**
  - Criado o hook `.githooks/pre-push` espelhando a validação de qualidade completa antes de qualquer `git push`.
  - Atualizada a Seção 5.3 do `README.md` documentando o fluxo duplo de proteção (Pre-Commit + Pre-Push).
  - Testada a execução do hook via `sh .githooks/pre-push` com 100% de sucesso.
* **Arquivos Chave:** `.githooks/pre-push`, `README.md`, `MEMORY.md`.

### [Atividade 3] — Commit da Governança de Memória Viva e Pre-Commit Hook
* **Data:** 13/11/2026
* **O que foi feito:**
  - Efetuado o commit `a16f606` sob solicitação expressa do usuário após interceptação e aprovação pelo pre-commit hook.
  - Implementada a política de Living Memory em `rules/07_AGENT_MEMORY_POLICY.md`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules` e `rules/README.md`.
* **Arquivos Chave:** `MEMORY.md`, `rules/*`, `scripts/*`, `AGENTS.md`.

---

## 🎯 3. Próximos Passos & Onde Parou
* **Onde parou:** Warnings de encoding totalmente eliminados na raiz. Scripts e hooks blindados com execução UTF-8 forçada e interceptador de warnings ativo.
* **Pronto para:** Receber autorização do usuário para commitar essas correções e seguir com o envio seguro (`git push`) ou novas demandas do projeto.
