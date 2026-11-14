"""Laboratório de Pesquisa organizado em abas (Diagnóstico, Parâmetros e Histórico)."""

from copy import deepcopy
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

import src.ui.charts as charts_module
import src.ui.components as components_module
from src.core.diagnostics import (
    CRITERION_DESCRIPTIONS,
    SELECTION_CRITERIA,
    format_rank_badge,
    rank_benchmarking_models,
)
from src.core.forecasting import (
    SCENARIO_LABELS,
    SCENARIO_SHORT_LABELS,
    sanitize_scenario,
    scenario_supports_generation,
)
from src.core.parameter_schema import (
    MODEL_DISPLAY_NAMES,
    MODEL_KEYS,
    get_parameter_taxonomy,
    sanitize_model_config,
)
from src.pipelines.cycle_manager import CycleManager
from src.utils.experiment_db import ExperimentDatabase

PRESET_LAGS: List[int] = [1, 2, 3, 4, 6, 8, 12, 24, 48, 72, 96, 120, 144, 168, 336]
PRESET_ROLL_MEANS: List[int] = [3, 6, 12, 24, 48, 72, 168]
PRESET_ROLL_STDS: List[int] = [6, 12, 24, 48, 168]


def _get_ui_version() -> int:
    if "param_ui_version" not in st.session_state:
        st.session_state.param_ui_version = 0
    return int(st.session_state.param_ui_version)


def _bump_ui_version() -> None:
    st.session_state.param_ui_version = _get_ui_version() + 1


def queue_lab_action(
    action_type: str,
    loading_message: str,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    """Enfileira uma ação de experimento para rodar no topo do ciclo com backdrop unificado."""
    st.session_state["pending_lab_action"] = {
        "type": action_type,
        "loading_message": loading_message,
        "payload": payload or {},
    }
    st.rerun()


def _run_pipeline_action(
    manager: CycleManager,
    configs: Dict[str, Dict[str, Any]],
    message: str,
) -> str:
    result = manager.run_all(model_configs=configs, export_figure=False)
    run_id = result.get("experiment", {}).get("run_id", "-")
    records = result.get("experiment", {}).get("new_records", [])
    if records:
        return (
            f"{message} (`{run_id}`) — 🏆 Novo campeão multi-critério salvo para: "
            f"{', '.join(records)}!"
        )
    return f"{message} (`{run_id}`)"


def _dispatch_pending_action(
    manager: CycleManager,
    action_type: str,
    payload: Dict[str, Any],
) -> str:
    criterion = str(payload.get("criterion", "multi_criteria"))
    scenario = sanitize_scenario(payload.get("scenario"))

    if action_type == "train_configs":
        return _run_pipeline_action(manager, payload["configs"], str(payload["message"]))

    if action_type == "reset_one":
        model_key = str(payload["model_key"])
        res = manager.db.reset_model_to_best(
            model_key, criterion=criterion, evaluation_scenario=scenario
        )
        _bump_ui_version()
        msg = f"🏆 {MODEL_DISPLAY_NAMES[model_key]} restaurado via {res['source']}."
        return _run_pipeline_action(manager, manager.db.load_active_configs(), msg)

    if action_type == "reset_all":
        restored = manager.db.reset_all_to_best(criterion=criterion, evaluation_scenario=scenario)
        _bump_ui_version()
        msg = f"🏆 Todos os modelos restaurados segundo `{SELECTION_CRITERIA[criterion]}`!"
        return _run_pipeline_action(manager, restored, msg)

    if action_type == "reset_factory":
        restored = manager.db.reset_to_factory_defaults(evaluation_scenario=scenario)
        _bump_ui_version()
        return _run_pipeline_action(
            manager, restored, "🔄 Parâmetros padrão iniciais restaurados para os 3 modelos!"
        )

    if action_type == "restore_run":
        chosen_run = str(payload["run_id"])
        restored = manager.db.restore_run_config(chosen_run)
        _bump_ui_version()
        return _run_pipeline_action(
            manager, restored, f"⏪ Parâmetros da rodada `{chosen_run}` carregados!"
        )

    if action_type == "switch_scenario":
        configs = manager.db.load_active_configs()
        for key in MODEL_KEYS:
            configs[key]["split"]["evaluation_scenario"] = scenario
        saved = manager.db.save_active_configs(configs)
        _bump_ui_version()
        return _run_pipeline_action(
            manager, saved, f"📌 Cenário alterado para **{SCENARIO_LABELS[scenario]}**!"
        )

    if action_type == "toggle_covariates":
        configs = manager.db.load_active_configs()
        use_temp = bool(payload.get("use_temperature", True))
        use_gen = bool(payload.get("use_generation", True))
        for key in MODEL_KEYS:
            configs[key]["features"]["use_temperature"] = use_temp
            configs[key]["features"]["use_generation"] = use_gen
            configs[key]["split"]["evaluation_scenario"] = scenario
        saved = manager.db.save_active_configs(configs)
        _bump_ui_version()
        state_lbl = (
            f"Temperatura={'ON' if use_temp else 'OFF'} · " f"Solar FV={'ON' if use_gen else 'OFF'}"
        )
        return _run_pipeline_action(
            manager, saved, f"🎛️ Covariáveis atualizadas no gráfico ({state_lbl})!"
        )

    res = manager.compact_to_champion(export_figure=False)
    _bump_ui_version()
    if res.get("empty"):
        return "ℹ️ Nenhuma rodada encontrada para compactar."
    orig = res["summary"]["kept_original_run_id"]
    return f"🧹 Histórico limpo! Mantida apenas a rodada Campeã (`{orig}` → `run_0001`)."


def process_pending_action(root_dir: str) -> None:
    """Executa ação enfileirada exibindo backdrop escuro unificado sobre toda a aplicação."""
    pending = st.session_state.get("pending_lab_action")
    if not isinstance(pending, dict):
        return

    backdrop = components_module.render_loading_backdrop(
        str(pending.get("loading_message", "Processando experimento..."))
    )
    try:
        manager = CycleManager(root_dir)
        feedback = _dispatch_pending_action(
            manager,
            str(pending.get("type", "")),
            dict(pending.get("payload", {})),
        )
        st.session_state["lab_feedback"] = feedback
    finally:
        st.session_state.pop("pending_lab_action", None)
        backdrop.empty()
    st.rerun()


def _build_learning_summary_rows(bench: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for idx, (key, info) in enumerate(rank_benchmarking_models(bench)):
        tr = info.get("train_metrics", {})
        te = info.get("metrics", {})
        diag = info.get("learning_diagnosis", {})
        err = info.get("error_diagnostics", {})
        rows.append(
            {
                "Posição": format_rank_badge(idx),
                "Modelo": charts_module.MODEL_UI_META.get(key, {}).get(
                    "short", info.get("name", key)
                ),
                "Nota Multi-Critério": f"{te.get('multi_criteria_score', 0.0):.1f}/100",
                "RMSE Treino (W)": tr.get("rmse", "-"),
                "RMSE Teste (W)": te.get("rmse", "-"),
                "R² Treino": f"{float(tr.get('r2', 0.0)) * 100:.1f}%",
                "R² Teste": f"{float(te.get('r2', 0.0)) * 100:.1f}%",
                "Acerto ≤ 200 W": f"{err.get('hit_rate_200w_pct', 0.0):.1f}%",
                "Diagnóstico": diag.get("status", "-"),
            }
        )
    return rows


def _render_diagnostics_tab(zenodo_data: Dict[str, Any]) -> None:
    st.info(
        "**Para que serve esta aba:** mostra se cada modelo realmente aprendeu o padrão ou se "
        "apenas *decorou* o treino (**Overfitting**), além de revelar em quais horários ele "
        "acerta mais e erra mais."
    )
    bench = zenodo_data.get("models_benchmarking", {})
    if not bench:
        st.warning("Execute o pipeline ao menos uma vez para visualizar o diagnóstico.")
        return

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.plotly_chart(charts_module.build_train_vs_test_chart(zenodo_data), width="stretch")
        st.caption(
            "💡 Barra verde muito menor que a azul indica **Overfitting** (foi ótimo no passado "
            "do treino, mas perdeu precisão nos dados novos do teste)."
        )
    with col_g2:
        st.plotly_chart(charts_module.build_period_error_chart(zenodo_data), width="stretch")
        st.caption(
            "💡 Mostra em qual turno do dia o erro médio absoluto (**MAE**) é maior para ajudar a "
            "decidir quais variáveis ou lags testar."
        )

    summary_rows = _build_learning_summary_rows(bench)
    if summary_rows:
        components_module.render_explained_dataframe(pd.DataFrame(summary_rows))

    with st.expander("🔎 Ver Top 5 Maiores Acertos e Maiores Erros no Teste (Por Modelo)"):
        diag_model = st.selectbox(
            "Escolha o modelo para inspecionar horas extremas:",
            options=[k for k in MODEL_KEYS if k in bench],
            format_func=lambda k: MODEL_DISPLAY_NAMES[k],
            key="diag_extreme_model",
        )
        err_diag = bench.get(diag_model, {}).get("error_diagnostics", {})
        c_best, c_worst = st.columns(2)
        with c_best:
            st.markdown("**✅ Top 5 Maiores Acertos (Menor Desvio)**")
            best_cases = err_diag.get("top_best_hours", [])
            if best_cases:
                components_module.render_explained_dataframe(pd.DataFrame(best_cases))
        with c_worst:
            st.markdown("**⚠️ Top 5 Maiores Erros (Maior Desvio)**")
            worst_cases = err_diag.get("top_worst_hours", [])
            if worst_cases:
                components_module.render_explained_dataframe(pd.DataFrame(worst_cases))


def _render_essential_hyperparams(
    model_key: str,
    hp: Dict[str, Any],
    ver: int,
) -> Dict[str, Any]:
    if model_key == "Ridge_Linear":
        alpha = st.number_input(
            "Alpha — Regularização L2",
            min_value=0.01,
            max_value=1000.0,
            value=float(hp.get("alpha", 1.0)),
            step=0.5,
            key=f"hp_alpha_{model_key}_{ver}",
        )
        st.caption("Impede pesos exagerados nas variáveis; valores maiores suavizam a previsão.")
        return {"alpha": alpha}

    if model_key == "Random_Forest":
        n_est = st.number_input(
            "Nº de Árvores (n_estimators)",
            min_value=10,
            max_value=500,
            value=int(hp.get("n_estimators", 100)),
            step=10,
            key=f"hp_nest_{model_key}_{ver}",
        )
        st.caption(
            "Quantas árvores votam na resposta. Mais árvores reduzem ruído, mas levam mais tempo."
        )
        max_d = st.number_input(
            "Profundidade Máxima (max_depth)",
            min_value=2,
            max_value=50,
            value=int(hp.get("max_depth", 16)),
            step=1,
            key=f"hp_depth_{model_key}_{ver}",
        )
        st.caption(
            "Controla o nível de detalhe das regras. Muito alto gera overfitting (decora o treino)."
        )
        return {
            "n_estimators": n_est,
            "max_depth": max_d,
            "min_samples_leaf": int(hp.get("min_samples_leaf", 1)),
        }

    max_iter = st.number_input(
        "Rodadas de Correção (max_iter)",
        min_value=20,
        max_value=1000,
        value=int(hp.get("max_iter", 200)),
        step=20,
        key=f"hp_iter_{model_key}_{ver}",
    )
    st.caption("Quantas etapas sequenciais o modelo usa para corrigir erros das etapas anteriores.")
    lr = st.number_input(
        "Taxa de Aprendizado (learning_rate)",
        min_value=0.005,
        max_value=0.5,
        value=float(hp.get("learning_rate", 0.05)),
        step=0.01,
        format="%.3f",
        key=f"hp_lr_{model_key}_{ver}",
    )
    st.caption("Tamanho de cada passo de aprendizado; valores menores generalizam melhor.")
    l2_reg = st.number_input(
        "Freio Anti-Overfitting (l2_regularization)",
        min_value=0.0,
        max_value=50.0,
        value=float(hp.get("l2_regularization", 0.0)),
        step=0.5,
        key=f"hp_l2_{model_key}_{ver}",
    )
    st.caption("Penaliza regras complexas demais para evitar que o modelo decore o treino.")
    return {
        "max_iter": max_iter,
        "learning_rate": lr,
        "max_depth": int(hp.get("max_depth", 0)),
        "l2_regularization": l2_reg,
    }


def _render_advanced_tuning_expander(
    model_key: str,
    feat: Dict[str, Any],
    split: Dict[str, Any],
    hp_base: Dict[str, Any],
    ver: int,
) -> Dict[str, Any]:
    with st.expander("⚙️ Ajustes Avançados (Divisão Treino/Teste, Desvio Móvel e Extras)"):
        std_opts = sorted(set(PRESET_ROLL_STDS) | set(feat["rolling_std_windows"]))
        roll_stds = st.multiselect(
            "Janelas de Desvio Padrão Móvel (h)",
            options=std_opts,
            default=feat["rolling_std_windows"],
            key=f"rstd_{model_key}_{ver}",
        )
        st.caption("Mede o quanto o consumo oscilou recentemente nas últimas N horas.")

        use_raw = st.checkbox(
            "Incluir Hora Numérica Linear (0..23)",
            value=bool(feat["use_raw_hour"]),
            key=f"raw_hr_{model_key}_{ver}",
        )
        st.caption("Útil para testar na prática a diferença contra o relógio circular sin/cos.")

        train_pct = st.slider(
            "Fatia de Treino Cronológico (%)",
            min_value=55,
            max_value=90,
            value=int(round(float(split["train_ratio"]) * 100)),
            step=5,
            key=f"split_ratio_{model_key}_{ver}",
        )
        st.caption(
            f"Divisão atual ({train_pct}% treino / {100 - train_pct}% teste no cenário v1.0), "
            "aplicada aos 3 modelos para comparação justa."
        )

        seed = st.number_input(
            "Semente Aleatória (random_state)",
            min_value=0,
            max_value=9999,
            value=int(split["random_state"]),
            step=1,
            key=f"split_seed_{model_key}_{ver}",
        )
        st.caption("Trava a reprodutibilidade matemática de árvores aleatórias.")

        hp_updated = dict(hp_base)
        if model_key == "Random_Forest":
            hp_updated["min_samples_leaf"] = st.number_input(
                "Mínimo de Amostras por Folha (min_samples_leaf)",
                min_value=1,
                max_value=50,
                value=int(hp_base.get("min_samples_leaf", 1)),
                step=1,
                key=f"hp_leaf_{model_key}_{ver}",
            )
            st.caption("Exige mais horas por regra final; valores de 3 a 10 reduzem overfitting.")
        elif model_key == "Hist_Gradient_Boosting":
            hp_updated["max_depth"] = st.number_input(
                "Profundidade Máxima das Árvores (0 = livre)",
                min_value=0,
                max_value=30,
                value=int(hp_base.get("max_depth", 0)),
                step=1,
                key=f"hp_hdepth_{model_key}_{ver}",
            )
            st.caption("Limitar a profundidade (ex.: 4 a 8) ajuda a evitar decoreba no treino.")

    return {
        "rolling_std_windows": roll_stds,
        "use_raw_hour": use_raw,
        "train_ratio": train_pct / 100.0,
        "random_state": seed,
        "hyperparameters": hp_updated,
    }


def _render_model_form(
    model_key: str,
    cfg: Dict[str, Any],
    ver: int,
    active_scenario: str,
) -> Dict[str, Any]:
    feat = cfg["features"]
    split = cfg["split"]
    hp = cfg["hyperparameters"]
    supports_gen = scenario_supports_generation(active_scenario)

    col_ml, col_dom = st.columns([1.25, 1.0])
    with col_ml:
        st.markdown("#### 1️⃣ Hiperparâmetros de ML *(Você Configura)*")
        st.markdown("**Engenharia Temporal (Memória & Relógio)**")
        lag_opts = sorted(set(PRESET_LAGS) | set(feat["power_lags"]))
        lags = st.multiselect(
            "Lags de Consumo t-k (horas)",
            options=lag_opts,
            default=feat["power_lags"],
            key=f"lags_{model_key}_{ver}",
        )
        st.caption(
            "Memória autoregressiva: `1` = 1h atrás, `24` = ontem na mesma hora, "
            "`168` = semana passada (no cenário v4 são usados apenas lags ≤ 24h)."
        )

        mean_opts = sorted(set(PRESET_ROLL_MEANS) | set(feat["rolling_mean_windows"]))
        roll_means = st.multiselect(
            "Médias Móveis (horas)",
            options=mean_opts,
            default=feat["rolling_mean_windows"],
            key=f"rmean_{model_key}_{ver}",
        )
        st.caption(
            "Suaviza picos isolados mostrando ao modelo o patamar médio das últimas N horas."
        )

        use_cyc = st.checkbox(
            "Usar Relógio Circular (hour_sin / hour_cos)",
            value=bool(feat["use_cyclical_hour"]),
            key=f"cyc_{model_key}_{ver}",
        )
        st.caption("Conecta 23h à 0h em círculo para o modelo entender o ciclo contínuo do dia.")

        st.markdown("**Ajuste de Aprendizado do Algoritmo**")
        hp_main = _render_essential_hyperparams(model_key, hp, ver)

    with col_dom:
        st.markdown("#### 2️⃣ Covariáveis *(Dados Reais Imutáveis)*")
        st.caption(
            "As leituras vêm direto do Excel e **não são alteradas**; marque quais "
            "covariáveis exógenas entram como entrada no modelo:"
        )
        if not supports_gen:
            st.warning(
                "No cenário **v4 Oficial**, apenas `Temperatura (temp_c)` existe no arquivo; "
                "Geração Solar FV e Tensão/Corrente são desativadas automaticamente."
            )

        use_temp = st.checkbox(
            "Temperatura Externa (temp_c)",
            value=bool(feat["use_temperature"]),
            key=f"dom_temp_{model_key}_{ver}",
        )
        st.caption("Medição externa (°C). Ajuda a associar dias frios/quentes à carga.")

        use_gen = st.checkbox(
            "Geração Solar FV (gen_w)",
            value=bool(feat["use_generation"]),
            key=f"dom_gen_{model_key}_{ver}",
            disabled=not supports_gen,
        )
        st.caption("Potência fotovoltaica medida (W). Indica insolação e rotina diurna do prédio.")

        use_elec = st.checkbox(
            "Tensão & Corrente Anteriores (t-1)",
            value=bool(feat["use_electrical_lags"]),
            key=f"dom_elec_{model_key}_{ver}",
            disabled=not supports_gen,
        )
        st.caption(
            "Leituras elétricas da hora passada (V e A), usadas sem vazamento da hora atual."
        )

        adv = _render_advanced_tuning_expander(model_key, feat, split, hp_main, ver)

        with st.expander("🧭 Guia Rápido: Hiperparâmetros de ML vs. Covariáveis"):
            df_tax = pd.DataFrame(get_parameter_taxonomy())[["variavel", "escopo", "mutabilidade"]]
            df_tax.columns = ["Variável / Hiperparâmetro", "Classificação", "Controle"]
            components_module.render_explained_dataframe(df_tax)

    return sanitize_model_config(
        model_key,
        {
            "features": {
                "power_lags": lags,
                "rolling_mean_windows": roll_means,
                "rolling_std_windows": adv["rolling_std_windows"],
                "use_cyclical_hour": use_cyc,
                "use_raw_hour": adv["use_raw_hour"],
                "use_temperature": use_temp,
                "use_generation": use_gen,
                "use_electrical_lags": use_elec,
            },
            "split": {
                "evaluation_scenario": active_scenario,
                "train_ratio": adv["train_ratio"],
                "random_state": adv["random_state"],
                "context_hours": split.get("context_hours", 72),
                "horizon_hours": split.get("horizon_hours", 168),
            },
            "hyperparameters": adv["hyperparameters"],
        },
    )


def _render_lab_actions(
    selected_model: str,
    edited_configs: Dict[str, Dict[str, Any]],
    criterion: str,
    active_scenario: str,
) -> None:
    st.markdown("---")
    b1, b2, b3, b4 = st.columns([1.2, 1.0, 1.0, 1.0])
    with b1:
        if st.button(
            "🚀 Salvar & Treinar Modelos",
            type="primary",
            width="stretch",
            key="btn_lab_train",
            help="Salva os hiperparâmetros e covariáveis, treina os 3 modelos e atualiza gráficos.",
        ):
            model_label = MODEL_DISPLAY_NAMES[selected_model]
            queue_lab_action(
                "train_configs",
                f"Treinando modelos com novos ajustes para {model_label}...",
                {
                    "configs": edited_configs,
                    "message": f"✅ Hiperparâmetros aplicados para {model_label}.",
                },
            )
    with b2:
        if st.button(
            "🏆 Melhor Deste Modelo",
            width="stretch",
            key="btn_lab_reset_one",
            help="Restaura o campeão Multi-Critério deste modelo no cenário atual.",
        ):
            queue_lab_action(
                "reset_one",
                f"Restaurando Campeão de {MODEL_DISPLAY_NAMES[selected_model]}...",
                {
                    "model_key": selected_model,
                    "criterion": criterion,
                    "scenario": active_scenario,
                },
            )
    with b3:
        if st.button(
            "🏆 Melhores de TODOS",
            width="stretch",
            key="btn_lab_reset_all",
            help="Restaura os 3 modelos para seus respectivos campeões do cenário atual.",
        ):
            queue_lab_action(
                "reset_all",
                "Restaurando os 3 Campeões Multi-Critério e recalculando previsão...",
                {"criterion": criterion, "scenario": active_scenario},
            )
    with b4:
        if st.button(
            "🔄 Padrão Inicial",
            width="stretch",
            key="btn_lab_reset_factory",
            help="Volta os 3 modelos para os hiperparâmetros iniciais de fábrica (baseline).",
        ):
            queue_lab_action(
                "reset_factory",
                "Restaurando configuração inicial de fábrica e recalculando modelos...",
                {"scenario": active_scenario},
            )


def _render_lab_tab(
    manager: CycleManager,
    criterion: str,
    active_scenario: str,
) -> None:
    st.info(
        "**Para que serve esta aba:** teste hipóteses alterando Hiperparâmetros de ML ou ativando "
        "Covariáveis e clique em **Salvar & Treinar** para ver o impacto no cenário selecionado."
    )

    active_configs = manager.db.load_active_configs()
    ver = _get_ui_version()

    c_sel, c_badge = st.columns([1.4, 1.0])
    with c_sel:
        selected_model = st.radio(
            "1. Escolha o modelo que deseja configurar:",
            options=list(MODEL_KEYS),
            format_func=lambda k: MODEL_DISPLAY_NAMES[k],
            horizontal=True,
            key="lab_selected_model",
        )
    with c_badge:
        winner = manager.db.select_champion_run(
            selected_model,
            criterion=criterion,
            train_ratio=float(active_configs[selected_model]["split"]["train_ratio"]),
            evaluation_scenario=active_scenario,
        )
        if winner:
            wm = winner["entry"].get("metrics", {})
            score = wm.get("multi_criteria_score", 0)
            st.success(
                f"🏆 Campeão em {SCENARIO_SHORT_LABELS.get(active_scenario, active_scenario)} "
                f"({winner['run_id']}): Nota **{score:.1f}** "
                f"· RMSE **{wm.get('rmse', 0):.1f} W** · MAE **{wm.get('mae', 0):.1f} W**"
            )

    edited_configs: Dict[str, Dict[str, Any]] = deepcopy(active_configs)
    with st.container(border=True):
        edited_configs[selected_model] = _render_model_form(
            selected_model,
            active_configs[selected_model],
            ver,
            active_scenario,
        )
        shared_split = edited_configs[selected_model]["split"]
        for key in MODEL_KEYS:
            edited_configs[key]["split"]["evaluation_scenario"] = active_scenario
            edited_configs[key]["split"]["train_ratio"] = shared_split["train_ratio"]
            edited_configs[key]["split"]["context_hours"] = shared_split["context_hours"]
            edited_configs[key]["split"]["horizon_hours"] = shared_split["horizon_hours"]
        _render_lab_actions(selected_model, edited_configs, criterion, active_scenario)


def _format_best_rows(champions_map: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for idx, (key, entry) in enumerate(rank_benchmarking_models(champions_map)):
        cfg = entry.get("config", {})
        feat = cfg.get("features", {})
        metrics = entry.get("metrics", {})
        tr_metrics = entry.get("train_metrics", {})
        diag = entry.get("learning_diagnosis", {})
        rows.append(
            {
                "Posição": format_rank_badge(idx),
                "Modelo": charts_module.MODEL_UI_META.get(key, {}).get(
                    "short", entry.get("display_name", key)
                ),
                "Nota Multi-Critério": f"{metrics.get('multi_criteria_score', 0.0):.1f}/100",
                "RMSE Treino (W)": tr_metrics.get("rmse", "-"),
                "RMSE Teste (W)": metrics.get("rmse", "-"),
                "MAE Teste (W)": metrics.get("mae", "-"),
                "Diagnóstico": diag.get("status", "-"),
                "Lags (h)": str(feat.get("power_lags", [])),
                "Nº Variáveis": entry.get("num_features", 0),
                "Run ID": entry.get("run_id", "-"),
            }
        )
    return rows


def _format_delta_label(delta: Any) -> str:
    if delta is None:
        return "Base (1ª)"
    val = float(delta)
    if val < 0:
        return f"🟢 {val:+.1f} W"
    if val > 0:
        return f"🔴 {val:+.1f} W"
    return "0.0 W"


def _format_history_rows(runs: List[Dict[str, Any]], active_run_id: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for run in runs[:40]:
        models = run.get("models", {})
        rid = str(run.get("run_id", "-"))
        sc = sanitize_scenario(run.get("evaluation_scenario"))
        rid_label = f"🟢 {rid} (Ativa)" if rid == active_run_id else rid
        for key in MODEL_KEYS:
            m_info = models.get(key)
            if not isinstance(m_info, dict):
                continue
            metrics = m_info.get("metrics", {})
            tr_metrics = m_info.get("train_metrics", {})
            diag = m_info.get("learning_diagnosis", {})
            err_diag = m_info.get("error_diagnostics", {})
            feat = m_info.get("config", {}).get("features", {})
            rows.append(
                {
                    "Run ID": rid_label,
                    "Cenário": SCENARIO_SHORT_LABELS.get(sc, sc),
                    "Modelo": charts_module.MODEL_UI_META.get(key, {}).get(
                        "short", MODEL_DISPLAY_NAMES[key]
                    ),
                    "Nota Multi-Critério": f"{metrics.get('multi_criteria_score', 0.0):.1f}/100",
                    "RMSE Treino (W)": tr_metrics.get("rmse", "-"),
                    "RMSE Teste (W)": metrics.get("rmse", "-"),
                    "Δ vs Anterior": _format_delta_label(m_info.get("delta_vs_prev_rmse_w")),
                    "Acerto ≤ 200 W": f"{err_diag.get('hit_rate_200w_pct', 0.0):.1f}%",
                    "Diagnóstico": diag.get("status", "-"),
                    "Lags (h)": str(feat.get("power_lags", [])),
                    "Recorde?": "🏆 Sim" if m_info.get("new_record") else "Não",
                }
            )
    return rows


def _render_history_tab(
    manager: CycleManager,
    criterion: str,
    active_scenario: str,
    active_run_id: str,
) -> None:
    st.info(
        "**Para que serve esta aba:** compara rodadas salvas no banco (`data/db/`), permite "
        "carregar experimentos passados ou limpar o histórico mantendo somente o Campeão geral."
    )

    best_registry = manager.db.load_best_registry()
    champions_map = (
        best_registry.get("champions_by_scenario", {}).get(active_scenario, {}).get(criterion)
        or best_registry.get("champions_by_criterion", {}).get(criterion)
        or best_registry.get("best_by_model", {})
    )
    sc_label = SCENARIO_SHORT_LABELS.get(active_scenario, active_scenario)
    st.markdown(f"#### 🏆 Campeões em `{sc_label}` — {SELECTION_CRITERIA[criterion]}")
    best_rows = _format_best_rows(champions_map)
    if best_rows:
        components_module.render_explained_dataframe(pd.DataFrame(best_rows))

    runs = manager.db.load_experiment_runs()
    st.markdown("#### 🧪 Histórico de Rodadas (`experiment_runs.json`)")
    history_rows = _format_history_rows(runs, active_run_id=active_run_id)
    if history_rows:
        components_module.render_explained_dataframe(pd.DataFrame(history_rows))

        run_ids = [str(r.get("run_id")) for r in runs if r.get("run_id")]
        if run_ids:
            c_r1, c_r2, c_r3 = st.columns([1.6, 1.0, 1.2])
            with c_r1:
                chosen_run = st.selectbox(
                    "Reproduzir parâmetros de uma rodada específica:",
                    options=run_ids,
                    key="hist_restore_run_id",
                )
            with c_r2:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("⏪ Carregar Rodada", width="stretch", key="btn_restore_run_id"):
                    queue_lab_action(
                        "restore_run",
                        f"Carregando parâmetros da rodada `{chosen_run}` e treinando modelos...",
                        {"run_id": chosen_run, "scenario": active_scenario},
                    )
            with c_r3:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button(
                    "🧹 Limpar Histórico (Manter Só Campeão)",
                    width="stretch",
                    key="btn_compact_champion",
                    help=(
                        "Remove todas as rodadas antigas do experiment_runs.json, preserva "
                        "somente a rodada Campeã Multi-Critério (renumerada para run_0001) e "
                        "sincroniza o gráfico principal."
                    ),
                ):
                    queue_lab_action(
                        "compact_champion",
                        "Limpando histórico e mantendo somente o Campeão geral (`run_0001`)...",
                        {"scenario": active_scenario},
                    )
    else:
        st.info("Nenhum experimento registrado ainda.")


def render_research_workbench(
    root_dir: str,
    zenodo_data: Dict[str, Any],
    manager: CycleManager,
) -> None:
    """Renderiza a bancada de pesquisa organizada em 3 abas claras e sem poluição visual."""
    _ = root_dir
    st.markdown("---")
    st.markdown("## 🔬 Bancada de Pesquisa & Experimentos")

    feedback = st.session_state.pop("lab_feedback", None)
    if feedback:
        st.success(feedback)

    criterion = "multi_criteria"
    active_scenario = sanitize_scenario(zenodo_data.get("evaluation_scenario"))
    active_run_id = str(zenodo_data.get("active_run_id", "-"))
    st.caption(
        f"🎯 **Critério:** {SELECTION_CRITERIA[criterion]} — "
        f"{CRITERION_DESCRIPTIONS[criterion]}"
    )

    tab_diag, tab_lab, tab_hist = st.tabs(
        [
            "🎓 Diagnóstico (Treino vs. Teste & Onde Erra)",
            "🧪 Laboratório de Parâmetros (Testar Hipóteses)",
            "🗄️ Histórico & Comparação de Experimentos",
        ]
    )

    with tab_diag:
        _render_diagnostics_tab(zenodo_data)
    with tab_lab:
        _render_lab_tab(manager, criterion, active_scenario)
    with tab_hist:
        _render_history_tab(manager, criterion, active_scenario, active_run_id)


def render_experiment_db_view(db: ExperimentDatabase) -> None:
    """Exibe os JSONs brutos do banco de dados para auditoria técnica."""
    st.markdown("### 🗄️ Auditoria dos Arquivos do Banco (`data/db/`)")
    with st.expander("🔍 Inspecionar JSONs Brutos (`data/db/`)"):
        tab_active, tab_best, tab_runs = st.tabs(
            ["active_config.json", "best_models_registry.json", "experiment_runs.json"]
        )
        with tab_active:
            st.json(db.load_active_configs(), expanded=False)
        with tab_best:
            st.json(db.load_best_registry(), expanded=False)
        with tab_runs:
            st.json(db.load_experiment_runs()[:20], expanded=False)
