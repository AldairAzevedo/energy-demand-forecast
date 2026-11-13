# 🧠 MEMORY.md — Memória de Trabalho e Estado Ativo do Projeto (DOCUMENTO VIVO)

> 🔥 **DOCUMENTO VIVO DE ATUALIZAÇÃO MANDATÓRIA (LIVING MEMORY):**  
> 1. **No Início:** Toda IA **DEVE** ler este arquivo imediatamente para obter consciência situacional instantânea de onde o projeto parou.  
> 2. **A Cada Nova Tarefa:** Este arquivo **NÃO É ESTÁTICO**. Ele **DEVE SER ATUALIZADO VIVAMENTE** ao final de cada tarefa ou ciclo de trabalho, adicionando a nova atividade e rotacionando as antigas (janela deslizante de 3 a 5 itens).  
> 3. **Limite Estrito:** Mantenha o arquivo sempre entre ~50 e 120 linhas (Zero Trash).

---

## 📌 1. Estado Atual do Sistema
* **Escopo Único:** Zenodo 2025 Smart Building — Previsão estrita de consumo elétrico (`power (W)`) com métricas multi-critério (RMSE, MAE, R², Treino e Inferência).
* **Branch Git Ativa:** `main` (Pronto para commit solicitado pelo usuário).
* **Deploy Online:** [energy-demand-forecast-ufam.streamlit.app](https://energy-demand-forecast-ufam.streamlit.app/)
* **Quality Gate:** Flake8 (0 erros, complexidade $\le 12$), Black + isort (100% formatado), Pytest (8/8 testes passando), Zero Warnings.
* **Regras de Git:** A IA está **PROIBIDA de fazer push** e **só faz commit quando o usuário pedir expressamente**.

---

## 🕒 2. Últimas Atividades Realizadas (Janela Deslizante: Últimas 3)

### [Atividade 1] — Refatoração de Escopo Zenodo 2025, Acessibilidade Light/Dark e Auto-Rerun
* **Data:** 13/11/2026
* **O que foi feito:**
  - Removidos cálculos e KPIs fora do escopo oficial (Demanda Líquida / Curva do Pato e indicadores de solar como saída).
  - Adicionados atributos causais (sazonalidade horária, lags 1h/2h/3h/24h/48h/168h e estatísticas móveis) e modelo `HistGradientBoostingRegressor` (R² = 0.9261, RMSE = 301.04 W, MAE = 156.51 W).
  - Implementada paleta universal de alto contraste nos temas Light e Dark (consumo real em violeta `#8B5CF6`, campeão em azul cobalto `#0284C7`, RF em verde e Ridge em laranja).
  - Adicionadas legendas coloridas sincronizadas e guia rápido para iniciantes.
  - Configurado auto-reload em tempo real (`.streamlit/config.toml`, `importlib.reload` e invalidação por `mtime`).
  - Atualizados `app.py`, `charts.py`, `components.py`, `slides_apresentacao.pptx/.pdf`, `PLANO_DE_TRABALHO.md` e `README.md`.
* **Arquivos Chave:** `src/ui/*`, `src/pipelines/zenodo_pipeline.py`, `.streamlit/config.toml`, `presentation/*`, `tests/*`.

### [Atividade 2] — Resolução de Warnings de Encoding CP1252 e Blindagem Zero Warnings
* **Data:** 13/11/2026
* **O que foi feito:**
  - Configurado `sys.stdout.reconfigure(encoding="utf-8")`, `-X utf8` e intolerância a warnings em `scripts/verify_quality.py`, `scripts/format_code.py` e `.githooks/*`.
* **Arquivos Chave:** `scripts/verify_quality.py`, `scripts/format_code.py`, `.githooks/*`.

### [Atividade 3] — Implementação do Git Pre-Push Hook e Governança de Memória Viva
* **Data:** 13/11/2026
* **O que foi feito:**
  - Criado `.githooks/pre-push` espelhando a validação de qualidade antes do `git push`.
* **Arquivos Chave:** `.githooks/pre-push`, `README.md`, `MEMORY.md`.

---

## 🎯 3. Próximos Passos & Onde Parou
* **Onde parou:** Commit realizado conforme a Regra 05 após aprovação pelo hook de pre-commit.
* **Pronto para:** Sanar dúvidas do usuário para a apresentação acadêmica de amanhã ou avançar na previsão trimestral / Mistral.
