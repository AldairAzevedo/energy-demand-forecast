"""Aplicação Monolítica Full Stack em Python (Streamlit) para o Desafio Zenodo 2025."""

import importlib
import os
import sys
from typing import Any, Dict

import pandas as pd
import streamlit as st

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import src.core.diagnostics as diagnostics_module  # noqa: E402
import src.core.forecasting as forecasting_module  # noqa: E402
import src.core.parameter_schema as schema_module  # noqa: E402
import src.pipelines.cycle_manager as cycle_manager_module  # noqa: E402
import src.pipelines.dataset_loader as dataset_loader_module  # noqa: E402
import src.pipelines.zenodo_pipeline as pipeline_module  # noqa: E402
import src.ui.charts as charts_module  # noqa: E402
import src.ui.components as components_module  # noqa: E402
import src.ui.param_lab as param_lab_module  # noqa: E402
import src.utils.experiment_db as experiment_db_module  # noqa: E402
from src.utils.file_resilience import read_bytes_resilient  # noqa: E402
from src.utils.json_io import load_json  # noqa: E402


def _reload_workspace_modules() -> None:
    """Recarrega módulos em ordem de dependência para evitar classes antigas no hot-reload."""
    for mod in (
        diagnostics_module,
        forecasting_module,
        schema_module,
        dataset_loader_module,
        experiment_db_module,
        pipeline_module,
        cycle_manager_module,
        charts_module,
        components_module,
        param_lab_module,
    ):
        importlib.reload(mod)


@st.cache_data
def load_zenodo_results(base_path: str, file_mtime: float = 0.0) -> Dict[str, Any]:
    """Carrega o JSON do pipeline Zenodo em cache, invalidando quando o arquivo muda."""
    _ = file_mtime
    fpath = os.path.join(base_path, "data", "db", "zenodo_forecast_results.json")
    return load_json(fpath) if os.path.exists(fpath) else {}


def _render_download_item(path: str, label: str, file_name: str, mime: str) -> None:
    if not os.path.exists(path):
        return
    try:
        payload = read_bytes_resilient(path)
    except OSError:
        st.caption(f"⚠️ Arquivo bloqueado em uso no momento: `{file_name}`")
        return
    st.download_button(
        label,
        data=payload,
        file_name=file_name,
        mime=mime,
        width="stretch",
    )


def _render_sidebar_downloads(root_dir: str) -> None:
    """Renderiza a Central de Downloads com slides, enunciado e dados Zenodo."""
    st.markdown("---")
    st.markdown("**📥 Central de Downloads:**")
    with st.expander("📦 Baixar Apresentação e Dados", expanded=False):
        _render_download_item(
            os.path.join(root_dir, "presentation", "slides_apresentacao.pdf"),
            "📊 Slides da Apresentação (PDF)",
            "Apresentacao_PGENE585_Aldair_Azevedo.pdf",
            "application/pdf",
        )
        _render_download_item(
            os.path.join(root_dir, "presentation", "slides_apresentacao.pptx"),
            "📑 Slides Editáveis (PPTX)",
            "Apresentacao_PGENE585_Aldair_Azevedo.pptx",
            ("application/vnd.openxmlformats-officedocument.presentationml.presentation"),
        )
        _render_download_item(
            os.path.join(root_dir, "docs", "zenodo.pdf"),
            "📘 Enunciado Oficial Zenodo (PDF)",
            "zenodo_2025_competition.pdf",
            "application/pdf",
        )
        _render_download_item(
            os.path.join(root_dir, "data", "zenodo", "data_v1.0.xlsx"),
            "🏢 Dados Zenodo (XLSX)",
            "dados_zenodo_smart_building.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        _render_download_item(
            os.path.join(root_dir, "data", "db", "zenodo_forecast_results.json"),
            "📋 Auditoria Zenodo (JSON)",
            "zenodo_forecast_results.json",
            "application/json",
        )


def _format_active_protocol_caption(active_scenario: str, zenodo_data: Dict[str, Any]) -> str:
    """Constrói descrição dinâmica com contagens reais de treino, teste, contexto e pós-corte."""
    tr_n = int(zenodo_data.get("train_samples", 0) or 0)
    te_n = int(zenodo_data.get("test_samples", 0) or 0)
    ctx_h = int(zenodo_data.get("context_hours", 0) or 0)
    hor_h = int(zenodo_data.get("horizon_hours", 0) or 0)
    if tr_n > 0 and te_n > 0 and active_scenario == "v1_internal_split":
        total = tr_n + te_n
        tr_pct = round(100.0 * tr_n / total)
        return (
            f"Treina nos primeiros {tr_pct}% de data_v1.0.xlsx ({tr_n:,} h) e testa nos "
            f"{100 - tr_pct}% finais inéditos ({te_n:,} h), exibindo {ctx_h} h de contexto + "
            f"{hor_h} h após o corte.".replace(",", ".")
        )
    if tr_n > 0 and te_n > 0 and active_scenario == "v1_to_v2":
        msg = (
            f"Treina em data_v1.0.xlsx ({tr_n:,} h), aquece lags no início de v2.0 sem "
            f"vazamento e testa em {te_n:,} h inéditas ({ctx_h} h contexto + {hor_h} h pós-corte)."
        )
        return msg.replace(",", ".")
    if tr_n > 0 and te_n > 0 and active_scenario == "v1_v2_to_v4":
        return (
            f"Treina em v1+v2 ({tr_n:,} h) com hora, temp_c e lags ≤ 24 h; usa {ctx_h} h de "
            f"contexto (Dia 1) e testa {te_n:,} h inéditas (Dias 2–3 de v4).".replace(",", ".")
        )
    return forecasting_module.SCENARIO_DESCRIPTIONS[active_scenario]


def _render_scenario_bar(active_scenario: str, zenodo_data: Dict[str, Any]) -> None:
    """Barra no topo da página para alternar o Cenário de Validação Cross-Dataset."""
    cols = st.columns(len(forecasting_module.EVALUATION_SCENARIOS))
    for col, sc in zip(cols, forecasting_module.EVALUATION_SCENARIOS):
        is_active = sc == active_scenario
        label = forecasting_module.SCENARIO_SHORT_LABELS[sc]
        prefix = "✅ " if is_active else "🔀 "
        with col:
            if st.button(
                f"{prefix}{label}",
                key=f"btn_scenario_{sc}",
                type="primary" if is_active else "secondary",
                width="stretch",
                help=forecasting_module.SCENARIO_DESCRIPTIONS[sc],
            ):
                if not is_active:
                    param_lab_module.queue_lab_action(
                        "switch_scenario",
                        f"Executando cenário **{forecasting_module.SCENARIO_LABELS[sc]}**...",
                        {"scenario": sc},
                    )
    st.caption(
        f"📐 **Protocolo ativo ({forecasting_module.SCENARIO_LABELS[active_scenario]}):** "
        f"{_format_active_protocol_caption(active_scenario, zenodo_data)}"
    )


def _render_chart_covariates_controls(
    zenodo_data: Dict[str, Any],
    active_scenario: str,
) -> None:
    """Switches integrados ao gráfico principal que re-treinam ao alternar covariáveis."""
    has_gen = bool(zenodo_data.get("has_generation", True))
    cov_state = zenodo_data.get("active_covariates", {})
    curr_temp = bool(cov_state.get("use_temperature", True))
    curr_gen = bool(cov_state.get("use_generation", True)) if has_gen else False
    ver = int(st.session_state.get("param_ui_version", 0))

    st.markdown("---")
    c_lbl, c_temp, c_gen = st.columns([1.2, 1.0, 1.0])
    with c_lbl:
        st.markdown("**🎛️ Covariáveis no Modelo *(Impacta a Previsão)***")
        st.caption(
            "Alternar aqui, re-treina e atualiza o gráfico acima "
            "(em sincronia com a aba Laboratório)."
        )
    with c_temp:
        new_temp = st.toggle(
            "🌡️ Temperatura Externa (`temp_c`)",
            value=curr_temp,
            key=f"chart_cov_temp_{ver}",
            help="Ativa/desativa Temperatura no modelo e atualiza o gráfico principal.",
        )
    with c_gen:
        new_gen = st.toggle(
            "☀️ Geração Solar FV (`gen_w`)",
            value=curr_gen,
            disabled=not has_gen,
            key=f"chart_cov_gen_{ver}",
            help=(
                "Ativa/desativa Geração Solar FV no modelo (indisponível no cenário v4 Oficial)."
            ),
        )

    if new_temp != curr_temp or (has_gen and new_gen != curr_gen):
        param_lab_module.queue_lab_action(
            "toggle_covariates",
            "Atualizando Covariáveis e recalculando gráfico principal...",
            {
                "scenario": active_scenario,
                "use_temperature": bool(new_temp),
                "use_generation": bool(new_gen) if has_gen else curr_gen,
            },
        )


def _render_forecast_page(zenodo_data: Dict[str, Any], root_dir: str) -> None:
    """Renderiza a página principal de previsão com hierarquia visual clara."""
    st.title("⚡ Previsão de Consumo Elétrico — Smart Building (Zenodo 2025)")

    active_scenario = forecasting_module.sanitize_scenario(zenodo_data.get("evaluation_scenario"))
    active_run_id = str(zenodo_data.get("active_run_id", "-"))
    scenario_label = forecasting_module.SCENARIO_LABELS[active_scenario]
    cutoff_label = str(zenodo_data.get("cutoff_label", "Horizonte oficial 1h"))

    components_module.render_active_status_strip(active_run_id, scenario_label, cutoff_label)
    _render_scenario_bar(active_scenario, zenodo_data)

    components_module.render_beginner_guide(
        "<b>Como interpretar o gráfico com Ponto de Corte:</b> à esquerda da linha vermelha "
        "está o <b>Contexto Pré-Corte</b> (passado recente que alimenta os lags); à direita "
        "estão as previsões passo a passo (<b>1h à frente</b>) comparadas ao "
        "<b>Consumo Real (linha violeta sólida)</b>.<br>"
        "<b>Por que média horária (W)?</b> As medições de 5 minutos são agrupadas por hora "
        "(padrão da competição), pois na física <b>Energia (Wh) = Potência Média (W) × 1 hora</b>."
    )

    palette = charts_module.COLOR_PALETTE
    ui_meta = charts_module.MODEL_UI_META
    models_bench = zenodo_data.get("models_benchmarking", {})
    ranked_models = (
        diagnostics_module.rank_benchmarking_models(models_bench)
        if models_bench
        else [(k, {}) for k in ui_meta]
    )
    best_key, best_info = ranked_models[0]
    best_metrics = best_info.get("metrics", {})
    best_name = best_info.get("name", zenodo_data.get("best_model_name", "-"))
    best_score = float(best_metrics.get("multi_criteria_score", 0.0))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        components_module.render_kpi_card(
            "Erro Típico — RMSE (Menor = Melhor)",
            f"{best_metrics.get('rmse', 0):.1f} W",
            f"🏆 1º Campeão: {best_name} · Nota {best_score:.1f}/100",
            accent_color=palette.get(best_key, palette["Hist_Gradient_Boosting"]),
        )
    with col2:
        components_module.render_kpi_card(
            "Erro Médio — MAE (Menor = Melhor)",
            f"{best_metrics.get('mae', 0):.1f} W",
            f"Desvio médio por hora ({ui_meta.get(best_key, {}).get('short', best_key)})",
            accent_color=palette.get("Observado", "#8B5CF6"),
        )
    with col3:
        components_module.render_kpi_card(
            "Aderência Global (R²)",
            f"{best_metrics.get('r2', 0) * 100:.1f}%",
            f"Consumo médio real: {zenodo_data.get('mean_test_power_w', 0):.0f} W",
            accent_color=palette.get(best_key, palette["Hist_Gradient_Boosting"]),
        )
    with col4:
        components_module.render_kpi_card(
            "Velocidade Total (Treino + Previsão)",
            f"{best_metrics.get('runtime_ms', 0):.1f} ms",
            (
                f"Treino: {best_metrics.get('train_time_ms', 0):.1f} ms · "
                f"Inferência: {best_metrics.get('inference_time_ms', 0):.1f} ms"
            ),
            accent_color=palette.get("Temperatura", "#F59E0B"),
        )

    with st.container(border=True):
        legend_items = [("Consumo Real Medido", palette["Observado"], "━━")]
        for idx, (m_key, m_info) in enumerate(ranked_models):
            meta = ui_meta.get(m_key, {})
            short = meta.get("short", m_key)
            tag = "🏆 1º Campeão" if idx == 0 else f"{idx + 1}º"
            score_val = m_info.get("metrics", {}).get("multi_criteria_score")
            suffix = f" ({score_val:.1f})" if score_val is not None else ""
            legend_items.append(
                (
                    f"{tag} · {short}{suffix}",
                    palette.get(m_key, "#94A3B8"),
                    meta.get("pill_symbol", "━━"),
                )
            )
        components_module.render_color_legend(legend_items)

        visibility: Dict[str, bool] = {}
        chk_cols = st.columns(len(ranked_models))
        for idx, (col, (m_key, m_info)) in enumerate(zip(chk_cols, ranked_models)):
            meta = ui_meta.get(m_key, {})
            prefix = "🏆 1º" if idx == 0 else f"{idx + 1}º"
            m_rmse = m_info.get("metrics", {}).get("rmse")
            rmse_help = f"RMSE: {m_rmse:.1f} W" if m_rmse is not None else None
            with col:
                visibility[m_key] = st.checkbox(
                    f"Mostrar {prefix} {meta.get('short', m_key)} ({meta.get('color_label', '')})",
                    value=True,
                    key=f"show_model_{m_key}",
                    help=rmse_help,
                )

        fig_zen = charts_module.build_zenodo_chart(
            zenodo_data,
            show_ridge=visibility.get("Ridge_Linear", True),
            show_rf=visibility.get("Random_Forest", True),
            show_hgb=visibility.get("Hist_Gradient_Boosting", True),
        )
        st.plotly_chart(fig_zen, width="stretch")
        _render_chart_covariates_controls(zenodo_data, active_scenario)

    st.markdown("#### 🎯 Classificação Dinâmica & Comparação Multi-Critério (Zenodo 2025)")
    b_rows = []
    for idx, (m_key, b_info) in enumerate(ranked_models):
        if not b_info:
            continue
        bm = b_info["metrics"]
        meta = ui_meta.get(m_key, {})
        b_rows.append(
            {
                "Posição": diagnostics_module.format_rank_badge(idx),
                "Modelo Preditivo": f"{meta.get('short', b_info.get('name', m_key))}",
                "Nota (0–100)": f"{float(bm.get('multi_criteria_score', 0.0)):.2f}",
                "Erro RMSE (W)": bm["rmse"],
                "Erro MAE (W)": bm["mae"],
                "Aderência (R²)": f"{bm['r2'] * 100:.1f}%",
                "Treino (ms)": bm["train_time_ms"],
                "Inferência (ms)": bm["inference_time_ms"],
                "Tempo Total (ms)": bm["runtime_ms"],
            }
        )
    st.dataframe(pd.DataFrame(b_rows), width="stretch", hide_index=True)
    st.caption(
        "💡 **Guia rápido:** Menor **RMSE** e **MAE** indicam previsões mais próximas da "
        "realidade em Watts; menor **Tempo Total** indica maior eficiência computacional."
    )

    param_lab_module.render_research_workbench(
        root_dir, zenodo_data, cycle_manager_module.CycleManager(root_dir)
    )


def main() -> None:
    """Função principal de renderização do dashboard Zenodo 2025."""
    _reload_workspace_modules()

    st.set_page_config(
        page_title="PGENE585 - Previsão de Consumo Elétrico (Zenodo 2025)",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    components_module.apply_custom_styles()
    param_lab_module.process_pending_action(project_root)

    json_path = os.path.join(project_root, "data", "db", "zenodo_forecast_results.json")
    mtime = os.path.getmtime(json_path) if os.path.exists(json_path) else 0.0
    zenodo_data = load_zenodo_results(project_root, mtime)

    with st.sidebar:
        st.markdown("### ⚡ PGENE585 - PPGEE / UFAM")
        st.caption("Transição Energética Sustentável e Mercados de Energia")
        st.markdown("**Aluno:** Aldair da Silva Azevedo  \n**Prof. Dr.:** Kenny Vinente")
        st.markdown("---")

        navigation = st.selectbox(
            "Navegação do Módulo",
            options=[
                "Previsão de Consumo (Zenodo 2025)",
                "Auditoria Técnica (JSON)",
            ],
        )

        _render_sidebar_downloads(project_root)

        st.markdown("---")
        st.caption(
            "Desafio Oficial: **Zenodo 2025 Smart Building** — "
            "Previsão de Consumo Elétrico (`power (W)`) com Avaliação Multi-critério "
            "(RMSE, MAE e Desempenho Computacional)."
        )

    if navigation == "Previsão de Consumo (Zenodo 2025)":
        _render_forecast_page(zenodo_data, project_root)
    elif navigation == "Auditoria Técnica (JSON)":
        st.title("📋 Auditoria Técnica dos JSONs (Zenodo 2025)")
        st.markdown("Inspeção direta dos arquivos de persistência unificados em `data/db/`.")
        manager = cycle_manager_module.CycleManager(project_root)
        param_lab_module.render_experiment_db_view(manager.db)
        components_module.render_cycle_summary(zenodo_data)
        st.json(zenodo_data, expanded=False)


if __name__ == "__main__":
    main()
