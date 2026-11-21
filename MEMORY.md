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
* **Quality Gate:** Flake8 (0 erros, complexidade $\le 12$), Black + isort (100% formatado), Pytest (20/20 testes passando, 0 warnings, no Dev Container Linux, Python 3.12.11), Streamlit `AppTest` validado nos 3 cenários sem exceções, Zero Warnings.
* **Regras de Git:** A IA está **PROIBIDA de fazer push** e **só faz commit quando o usuário pedir expressamente**.

---

## 🕒 2. Últimas Atividades Realizadas (Janela Deslizante: Últimas 3)

### [Atividade 0] — Dev Container Enxuto (Python 3.12)
* **Data:** 21/11/2026
* **O que foi feito:**
  - `.devcontainer/devcontainer.json` reescrito: imagem `python:1-3.12-bookworm` (alinhada ao badge Python 3.12 do README e à imagem do curso de IA, reaproveitando as camadas já baixadas), `postCreateCommand: pip install -r requirements.txt` e porta 8501 encaminhada.
  - Removidos resquícios do modelo Streamlit do Codespaces: `customizations.codespaces`, trecho `packages.txt` (arquivo inexistente), instalação duplicada do `streamlit` e `postAttachCommand` (Streamlit agora é iniciado manualmente; flags que desligavam CORS/XSRF não são mais usadas).
  - `README.md` seção 3 atualizada (3.1 Dev Container, 3.2 instalação manual).
  - Pytest no contêiner Linux revelou `test_read_bytes_resilient_permission_fallback` dependente do Windows (no Linux o `shutil.copy2` usa o `open` builtin, bloqueado pelo mock global). Corrigido: o mock agora substitui só o `open` do módulo `src.utils.file_resilience`.
  - Removido `float_precision="round_trip"` de `pd.read_csv` em `src/pipelines/dataset_loader.py` (`Pandas4Warning`: obsoleto no pandas 3.x, que já lê floats com precisão padrão adequada); paridade do cache segue coberta por `test_hourly_cache_roundtrip_and_invalidation` (`rtol=1e-12`).
  - Pendente: dependências do `requirements.txt` sem versão fixada (`>=`).
* **Arquivos Chave:** `.devcontainer/devcontainer.json`, `README.md`, `tests/test_experiment_db.py`, `src/pipelines/dataset_loader.py`.

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

* *(Compactada)* [Atividade 3] — 13/11/2026: Zero Warnings + hooks pre-commit/pre-push (`scripts/*`, `.githooks/*`).

---

## 🎯 3. Próximos Passos & Onde Parou
* **Onde parou:** Implementação cross-dataset (`v1`, `v2`, `v4`), gráfico Ponto de Corte + Covariáveis, padronização `Hiperparâmetros de ML vs. Covariáveis`, *backdrop* unificado, indicador `run_XXXX` no topo e compactação para o Campeão concluídos e aprovados no Quality Gate (18/18 testes) + `AppTest`.
* **Dev Container (21/11/2026):** configuração enxuta em Python 3.12 validada: pytest 20/20 e flake8 sem erros dentro do contêiner; `Pandas4Warning` corrigido → 20 passed, 0 warnings. Alterações na *working tree*, aguardando commit do usuário.
* **Pronto para:** Testes ao vivo no Streamlit (`python -m streamlit run streamlit_app.py`), apresentação da disciplina PGENE585 ou `git commit` caso o usuário solicite.
