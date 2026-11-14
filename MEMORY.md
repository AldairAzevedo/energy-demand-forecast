# 🧠 MEMORY.md — Memória de Trabalho e Estado Ativo do Projeto (DOCUMENTO VIVO)

> 🔥 **DOCUMENTO VIVO DE ATUALIZAÇÃO MANDATÓRIA (LIVING MEMORY):**
> 1. **No Início:** Toda IA **DEVE** ler este arquivo imediatamente para obter consciência situacional instantânea de onde o projeto parou.
> 2. **A Cada Nova Tarefa:** Este arquivo **NÃO É ESTÁTICO**. Ele **DEVE SER ATUALIZADO VIVAMENTE** ao final de cada tarefa ou ciclo de trabalho, adicionando a nova atividade e rotacionando as antigas (janela deslizante de 3 a 5 itens).
> 3. **Limite Estrito:** Mantenha o arquivo sempre entre ~50 e 120 linhas (Zero Trash).

---

## 📌 1. Estado Atual do Sistema
* **Escopo Único:** Zenodo 2025 Smart Building — Previsão horária `1h` de consumo elétrico (`power (W)`) em 3 cenários (`v1_internal_split`, `v1_to_v2`, `v1_v2_to_v4`) com avaliação Multi-Critério (RMSE, MAE, R², Treino e Inferência).
* **Banco de Experimentos (`data/db/`, Schema `1.2.0`):** `active_config.json`, `best_models_registry.json` (com `champions_by_scenario`), `experiment_runs.json` e `zenodo_forecast_results.json` (incluindo `active_run_id`, `context_sample` e `recent_predictions_sample` imediatamente pós-corte).
* **Interface Científica:** Terminologia padronizada em **`Hiperparâmetros de ML`** vs. **`Covariáveis`**, gráfico principal unificado no estilo Timestral (**Potência + Temperatura + Geração Solar FV** na mesma figura e mesmo **Ponto de Corte Temporal**, iluminando ou apagando o Pós-Corte das covariáveis conforme os switches integrados que re-treinam em sincronia com a aba Laboratório), barra de cenário + `🧪 Rodada Ativa: run_XXXX` no topo, *backdrop* escuro unificado em todos os botões e botão **`🧹 Limpar Histórico (Manter Só Campeão)`** (`compact_history_to_champion`).
* **Branch Git Ativa:** `main` (alterações na *working tree*, aguardando solicitação explícita de commit pelo usuário conforme Regra 05).
* **Deploy Online:** [energy-demand-forecast-ufam.streamlit.app](https://energy-demand-forecast-ufam.streamlit.app/)
* **Quality Gate:** Flake8 (0 erros, complexidade $\le 12$), Black + isort (100% formatado), Pytest (18/18 testes passando), Streamlit `AppTest` validado nos 3 cenários sem exceções, Zero Warnings.
* **Regras de Git:** A IA está **PROIBIDA de fazer push** e **só faz commit quando o usuário pedir expressamente**.

---

## 🕒 2. Últimas Atividades Realizadas (Janela Deslizante: Últimas 3)

### [Atividade 1] — Cross-Dataset (v1, v2, v4), Gráfico Ponto de Corte, Backdrop Unificado & Reset para Campeão
* **Data:** 14/11/2026
* **O que foi feito:**
  - Criados `src/core/forecasting.py` (cenários `v1_internal_split`, `v1_to_v2` com *warm-up* causal sem leakage e `v1_v2_to_v4` compatível com `≤ 24 h` sem geração/elétricos) e `src/pipelines/dataset_loader.py` (tratando `ºC`/`˚C` e combinando `v4` Dias 1–3).
  - Atualizado `src/pipelines/zenodo_pipeline.py` e `src/ui/charts.py` para gravar e plotar `context_sample` (pré-corte) + linha vertical `✂️ Ponto de Corte` + `recent_predictions_sample` imediatamente pós-corte (`[:horizon_hours]`, corrigindo fatia `[-168:]`), com datas/horas reais no eixo X e subgráfico opcional de **Covariáveis**.
  - Atualizados `src/utils/experiment_db.py` (Schema `1.2.0`, campeões isolados por cenário, `compact_history_to_champion`), `src/pipelines/cycle_manager.py` (`active_run_id`), `src/ui/components.py`, `src/ui/app.py` e `src/ui/param_lab.py` (`Hiperparâmetros de ML` vs. `Covariáveis`, *backdrop* unificado via `pending_lab_action`, indicador de `run_XXXX` no topo e botão `🧹 Limpar Histórico (Manter Só Campeão)`).
* **Arquivos Chave:** `src/core/forecasting.py`, `src/core/parameter_schema.py`, `src/pipelines/dataset_loader.py`, `src/pipelines/zenodo_pipeline.py`, `src/utils/experiment_db.py`, `src/ui/*`, `tests/test_cross_dataset.py`.

### [Atividade 2] — Evolução Multi-Critério, Bancada em 3 Abas e Remoção da Ingestão
* **Data:** 13/11/2026
* **O que foi feito:**
  - Evoluído `src/core/diagnostics.py`, bancada em 3 abas (**Diagnóstico**, **Laboratório de Parâmetros** e **Histórico**), removida ingestão manual e diretório legado `data/cycles/`.
* **Arquivos Chave:** `src/core/diagnostics.py`, `src/ui/param_lab.py`, `src/pipelines/cycle_manager.py`.

### [Atividade 3] — Blindagem Zero Warnings e Hooks Pre-Commit / Pre-Push
* **Data:** 13/11/2026
* **O que foi feito:**
  - Padronizado UTF-8 e política Zero Warnings em `scripts/verify_quality.py`, `scripts/format_code.py`, `.githooks/pre-commit` e `.githooks/pre-push`.
* **Arquivos Chave:** `scripts/*`, `.githooks/*`, `rules/*`.

---

## 🎯 3. Próximos Passos & Onde Parou
* **Onde parou:** Implementação cross-dataset (`v1`, `v2`, `v4`), gráfico Ponto de Corte + Covariáveis, padronização `Hiperparâmetros de ML vs. Covariáveis`, *backdrop* unificado, indicador `run_XXXX` no topo e compactação para o Campeão concluídos e aprovados no Quality Gate (18/18 testes) + `AppTest`.
* **Pronto para:** Testes ao vivo no Streamlit (`python -m streamlit run streamlit_app.py`), apresentação da disciplina PGENE585 ou `git commit` caso o usuário solicite.
