"""Aplicação Monolítica Full Stack em Python (Streamlit) para Análise de Demanda de Energia."""

import os
import sys
from typing import Any, Dict

import pandas as pd
import streamlit as st

# Garante acesso aos módulos internos
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui.charts import (  # noqa: E402
    build_cmu_q5_chart,
    build_cmu_q6_comparison_chart,
    build_residuals_chart,
    build_zenodo_chart,
)
from src.ui.components import (  # noqa: E402
    apply_custom_styles,
    render_cycle_summary,
    render_kpi_card,
)
from src.utils.json_io import load_json  # noqa: E402


@st.cache_data
def load_all_cycles(base_path: str) -> Dict[str, Any]:
    """Carrega todos os 7 arquivos de ciclos em cache na memória RAM para resposta ultra-rápida."""
    cycles_dir = os.path.join(base_path, "data", "cycles")
    files_map = {
        "cycle_01": "cycle_01_cmu_q5_raw.json",
        "cycle_02": "cycle_02_cmu_q5_fitted_models.json",
        "cycle_03": "cycle_03_cmu_q6_cleaned_weather.json",
        "cycle_04": "cycle_04_cmu_q6_interpolated_sync.json",
        "cycle_05": "cycle_05_cmu_q6_daily_features.json",
        "cycle_06": "cycle_06_cmu_q6_multivariate_comparison.json",
        "cycle_07": "cycle_07_zenodo_smart_building.json",
    }
    loaded = {}
    for key, fname in files_map.items():
        fpath = os.path.join(cycles_dir, fname)
        if os.path.exists(fpath):
            loaded[key] = load_json(fpath)
        else:
            loaded[key] = {}
    return loaded


def main() -> None:
    """Função principal de renderização do dashboard monolítico."""
    st.set_page_config(
        page_title="PGENE585 - Previsão de Demanda & Transição Energética",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_custom_styles()

    cycles_data = load_all_cycles(project_root)

    # Barra lateral de navegação
    with st.sidebar:
        st.markdown("### ⚡ PGENE585 - PPGEE / UFAM")
        st.caption("Transição Energética Sustentável e Mercados de Energia")
        st.markdown("**Aluno:** Aldair da Silva Azevedo  \n**Prof. Dr.:** Kenny Vinente")
        st.markdown("---")

        navigation = st.radio(
            "Selecione o Módulo de Análise:",
            options=[
                "Laboratório de Modelos (CMU Item 5)",
                "Engenharia de Features (CMU Item 6)",
                "Smart Building & Solar (Zenodo 2025)",
                "Auditoria dos 7 Ciclos (JSON)",
            ],
            index=0,
        )

        st.markdown("---")
        st.caption("Arquitetura Monolítica 100% Python | POO & SOLID")

    # Módulo 1: Laboratório de Modelos (CMU Item 5)
    if navigation == "Laboratório de Modelos (CMU Item 5)":
        st.title("🔬 Laboratório de Modelos: Demanda de Pico vs. Temperatura")
        st.markdown(
            "Análise comparativa das **4 arquiteturas de regressão** sob as funções de perda "
            "**L2 (Mínimos Quadrados)** e **L1 (Perda Absoluta Robusta - LAD)**."
        )

        c1_data = cycles_data.get("cycle_01", {})
        c2_data = cycles_data.get("cycle_02", {})

        if not c2_data:
            st.error("Dados do Ciclo 02 não encontrados. Execute o pipeline primeiro.")
            return

        model_options = ["Linear", "Polinomial_d5", "RBF", "Kernel_Gaussiano"]

        # Painel Superior: Controles do Gráfico Principal
        with st.container(border=True):
            col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1.4, 2.5, 1.1])
            with col_ctrl1:
                loss_choice = st.radio(
                    "Função de Perda:",
                    options=["L2", "L1"],
                    format_func=lambda x: (
                        "L2 (Squared Loss - OLS)" if x == "L2" else "L1 (Absolute Loss - LAD)"
                    ),
                    horizontal=False,
                )
            with col_ctrl2:
                selected_models = st.multiselect(
                    "Modelos a Exibir (Sobreposição):",
                    options=model_options,
                    default=model_options,
                    format_func=lambda x: {
                        "Linear": "1. Linear Simples",
                        "Polinomial_d5": "2. Polinomial (Grau 5)",
                        "RBF": "3. RBF (5 Centros)",
                        "Kernel_Gaussiano": "4. Kernel Gaussiano Ridge",
                    }.get(x, x),
                )
            with col_ctrl3:
                st.write("**Demanda Real:**")
                show_scatter = st.checkbox(
                    "Exibir 1.460 Pontos",
                    value=True,
                    help="Exibe as medições reais de consumo em GW da Duquesne Light.",
                )

        # Gráfico Principal
        fig_main = build_cmu_q5_chart(
            c1_data,
            c2_data,
            selected_models,
            loss_type=loss_choice,
            show_scatter=show_scatter,
        )
        st.plotly_chart(fig_main, use_container_width=True)

        # Tabela e Cards de Métricas
        st.markdown("#### 📊 Desempenho Quantitativo dos Modelos")
        models_dict = c2_data.get("models", {}).get(loss_choice, {})
        rows = []
        for m_key in model_options:
            if m_key in models_dict:
                info = models_dict[m_key]
                m = info["metrics"]
                r2_val = m["r2"]
                rmse_val = m["rmse"]
                mae_val = m["mae"]
                rows.append(
                    {
                        "Modelo": info["model_name"],
                        "R² Score (Acurácia)": f"{r2_val:.3f} ({r2_val * 100:.1f}%)",
                        "RMSE [Erro Quadrático]": f"{rmse_val:.3f} GW ({rmse_val * 1000:.0f} MW)",
                        "MAE [Erro Médio Diário]": f"{mae_val:.3f} GW ({mae_val * 1000:.0f} MW)",
                        "Tempo de Ajuste": f"{m['runtime_ms']:.1f} ms",
                    }
                )
        df_metrics = pd.DataFrame(rows)
        st.dataframe(df_metrics, use_container_width=True, hide_index=True)

        # Painel de Resíduos Contextualizado
        st.markdown("---")
        col_res_header, col_res_select = st.columns([2.8, 1.2])
        with col_res_select:
            residual_target = st.selectbox(
                "Modelo Inspecionado:",
                options=model_options,
                index=0,
                format_func=lambda x: {
                    "Linear": "1. Linear Simples",
                    "Polinomial_d5": "2. Polinomial (Grau 5)",
                    "RBF": "3. RBF (5 Centros)",
                    "Kernel_Gaussiano": "4. Kernel Gaussiano Ridge",
                }.get(x, x),
            )

        model_label_map = {
            "Linear": "1. Linear Simples",
            "Polinomial_d5": "2. Polinomial (Grau 5)",
            "RBF": "3. RBF (5 Centros)",
            "Kernel_Gaussiano": "4. Kernel Gaussiano Ridge",
        }
        selected_model_name = model_label_map.get(residual_target, residual_target)

        with col_res_header:
            st.markdown("#### 📉 Distribuição de Resíduos")
            st.markdown(
                f"Fórmula: `Resíduo = Demanda Real − Demanda Prevista` &nbsp;•&nbsp; "
                f"Modelo em análise: **:blue[{selected_model_name}]** ({loss_choice})"
            )

        fig_res = build_residuals_chart(c1_data, c2_data, residual_target, loss_type=loss_choice)
        st.plotly_chart(fig_res, use_container_width=True)

    # Módulo 2: Engenharia de Features (CMU Item 6)
    elif navigation == "Engenharia de Features (CMU Item 6)":
        st.title("🛠️ Engenharia de Features: Limpeza, Interpolação e Dados Multivariados")
        st.markdown(
            "Demonstração do pipeline de tratamento de dados de sensores brutos e a "
            "**prova empírica da redução do erro de previsão** ao incluir variáveis climáticas."
        )

        c3_data = cycles_data.get("cycle_03", {})
        c5_data = cycles_data.get("cycle_05", {})
        c6_data = cycles_data.get("cycle_06", {})

        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        with col_kpi1:
            render_kpi_card(
                "Registros Originais",
                f"{c3_data.get('original_records_count', 0):,}",
                "Total de leituras brutas da estação NOAA",
            )
        with col_kpi2:
            render_kpi_card(
                "Sentinelas -9999",
                "100 tratados",
                "Falhas de sensor corrigidas por interpolação",
            )
        with col_kpi3:
            reduction = c6_data.get("comparison", {}).get("mse_reduction_percentage", 0.0)
            render_kpi_card(
                "Redução no MSE",
                f"{reduction}%",
                "Queda no erro ao usar vento, umidade e orvalho",
            )
        with col_kpi4:
            r2_multi = c6_data.get("comparison", {}).get("r2_multivariate", 0.0)
            render_kpi_card(
                "R² Multivariado",
                f"{r2_multi:.3f} ({r2_multi * 100:.1f}%)",
                "Demanda explicada pelo clima completo",
            )

        st.markdown("---")

        col_chart, col_corr = st.columns([1.5, 1.1])
        with col_chart:
            fig_comp = build_cmu_q6_comparison_chart(c6_data)
            st.plotly_chart(fig_comp, use_container_width=True)
            st.caption(
                "📌 **Significado das Siglas de Erro:**<br>"
                "• **RMSE (Root Mean Square Error):** Raiz do erro quadrático médio em MW. "
                "Penaliza desvios severos e picos imprevistos.<br>"
                "• **MAE (Mean Absolute Error):** Erro médio absoluto em MW (desvio linear direto "
                "entre a previsão e a carga real).<br>"
                "• **MSE (Mean Squared Error):** Erro quadrático total da função de perda "
                "(redução de 8.73% comprovada).",
                unsafe_allow_html=True,
            )

        with col_corr:
            st.markdown("#### 🌡️ Correlação com o Pico de Demanda")
            corrs = c5_data.get("correlations_with_peak_demand", {})
            corr_df = pd.DataFrame(
                [
                    {
                        "Variável Climática": "Ponto de Orvalho Médio",
                        "Correlação Linear (r)": f"{corrs.get('dewpoint_mean', 0.3892):+.4f}",
                    },
                    {
                        "Variável Climática": "Temperatura Mínima",
                        "Correlação Linear (r)": f"{corrs.get('temp_min', 0.3770):+.4f}",
                    },
                    {
                        "Variável Climática": "Temperatura Máxima",
                        "Correlação Linear (r)": f"{corrs.get('temp_max', 0.3401):+.4f}",
                    },
                    {
                        "Variável Climática": "Umidade Relativa Média",
                        "Correlação Linear (r)": f"{corrs.get('humidity_mean', 0.0746):+.4f}",
                    },
                    {
                        "Variável Climática": "Pressão Atmosférica Média",
                        "Correlação Linear (r)": f"{corrs.get('pressure_mean', -0.0403):+.4f}",
                    },
                    {
                        "Variável Climática": "Velocidade do Vento Média",
                        "Correlação Linear (r)": f"{corrs.get('wind_mean', -0.1440):+.4f}",
                    },
                ]
            )
            st.dataframe(corr_df, use_container_width=True, hide_index=True)
            st.caption(
                "💡 **O que é o Coeficiente Linear (r de Pearson)?**<br>"
                "Varia de -1 a +1 e mede a força da relação linear com o pico de demanda:<br>"
                "• **Positivo (+):** Aumenta o pico (ar abafado e ar-condicionado).<br>"
                "• **Negativo (-):** Alivia o pico (vento dissipa calor por convecção natural).",
                unsafe_allow_html=True,
            )

    # Módulo 3: Smart Building & Solar (Zenodo 2025)
    elif navigation == "Smart Building & Solar (Zenodo 2025)":
        st.title("🏢 Previsão em Smart Buildings & Integração Solar Fotovoltaica")
        st.markdown(
            "Benchmark da **Competição Zenodo 2025** em um edifício inteligente com 1 ano "
            "de telemetria e geração solar no telhado."
        )

        c7_data = cycles_data.get("cycle_07", {})
        solar_info = c7_data.get("solar_energy_impact", {})

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_kpi_card(
                "Consumo Médio",
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
            c7_data,
            show_ridge=show_ridge,
            show_rf=show_rf,
            show_solar=show_solar,
            show_net=show_net,
        )
        st.plotly_chart(fig_zen, use_container_width=True)

        st.markdown("#### 🎯 Avaliação Multi-critério dos Modelos de Previsão")
        models_bench = c7_data.get("models_benchmarking", {})
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
            "**R²** quantifica a precisão global (Random Forest lidera com 90.0%)."
        )

    # Módulo 4: Auditoria dos 7 Ciclos (JSON)
    elif navigation == "Auditoria dos 7 Ciclos (JSON)":
        st.title("📋 Trilha de Auditoria: Os 7 Ciclos de Refinamento em JSON")
        st.markdown(
            "Todos os ciclos de ingestão, higienização, engenharia e predição persistidos "
            "em arquivos JSON estruturados em `data/cycles/`."
        )

        cycle_keys = [
            ("cycle_01", "Ciclo 01: Dados Brutos CMU Q5 (Temperatura & Demanda)"),
            ("cycle_02", "Ciclo 02: Modelos CMU Q5 Ajustados (4 Modelos x 2 Perdas)"),
            ("cycle_03", "Ciclo 03: Limpeza de Sensores CMU Q6 (-9999 & Deduplicação)"),
            ("cycle_04", "Ciclo 04: Interpolação Temporal CMU Q6 (Sincronização)"),
            ("cycle_05", "Ciclo 05: Atributos Multivariados CMU Q6 (Agregação Diária)"),
            ("cycle_06", "Ciclo 06: Benchmarking Univariado vs. Multivariado"),
            ("cycle_07", "Ciclo 07: Benchmark Smart Building Zenodo 2025"),
        ]

        selected_cycle_key = st.selectbox(
            "Selecione o Ciclo para Inspecionar:",
            options=[k for k, _ in cycle_keys],
            format_func=lambda k: dict(cycle_keys).get(k, k),
        )

        cycle_obj = cycles_data.get(selected_cycle_key, {})
        render_cycle_summary(cycle_obj)

        st.json(cycle_obj, expanded=False)


if __name__ == "__main__":
    main()
