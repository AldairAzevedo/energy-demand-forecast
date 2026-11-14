"""Componentes visuais reutilizáveis com foco em clareza cognitiva e UI/UX."""

from typing import Any, Dict, List, Tuple

import streamlit as st


def apply_custom_styles() -> None:
    """Aplica estilos CSS limpos, legíveis e com hierarquia visual clara."""
    st.markdown(
        """
        <style>
        .metric-card {
            background-color: var(--secondary-background-color, rgba(148, 163, 184, 0.10));
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-left: 4px solid #0284C7;
            border-radius: 10px;
            padding: 14px 18px;
            margin-bottom: 12px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
            min-height: 124px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .metric-label {
            font-size: 12px;
            font-weight: 700;
            color: var(--text-color);
            opacity: 0.78;
            text-transform: uppercase;
            letter-spacing: 0.45px;
        }
        .metric-value {
            font-size: 26px;
            font-weight: 800;
            color: var(--text-color);
            margin-top: 4px;
        }
        .metric-delta {
            font-size: 12.5px;
            color: #10B981;
            font-weight: 600;
            margin-top: 5px;
            line-height: 1.35;
        }
        .badge-cycle {
            display: inline-block;
            background-color: rgba(2, 132, 199, 0.15);
            color: #0284C7;
            padding: 4px 12px;
            border-radius: 14px;
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        .legend-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 6px 0 12px 0;
        }
        .legend-pill {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 5px 12px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 700;
            background-color: rgba(148, 163, 184, 0.12);
            border: 1.5px solid;
        }
        .guide-box {
            background-color: rgba(139, 92, 246, 0.12);
            border: 1px solid rgba(139, 92, 246, 0.35);
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 14px;
            color: var(--text-color);
            font-size: 14px;
            line-height: 1.5;
        }
        .status-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
            margin: 4px 0 10px 0;
        }
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 12px;
            border-radius: 999px;
            font-size: 12.5px;
            font-weight: 700;
            background-color: rgba(2, 132, 199, 0.14);
            border: 1px solid rgba(2, 132, 199, 0.40);
            color: var(--text-color);
        }
        .status-pill-muted {
            background-color: rgba(148, 163, 184, 0.12);
            border-color: rgba(148, 163, 184, 0.35);
        }
        .loading-backdrop {
            position: fixed;
            inset: 0;
            z-index: 999999;
            background: rgba(2, 6, 23, 0.72);
            backdrop-filter: blur(3px);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .loading-modal {
            background: #0f172a;
            color: #f8fafc;
            border: 1px solid rgba(56, 189, 248, 0.45);
            border-radius: 14px;
            padding: 24px 32px;
            box-shadow: 0 18px 48px rgba(0, 0, 0, 0.55);
            text-align: center;
            max-width: 440px;
            font-size: 15px;
            font-weight: 600;
        }
        .loading-spinner {
            width: 36px;
            height: 36px;
            border: 4px solid rgba(56, 189, 248, 0.25);
            border-top-color: #38bdf8;
            border-radius: 50%;
            margin: 0 auto 14px auto;
            animation: spin-action 0.85s linear infinite;
        }
        @keyframes spin-action {
            to { transform: rotate(360deg); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    title: str, value: str, subtext: str = "", accent_color: str = "#0284C7"
) -> None:
    """Renderiza um card de KPI com borda lateral colorida e altura uniforme."""
    sub_html = (
        f'<div class="metric-delta">{subtext}</div>'
        if subtext
        else '<div class="metric-delta" style="visibility: hidden;">&nbsp;</div>'
    )
    card_html = f"""
    <div class="metric-card" style="border-left-color: {accent_color};">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
        {sub_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_color_legend(items: List[Tuple[str, str, str]]) -> None:
    """Exibe legenda visual com texto e borda na mesma cor das linhas do gráfico."""
    pills_html = "".join(
        f'<span class="legend-pill" style="color: {color}; border-color: {color};">'
        f"{symbol} {label}</span>"
        for label, color, symbol in items
    )
    st.markdown(f'<div class="legend-strip">{pills_html}</div>', unsafe_allow_html=True)


def render_beginner_guide(text: str) -> None:
    """Exibe caixa explicativa amigável para leitura rápida por qualquer usuário."""
    st.markdown(f'<div class="guide-box">{text}</div>', unsafe_allow_html=True)


def render_cycle_summary(cycle_data: Dict[str, Any]) -> None:
    """Exibe um cabeçalho resumido para a auditoria do pipeline Zenodo 2025."""
    title = cycle_data.get("title", "Previsão de Consumo Elétrico — Zenodo 2025")
    st.markdown(
        '<span class="badge-cycle">Zenodo 2025 • Smart Building</span>',
        unsafe_allow_html=True,
    )
    st.subheader(title)


def render_active_status_strip(run_id: str, scenario_label: str, cutoff_label: str) -> None:
    """Exibe no topo da página qual rodada (run_XXXX) e cenário estão renderizados."""
    st.markdown(
        f'<div class="status-strip">'
        f'<span class="status-pill">🧪 Rodada Ativa: {run_id or "-"}</span>'
        f'<span class="status-pill status-pill-muted">📌 {scenario_label}</span>'
        f'<span class="status-pill status-pill-muted">✂️ {cutoff_label}</span>'
        f"</div>",
        unsafe_allow_html=True,
    )


def render_loading_backdrop(message: str) -> Any:
    """Exibe overlay escuro translúcido centralizado durante execuções de ações."""
    slot = st.empty()
    slot.markdown(
        f'<div class="loading-backdrop">'
        f'<div class="loading-modal">'
        f'<div class="loading-spinner"></div>'
        f"<div>{message}</div>"
        f'<div style="font-size:12.5px;color:#94a3b8;margin-top:8px;">'
        f"Aguarde enquanto os modelos são recalculados e salvos em data/db/..."
        f"</div></div></div>",
        unsafe_allow_html=True,
    )
    return slot


TABLE_COLUMN_METADATA: Dict[str, Tuple[str, str]] = {
    "Posição": (
        "Posição",
        (
            "Classificação dinâmica do modelo neste cenário pelo critério Multi-Critério "
            "(1º Campeão → 3º)."
        ),
    ),
    "Modelo": (
        "Modelo",
        "Algoritmo preditivo avaliado (HistGradientBoosting, Random Forest ou Ridge Linear).",
    ),
    "Nota Multi-Critério": (
        "Nota Multi-Critério",
        (
            "Pontuação oficial de 0 a 100: Acurácia no teste (80%), Equilíbrio Treino–Teste "
            "(15%) e Velocidade (5%)."
        ),
    ),
    "RMSE Teste (W)": (
        "RMSE Teste (W)",
        (
            "Raiz do Erro Quadrático Médio no teste (Watts). Penaliza erros grandes; "
            "menor = melhor."
        ),
    ),
    "RMSE Treino (W)": (
        "RMSE Treino (W)",
        (
            "Raiz do Erro Quadrático Médio no treino (Watts). Muito menor que o RMSE Teste "
            "indica overfitting."
        ),
    ),
    "MAE Teste (W)": (
        "MAE Teste (W)",
        (
            "Erro Médio Absoluto no teste: desvio médio por hora (Watts) frente ao consumo "
            "real; menor = melhor."
        ),
    ),
    "Aderência (R²)": (
        "Aderência (R²)",
        (
            "Coeficiente de Determinação R² no teste: percentual da variação real explicado "
            "pelo modelo; maior = melhor."
        ),
    ),
    "R² Treino": (
        "R² Treino",
        "Coeficiente de Determinação R² nos dados de treino (mede o ajuste ao passado).",
    ),
    "R² Teste": (
        "R² Teste",
        "Coeficiente de Determinação R² nos dados inéditos (mede a generalização real).",
    ),
    "Treino (ms)": (
        "Treino (ms)",
        (
            "Tempo computacional em milissegundos gasto para ajustar o modelo nos dados "
            "históricos."
        ),
    ),
    "Inferência (ms)": (
        "Inferência (ms)",
        (
            "Tempo computacional em milissegundos para gerar todas as previsões 1h no "
            "conjunto de teste."
        ),
    ),
    "Tempo Total (ms)": (
        "Tempo Total (ms)",
        "Soma de treino + inferência em milissegundos; menor = maior eficiência computacional.",
    ),
    "Acerto ≤ 200 W": (
        "Acerto ≤ 200 W",
        (
            "Percentual de horas do conjunto de teste em que o erro absoluto ficou dentro "
            "de ±200 W."
        ),
    ),
    "Diagnóstico": (
        "Diagnóstico",
        (
            "Classificação automática Treino vs. Teste (Bom Ajuste, Leve Sobreajuste, "
            "Overfitting ou Underfitting)."
        ),
    ),
    "Lags (h)": (
        "Lags (h)",
        (
            "Janelas de memória autoregressiva em horas passadas (ex.: 1 = 1h atrás, "
            "24 = ontem, 168 = semana passada)."
        ),
    ),
    "Nº Variáveis": (
        "Nº Variáveis",
        (
            "Total de atributos de entrada (temporais + covariáveis) efetivamente usados "
            "pelo modelo."
        ),
    ),
    "Run ID": (
        "Run ID",
        (
            "Identificador sequencial único da rodada experimental registrada no banco "
            "JSON (data/db/)."
        ),
    ),
    "Cenário": (
        "Cenário",
        (
            "Protocolo de validação usado na rodada (v1.0 Split Interno, v1 → v2 ou "
            "v1+v2 → v4 Oficial)."
        ),
    ),
    "Δ vs Anterior": (
        "Δ vs Anterior",
        (
            "Diferença de RMSE Teste (W) frente à rodada anterior; valores negativos "
            "(verde) indicam melhora."
        ),
    ),
    "Recorde?": (
        "Recorde?",
        (
            "Indica se esta rodada registrou novo recorde Multi-Critério para este modelo "
            "no cenário."
        ),
    ),
    "test_hour_index": (
        "Hora Pós-Corte",
        "Posição sequencial da hora após o Ponto de Corte dentro do conjunto de teste.",
    ),
    "hour_of_day": (
        "Hora do Dia (h)",
        "Horário do relógio (0h a 23h) correspondente à medição horária.",
    ),
    "real_w": (
        "Consumo Real (W)",
        "Potência média horária realmente consumida e medida no edifício nessa hora.",
    ),
    "pred_w": (
        "Previsão (W)",
        "Potência média horária prevista 1h à frente pelo modelo inspecionado.",
    ),
    "abs_error_w": (
        "Erro Absoluto (W)",
        "Módulo da diferença |Previsão − Real| em Watts nessa hora específica.",
    ),
    "Variável / Hiperparâmetro": (
        "Variável / Hiperparâmetro",
        (
            "Nome do atributo de entrada (lag, média móvel, relógio, covariável) ou "
            "parâmetro de aprendizado."
        ),
    ),
    "Classificação": (
        "Classificação",
        (
            "Separação científica entre Hiperparâmetro de ML / Engenharia Temporal e "
            "Covariável física real."
        ),
    ),
    "Controle": (
        "Controle",
        (
            "Indica onde na interface (Laboratório ou Gráfico Principal) esse parâmetro "
            "pode ser ajustado."
        ),
    ),
}


def build_table_column_config(columns: Any) -> Dict[str, Any]:
    """Gera st.column_config com rótulo e tooltip explicativo para cada coluna."""
    config: Dict[str, Any] = {}
    for col in columns:
        col_str = str(col)
        if col_str in TABLE_COLUMN_METADATA:
            label, help_text = TABLE_COLUMN_METADATA[col_str]
            config[col_str] = st.column_config.Column(label=label, help=help_text)
    return config


def render_explained_dataframe(df: Any) -> None:
    """Renderiza DataFrame Streamlit com tooltips explicativos em todas as colunas."""
    columns = list(getattr(df, "columns", []))
    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        column_config=build_table_column_config(columns),
    )
