"""Aplicação Monolítica Full Stack em Python (Streamlit) para o Desafio Zenodo 2025."""

import importlib
import os
import shutil
import sys
from typing import Any, Dict

import pandas as pd
import streamlit as st

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import src.ui.charts as charts_module  # noqa: E402
import src.ui.components as components_module  # noqa: E402
from src.pipelines.cycle_manager import CycleManager  # noqa: E402
from src.utils.json_io import load_json  # noqa: E402


@st.cache_data
def load_zenodo_results(base_path: str, file_mtime: float = 0.0) -> Dict[str, Any]:
    """Carrega o JSON do pipeline Zenodo em cache, invalidando quando o arquivo muda."""
    _ = file_mtime
    fpath = os.path.join(base_path, "data", "cycles", "zenodo_forecast_results.json")
    return load_json(fpath) if os.path.exists(fpath) else {}


def restore_baseline_data(root_dir: str) -> None:
    """Restaura o dataset original de referência do Zenodo a partir do baseline."""
    baseline_zenodo = os.path.join(root_dir, "data", "baseline", "zenodo")
    target_zenodo = os.path.join(root_dir, "data", "zenodo")

    if os.path.exists(baseline_zenodo):
        os.makedirs(target_zenodo, exist_ok=True)
        for fname in os.listdir(baseline_zenodo):
            src_file = os.path.join(baseline_zenodo, fname)
            if os.path.isfile(src_file):
                shutil.copy2(src_file, os.path.join(target_zenodo, fname))


def _render_sidebar_pipeline_controls(root_dir: str) -> None:
    """Renderiza controles de execução do pipeline Zenodo com logs ao vivo."""
    st.markdown("---")
    st.markdown("**⚙️ Controle de Pipeline:**")

    if "pipeline_running" not in st.session_state:
        st.session_state.pipeline_running = False
    if "pipeline_logs" not in st.session_state:
        st.session_state.pipeline_logs = []

    def start_pipeline() -> None:
        st.session_state.pipeline_running = True
        st.session_state.pipeline_logs = []

    btn_label = (
        "⏳ Executando Pipeline..."
        if st.session_state.pipeline_running
        else "⚡ Executar Previsão (Zenodo)"
    )

    st.button(
        btn_label,
        key="btn_run_pipeline_sidebar",
        disabled=st.session_state.pipeline_running,
        help="Executa o pipeline Zenodo 2025 e atualiza métricas, JSON e gráficos.",
        width="stretch",
        on_click=start_pipeline,
    )

    if st.button(
        "🔄 Restaurar Originais (Reset)",
        key="btn_reset_baseline_sidebar",
        disabled=st.session_state.pipeline_running,
        help="Restaura o dataset original do Zenodo e reexecuta o pipeline.",
        width="stretch",
    ):
        with st.spinner("Restaurando dataset oficial Zenodo e recalculando métricas..."):
            restore_baseline_data(root_dir)
            manager = CycleManager(root_dir)
            manager.run_all()
            st.cache_data.clear()
        st.success("✅ Dataset oficial Zenodo restaurado com sucesso!")
        st.rerun()

    st.caption(
        "💡 Para upload de novos dados (.xlsx), acesse a aba **Auditoria do Pipeline (JSON)**."
    )

    log_placeholder = st.empty()

    if st.session_state.pipeline_running:
        live_logs = []

        def live_callback(msg: str) -> None:
            live_logs.append(msg)
            log_placeholder.code("\n".join(live_logs), language="bash")

        try:
            live_callback("[Início] Inicializando executor do pipeline Zenodo...")
            manager = CycleManager(root_dir)
            manager.run_all(callback=live_callback)
            st.cache_data.clear()
            live_callback("[Concluído] Cache renovado e dashboard atualizado!")
            st.session_state.pipeline_logs = live_logs
        except Exception as err:
            live_callback(f"[ERRO] Falha na execução: {err}")
            st.session_state.pipeline_logs = live_logs
        finally:
            st.session_state.pipeline_running = False
            st.rerun()

    elif st.session_state.pipeline_logs:
        with st.expander("📋 Logs da Execução", expanded=True):
            st.code("\n".join(st.session_state.pipeline_logs), language="bash")


def _render_download_item(path: str, label: str, file_name: str, mime: str) -> None:
    if os.path.exists(path):
        with open(path, "rb") as file:
            st.download_button(
                label,
                data=file.read(),
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
            os.path.join(root_dir, "data", "cycles", "zenodo_forecast_results.json"),
            "📋 Auditoria Zenodo (JSON)",
            "zenodo_forecast_results.json",
            "application/json",
        )


def _render_data_ingestion(root_dir: str) -> None:
    """Renderiza interface para ingestão de novos dados do Zenodo."""
    with st.expander("📥 Ingestão de Novos Dados (Retreinar Modelos)", expanded=False):
        st.markdown(
            "Carregue novas séries temporais do **Zenodo Smart Building (.xlsx)** "
            "para alimentar e retreinar os modelos preditivos."
        )

        new_file = st.file_uploader(
            "Envie novo arquivo Excel do Smart Building (substitui data_v1.0.xlsx):",
            type=["xlsx"],
            key="uploader_zenodo",
        )
        if new_file is not None and st.button("💾 Ingerir Zenodo & Recalcular", key="btn_save_zen"):
            dest_path = os.path.join(root_dir, "data", "zenodo", "data_v1.0.xlsx")
            with open(dest_path, "wb") as f:
                f.write(new_file.getbuffer())
            with st.spinner("Processando novo dataset e retreinando modelos..."):
                manager = CycleManager(root_dir)
                manager.run_all()
                st.cache_data.clear()
            st.success("✅ Novo dataset Zenodo ingerido e modelos retreinados!")
            st.rerun()


def _render_forecast_page(zenodo_data: Dict[str, Any]) -> None:
    """Renderiza a página principal de previsão com hierarquia visual clara."""
    st.title("⚡ Previsão de Consumo Elétrico — Smart Building (Zenodo 2025)")
    components_module.render_beginner_guide(
        "<b>Como interpretar este painel:</b> O objetivo do desafio é prever o consumo elétrico "
        "do prédio (<b>linha violeta sólida</b>) com o menor erro possível e no menor tempo. "
        "Quanto mais próxima a linha de um modelo estiver da linha violeta, "
        "<b>mais certeira foi a previsão</b>."
    )

    palette = charts_module.COLOR_PALETTE
    models_bench = zenodo_data.get("models_benchmarking", {})
    best_key = zenodo_data.get("best_model_key", "Hist_Gradient_Boosting")
    best_metrics = models_bench.get(best_key, {}).get("metrics", {})

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        components_module.render_kpi_card(
            "Erro Típico — RMSE (Menor = Melhor)",
            f"{best_metrics.get('rmse', 0):.1f} W",
            f"Campeão: {zenodo_data.get('best_model_name', '-')}",
            accent_color=palette["Hist_Gradient_Boosting"],
        )
    with col2:
        components_module.render_kpi_card(
            "Erro Médio — MAE (Menor = Melhor)",
            f"{best_metrics.get('mae', 0):.1f} W",
            "Desvio médio por hora frente ao consumo real",
            accent_color=palette["Random_Forest"],
        )
    with col3:
        components_module.render_kpi_card(
            "Aderência Global (R²)",
            f"{best_metrics.get('r2', 0) * 100:.1f}%",
            f"Consumo médio real: {zenodo_data.get('mean_test_power_w', 0):.0f} W",
            accent_color=palette["Observado"],
        )
    with col4:
        components_module.render_kpi_card(
            "Velocidade Total (Treino + Previsão)",
            f"{best_metrics.get('runtime_ms', 0):.1f} ms",
            (
                f"Treino: {best_metrics.get('train_time_ms', 0):.1f} ms · "
                f"Inferência: {best_metrics.get('inference_time_ms', 0):.1f} ms"
            ),
            accent_color=palette["Ridge_Linear"],
        )

    with st.container(border=True):
        components_module.render_color_legend(
            [
                ("Consumo Real Medido", palette["Observado"], "━━"),
                ("HistGradientBoosting (Campeão)", palette["Hist_Gradient_Boosting"], "━━"),
                ("Random Forest", palette["Random_Forest"], "╌╌"),
                ("Ridge Linear (Baseline)", palette["Ridge_Linear"], "┈┈"),
            ]
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            show_hgb = st.checkbox("Mostrar HistGradientBoosting (Azul)", value=True)
        with c2:
            show_rf = st.checkbox("Mostrar Random Forest (Verde)", value=True)
        with c3:
            show_ridge = st.checkbox("Mostrar Ridge Linear (Laranja)", value=True)

    fig_zen = charts_module.build_zenodo_chart(
        zenodo_data,
        show_ridge=show_ridge,
        show_rf=show_rf,
        show_hgb=show_hgb,
    )
    st.plotly_chart(fig_zen, width="stretch")

    st.markdown("#### 🎯 Comparação Multi-Critério (Critérios Oficiais Zenodo 2025)")
    b_rows = []
    for _, b_info in models_bench.items():
        bm = b_info["metrics"]
        b_rows.append(
            {
                "Modelo Preditivo": b_info["name"],
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


def main() -> None:
    """Função principal de renderização do dashboard Zenodo 2025."""
    importlib.reload(charts_module)
    importlib.reload(components_module)

    st.set_page_config(
        page_title="PGENE585 - Previsão de Consumo Elétrico (Zenodo 2025)",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    components_module.apply_custom_styles()

    json_path = os.path.join(project_root, "data", "cycles", "zenodo_forecast_results.json")
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
                "Auditoria do Pipeline (JSON)",
            ],
        )

        _render_sidebar_pipeline_controls(project_root)
        _render_sidebar_downloads(project_root)

        st.markdown("---")
        st.caption(
            "Desafio Oficial: **Zenodo 2025 Smart Building** — "
            "Previsão de Consumo Elétrico (`power (W)`) com Avaliação Multi-critério "
            "(RMSE, MAE e Desempenho Computacional)."
        )

    if navigation == "Previsão de Consumo (Zenodo 2025)":
        _render_forecast_page(zenodo_data)
    elif navigation == "Auditoria do Pipeline (JSON)":
        st.title("📋 Auditoria do Pipeline Zenodo 2025 (JSON)")
        st.markdown(
            "Resultados completos de ingestão e avaliação multi-critério persistidos em "
            "`data/cycles/zenodo_forecast_results.json`."
        )
        _render_data_ingestion(project_root)
        components_module.render_cycle_summary(zenodo_data)
        st.json(zenodo_data, expanded=False)


if __name__ == "__main__":
    main()
