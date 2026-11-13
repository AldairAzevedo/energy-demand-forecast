"""Módulo de gráficos interativos Plotly com alto contraste e codificação por cores."""

from typing import Any, Dict

import plotly.graph_objects as go

COLOR_PALETTE = {
    "Observado": "#8B5CF6",  # Violeta Vivo (Contraste alto no Light e Dark)
    "Hist_Gradient_Boosting": "#0284C7",  # Azul Cobalto (Campeão)
    "Random_Forest": "#059669",  # Verde Esmeralda (Árvores)
    "Ridge_Linear": "#EA580C",  # Laranja Âmbar (Baseline Linear)
}


def build_zenodo_chart(
    forecast_data: Dict[str, Any],
    show_ridge: bool = True,
    show_rf: bool = True,
    show_hgb: bool = True,
) -> go.Figure:
    """Constrói gráfico de série temporal com cores de alto contraste e legenda colorida."""
    fig = go.Figure()
    samples = forecast_data.get("recent_predictions_sample", [])
    if not samples:
        return fig

    hours = [s["hour"] for s in samples]
    real_power = [s["real_power_w"] for s in samples]

    fig.add_trace(
        go.Scatter(
            x=hours,
            y=real_power,
            mode="lines",
            name=(
                f"<span style='color:{COLOR_PALETTE['Observado']}'>"
                "<b>Consumo Real Medido (W)</b></span>"
            ),
            line=dict(color=COLOR_PALETTE["Observado"], width=2.8),
            fill="tozeroy",
            fillcolor="rgba(139, 92, 246, 0.08)",
            hovertemplate="Consumo Real: <b>%{y:.0f} W</b><extra></extra>",
        )
    )

    if show_hgb:
        c_hgb = COLOR_PALETTE["Hist_Gradient_Boosting"]
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=[s.get("pred_hgb_w", 0.0) for s in samples],
                mode="lines",
                name=f"<span style='color:{c_hgb}'><b>HistGradientBoosting</b></span>",
                line=dict(color=c_hgb, width=2.4),
                hovertemplate="HistGradientBoosting: <b>%{y:.0f} W</b><extra></extra>",
            )
        )

    if show_rf:
        c_rf = COLOR_PALETTE["Random_Forest"]
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=[s.get("pred_rf_w", 0.0) for s in samples],
                mode="lines",
                name=f"<span style='color:{c_rf}'><b>Random Forest</b></span>",
                line=dict(color=c_rf, dash="dash", width=2.2),
                hovertemplate="Random Forest: <b>%{y:.0f} W</b><extra></extra>",
            )
        )

    if show_ridge:
        c_ridge = COLOR_PALETTE["Ridge_Linear"]
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=[s.get("pred_ridge_w", 0.0) for s in samples],
                mode="lines",
                name=f"<span style='color:{c_ridge}'><b>Ridge Linear (Baseline)</b></span>",
                line=dict(color=c_ridge, dash="dot", width=2.2),
                hovertemplate="Ridge Linear: <b>%{y:.0f} W</b><extra></extra>",
            )
        )

    fig.update_layout(
        title="Consumo Real vs. Previsões dos Modelos (Semana de Teste — 168h)",
        xaxis_title="Hora da Semana de Teste (h)",
        yaxis_title="Potência Elétrica Consumida (W)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        xaxis=dict(gridcolor="rgba(148, 163, 184, 0.22)"),
        yaxis=dict(gridcolor="rgba(148, 163, 184, 0.22)"),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="center",
            x=0.5,
            font=dict(size=13),
        ),
        margin=dict(l=55, r=25, t=85, b=50),
        height=500,
    )
    return fig
