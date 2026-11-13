"""Aplicação Monolítica Full Stack em Python (Streamlit) para o Desafio Zenodo Smart Building."""

import os
import shutil
import sys
from typing import Any, Dict

import pandas as pd
import streamlit as st

# Garante acesso aos módulos internos
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.pipelines.cycle_manager import CycleManager  # noqa: E402
from src.ui.charts import build_zenodo_chart  # noqa: E402
from src.ui.components import (  # noqa: E402
    apply_custom_styles,
    render_cycle_summary,
    render_kpi_card,
)
from src.utils.json_io import load_json  # noqa: E402


@st.cache_data
def load_zenodo_cycle(base_path: str) -> Dict[str, Any]:
    """Carrega o JSON do pipeline Zenodo em cache na memória RAM."""
    fpath = os.path.join(base_path, "data", "cycles", "cycle_07_zenodo_smart_building.json")
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
    """Renderiza controles de execução do pipeline Zenodo com logs ao vivo e bloqueio."""
    st.markdown("---")
    st.markdown("**⚙️ Controle de Pipeline (IA):**")

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
        else "⚡ Executar Pipeline (Zenodo)"
    )

    st.button(
        btn_label,
        key="btn_run_pipeline_sidebar",
        disabled=st.session_state.pipeline_running,
        help="Executa o pipeline completo Zenodo e atualiza métricas, JSON e gráficos.",
        use_container_width=True,
        on_click=start_pipeline,
    )

    if st.button(
        "🔄 Restaurar Originais (Reset)",
        key="btn_reset_baseline_sidebar",
        disabled=st.session_state.pipeline_running,
        help="Restaura o dataset original do Zenodo e reexecuta o pipeline.",
        use_container_width=True,
    ):
        with st.spinner("Restaurando dataset oficial Zenodo e recalculando métricas..."):
            restore_baseline_data(root_dir)
            manager = CycleManager(root_dir)
            manager.run_all()
            st.cache_data.clear()
        st.success("✅ Dataset oficial Zenodo restaurado com sucesso!")
        st.rerun()

    st.caption(
        "💡 Para upload de novos dados (.xlsx), acesse a aba "
        "**Auditoria do Pipeline (JSON)**."
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


def _render_sidebar_downloads(root_dir: str) -> None:
    """Renderiza a Central de Downloads com slides e dados Zenodo."""
    st.markdown("---")
    st.markdown("**📥 Central de Downloads:**")
    with st.expander("📦 Baixar Apresentação e Dados", expanded=False):
        # 1. Slides da Apresentação (PDF)
        pdf_path = os.path.join(root_dir, "presentation", "slides_apresentacao.pdf")
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "📊 Slides da Apresentação (PDF)",
                    data=f.read(),
                    file_name="Apresentacao_PGENE585_Aldair_Azevedo.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

        # 2. Slides Editáveis (PPTX)
        pptx_path = os.path.join(root_dir, "presentation", "slides_apresentacao.pptx")
        if os.path.exists(pptx_path):
            with open(pptx_path, "rb") as f:
                st.download_button(
                    "📑 Slides Editáveis (PPTX)",
                    data=f.read(),
                    file_name="Apresentacao_PGENE585_Aldair_Azevedo.pptx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "presentationml.presentation"
                    ),
                    use_container_width=True,
                )

        # 3. Dados Smart Building Zenodo (XLSX)
        zenodo_path = os.path.join(root_dir, "data", "zenodo", "data_v1.0.xlsx")
        if os.path.exists(zenodo_path):
            with open(zenodo_path, "rb") as f:
                st.download_button(
                    "🏢 Dados Zenodo (XLSX)",
                    data=f.read(),
                    file_name="dados_zenodo_smart_building.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

        # 4. Resultado JSON do Pipeline Zenodo
        cycle_json = os.path.join(
            root_dir, "data", "cycles", "cycle_07_zenodo_smart_building.json"
        )
        if os.path.exists(cycle_json):
            with open(cycle_json, "rb") as f:
                st.download_button(
                    "📋 Auditoria Zenodo (JSON)",
                    data=f.read(),
                    file_name="cycle_07_zenodo_smart_building.json",
                    mime="application/json",
                    use_container_width=True,
                )


def _render_data_ingestion(root_dir: str) -> None:
    """Renderiza interface para ingestão de novos dados em massa do Zenodo."""
    with st.expander("📥 Ingestão de Novos Dados em Massa (Retreinar Modelos)", expanded=False):
        st.markdown(
            "Carregue novas séries temporais do **Zenodo Smart Building (.xlsx)** "
            "para alimentar e retreinar os modelos de IA."
        )

        new_file = st.file_uploader(
            "Envie novo arquivo Excel do Smart Building (substitui data_v1.0.xlsx):",
            type=["xlsx"],
            key="uploader_zenodo",
        )
        if new_file is not None:
            if st.button("💾 Ingerir Zenodo & Recalcular Modelos", key="btn_save_zenodo"):
                dest_path = os.path.join(root_dir, "data", "zenodo", "data_v1.0.xlsx")
                with open(dest_path, "wb") as f:
                    f.write(new_file.getbuffer())
                with st.spinner("Processando novo dataset e retreinando modelos..."):
                    manager = CycleManager(root_dir)
                    manager.run_all()
                    st.cache_data.clear()
                st.success("✅ Novo dataset Zenodo ingerido e modelos retreinados!")
                st.rerun()


def main() -> None:
    """Função principal de renderização do dashboard Zenodo Smart Building."""
    st.set_page_config(
        page_title="PGENE585 - Smart Building & Energia Solar (Zenodo)",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_custom_styles()

    zenodo_data = load_zenodo_cycle(project_root)

    # Barra lateral de navegação
    with st.sidebar:
        st.markdown("### ⚡ PGENE585 - PPGEE / UFAM")
        st.caption("Transição Energética Sustentável e Mercados de Energia")
        st.markdown("**Aluno:** Aldair da Silva Azevedo  \n**Prof. Dr.:** Kenny Vinente")
        st.markdown("---")

        navigation = st.selectbox(
            "Navegação do Módulo",
            options=[
                "Smart Building & Energia Solar (Zenodo)",
                "Auditoria do Pipeline (JSON)",
            ],
        )

        _render_sidebar_pipeline_controls(project_root)
        _render_sidebar_downloads(project_root)

        st.markdown("---")
        st.caption(
            "Desafio Acadêmico: **Zenodo Smart Building (2025)** — "
            "Previsão de Carga e Geração Solar Fotovoltaica"
        )

    # Módulo 1: Smart Building & Energia Solar (Zenodo)
    if navigation == "Smart Building & Energia Solar (Zenodo)":
        st.title("🏢 Smart Building & Transição Energética (Zenodo 2025)")
        st.markdown(
            "Previsão de consumo predial (com lags temporais $t-1$ e $t-24$), impacto da "
            "**geração solar fotovoltaica distribuída** e análise da **Demanda Líquida** "
            "(Curva do Pato)."
        )

        solar_info = zenodo_data.get("solar_energy_impact", {})
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_kpi_card(
                "Consumo Médio Bruto",
                f"{solar_info.get('mean_consumption_w', 0):.0f} W",
                "Demanda total de eletricidade do edifício",
            )
        with col2:
            render_kpi_card(
                "Geração Solar Média",
                f"{solar_info.get('mean_solar_generation_w', 0):.0f} W",
                "Potência limpa gerada na cobertura solar",
            )
        with col3:
            render_kpi_card(
                "Demanda Líquida",
                f"{solar_info.get('mean_net_demand_w', 0):.0f} W",
                "Carga real puxada da rede (Consumo − Solar)",
            )
        with col4:
            render_kpi_card(
                "Cobertura Solar",
                f"{solar_info.get('solar_coverage_ratio_pct', 0):.1f}%",
                "Parcela do consumo atendida pela energia solar",
            )

        with st.container(border=True):
            col_opt1, col_opt2, col_opt3, col_opt4 = st.columns(4)
            with col_opt1:
                show_ridge = st.checkbox("Previsão Ridge Linear", value=True)
            with col_opt2:
                show_rf = st.checkbox("Previsão Random Forest", value=True)
            with col_opt3:
                show_solar = st.checkbox("Geração Solar Fotovoltaica", value=True)
            with col_opt4:
                show_net = st.checkbox("Demanda Líquida (Curva do Pato)", value=True)

        fig_zen = build_zenodo_chart(
            zenodo_data,
            show_ridge=show_ridge,
            show_rf=show_rf,
            show_solar=show_solar,
            show_net=show_net,
        )
        st.plotly_chart(fig_zen, use_container_width=True)

        st.markdown("#### 🎯 Avaliação Multi-critério dos Modelos de Previsão")
        models_bench = zenodo_data.get("models_benchmarking", {})
        b_rows = []
        for _, b_info in models_bench.items():
            bm = b_info["metrics"]
            b_rows.append(
                {
                    "Modelo": b_info["name"],
                    "RMSE [Erro Quadrático] (W)": bm["rmse"],
                    "MAE [Erro Médio Absoluto] (W)": bm["mae"],
                    "R² Score (Acurácia)": f"{bm['r2']:.3f} ({bm['r2'] * 100:.1f}%)",
                    "Tempo de Execução (ms)": bm["runtime_ms"],
                }
            )
        st.dataframe(pd.DataFrame(b_rows), use_container_width=True, hide_index=True)
        st.caption(
            "💡 **Legenda das Métricas:** "
            "**RMSE** penaliza grandes desvios em Watts; "
            "**MAE** expressa o desvio linear médio da carga em Watts; "
            "**R²** quantifica a precisão global."
        )

    # Módulo 2: Auditoria do Pipeline (JSON)
    elif navigation == "Auditoria do Pipeline (JSON)":
        st.title("📋 Trilha de Auditoria: Pipeline Zenodo em JSON")
        st.markdown(
            "Resultados completos de ingestão, engenharia de atributos e predição persistidos "
            "em `data/cycles/cycle_07_zenodo_smart_building.json`."
        )

        _render_data_ingestion(project_root)

        render_cycle_summary(zenodo_data)
        st.json(zenodo_data, expanded=False)


if __name__ == "__main__":
    main()
