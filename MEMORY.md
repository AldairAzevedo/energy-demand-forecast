# 🧠 MEMORY.md — Memória de Trabalho e Estado Ativo do Projeto (DOCUMENTO VIVO)

> 🔥 **DOCUMENTO VIVO DE ATUALIZAÇÃO MANDATÓRIA (LIVING MEMORY):**  
> 1. **No Início:** Toda IA **DEVE** ler este arquivo imediatamente para obter consciência situacional instantânea de onde o projeto parou.  
> 2. **A Cada Nova Tarefa:** Este arquivo **NÃO É ESTÁTICO**. Ele **DEVE SER ATUALIZADO VIVAMENTE** ao final de cada tarefa ou ciclo de trabalho, adicionando a nova atividade e rotacionando as antigas (janela deslizante de 3 a 5 itens).  
> 3. **Limite Estrito:** Mantenha o arquivo sempre entre ~50 e 120 linhas (Zero Trash).

---

## 📌 1. Estado Atual do Sistema
* **Escopo Único:** Zenodo 2025 Smart Building (Previsão de Carga, Geração Solar FV, Curva do Pato / Demanda Líquida).
* **Branch Git Ativa:** `main` (Sincronizada com `origin/main` após push do usuário).
* **Deploy Online:** [energy-demand-forecast-ufam.streamlit.app](https://energy-demand-forecast-ufam.streamlit.app/)
* **Quality Gate:** Flake8 (0 erros, complexidade $\le 12$), Black + isort (100% formatado), Pytest (8/8 testes passando).
* **Git Hooks Ativos:** `.githooks/pre-commit` e `.githooks/pre-push` executando `scripts/verify_quality.py`.
* **Regras de Git:** A IA está **PROIBIDA de fazer push** e **só faz commit quando o usuário pedir expressamente**.

---

## 🕒 2. Últimas Atividades Realizadas (Janela Deslizante: Últimas 3)

### [Atividade 1] — Implementação do Git Pre-Push Hook e Atualização do README
* **Data:** 13/11/2026
* **O que foi feito:**
  - Criado o hook `.githooks/pre-push` espelhando a validação de qualidade completa antes de qualquer `git push`.
  - Atualizada a Seção 5.3 do `README.md` documentando o fluxo duplo de proteção (Pre-Commit + Pre-Push).
  - Testada a execução do hook via `sh .githooks/pre-push` com 100% de sucesso.
* **Arquivos Chave:** `.githooks/pre-push`, `README.md`, `MEMORY.md`.

### [Atividade 2] — Commit da Governança de Memória Viva e Pre-Commit Hook
* **Data:** 13/11/2026
* **O que foi feito:**
  - Efetuado o commit `a16f606` sob solicitação expressa do usuário após interceptação e aprovação pelo pre-commit hook.
  - Implementada a política de Living Memory em `rules/07_AGENT_MEMORY_POLICY.md`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules` e `rules/README.md`.
* **Arquivos Chave:** `MEMORY.md`, `rules/*`, `scripts/*`, `AGENTS.md`.

### [Atividade 3] — Criação da Governança de Regras e Diretivas de IA
* **Data:** 13/11/2026
* **O que foi feito:**
  - Criado o diretório `rules/` com manuais de SOLID, Clean Code & Zero Trash, SonarQube, Testes e Git Policy.
  - Criados os pontos de entrada `AGENTS.md`, `CLAUDE.md` e `.cursorrules`.
  - Definida a proibição de `git push` pela IA e restrição de commits apenas sob autorização direta do usuário.
* **Arquivos Chave:** `rules/*`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules`.

---

## 🎯 3. Próximos Passos & Onde Parou
* **Onde parou:** Duplo Git Hook configurado (`pre-commit` e `pre-push`). Todas as validações automatizadas tanto ao commitar quanto ao enviar com `git push`.
* **Pronto para:** O usuário testar localmente em seu terminal executando `git push` ou receber novas tarefas de negócio/modelagem para o projeto Zenodo.
