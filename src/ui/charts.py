"""Módulo de gráficos interativos Plotly para o desafio Zenodo Smart Building."""

from typing import Any, Dict

import plotly.graph_objects as go

COLOR_PALETTE = {
    "Observado": "#1E293B",  # Ardósia Escura
    "Ridge_Linear": "#6366F1",  # Índigo
    "Random_Forest": "#059669",  # Verde Floresta
    "Solar": "#EAB308",  # Âmbar Solar
    "Demanda_Liquida": "#059669",  # Verde Floresta
}


def build_zenodo_chart(
    cycle_07_data: Dict[str, Any],
    show_ridge: bool = True,
    show_rf: bool = True,
    show_solar: bool = True,
    show_net: bool = True,
) -> go.Figure:
    """Constrói o gráfico de série temporal de carga do Smart Building e impacto solar."""
    fig = go.Figure()
    samples = cycle_07_data.get("recent_predictions_sample", [])
    if not samples:
        return fig

    hours = [s["hour"] for s in samples]
    real_power = [s["real_power_w"] for s in samples]
    pred_ridge = [s.get("pred_ridge_w", 0.0) for s in samples]
    pred_rf = [s.get("pred_rf_w", 0.0) for s in samples]
    solar_pv = [s["solar_pv_w"] for s in samples]
    net_demand = [s["net_demand_w"] for s in samples]

    fig.add_trace(
        go.Scatter(
            x=hours,
            y=real_power,
            mode="lines",
            name="Consumo Real Medido (W)",
            line=dict(color=COLOR_PALETTE["Observado"], width=2.0),
        )
    )

    if show_ridge:
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=pred_ridge,
                mode="lines",
                name="Previsão Ridge Linear (W)",
                line=dict(color=COLOR_PALETTE["Ridge_Linear"], dash="dot", width=1.8),
            )
        )

    if show_rf:
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=pred_rf,
                mode="lines",
                name="Previsão Random Forest (W)",
                line=dict(color=COLOR_PALETTE["Random_Forest"], dash="dash", width=2.0),
            )
        )

    if show_solar:
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=solar_pv,
                mode="lines",
                name="Geração Solar FV (W)",
                line=dict(color=COLOR_PALETTE["Solar"], width=1.8),
                fill="tozeroy",
                fillcolor="rgba(234, 179, 8, 0.15)",
            )
        )

    if show_net:
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=net_demand,
                mode="lines",
                name="Demanda Líquida da Rede (W)",
                line=dict(color=COLOR_PALETTE["Demanda_Liquida"], width=2.0),
            )
        )

    fig.update_layout(
        title="Curva de Carga Smart Building: Previsão vs. Impacto Solar Fotovoltaico",
        xaxis_title="Hora da Amostra (Semana de Teste)",
        yaxis_title="Potência Elétrica (W)",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
        margin=dict(l=50, r=30, t=80, b=50),
        height=500,
    )
    return fig
