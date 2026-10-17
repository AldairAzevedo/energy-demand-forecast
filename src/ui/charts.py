from typing import Any, Dict, List

import plotly.graph_objects as go

COLOR_PALETTE = {
    "Linear": "#2563EB",  # Azul Real
    "Polinomial_d5": "#DC2626",  # Vermelho Carmim
    "RBF": "#16A34A",  # Verde Esmeralda
    "Kernel_Gaussiano": "#9333EA",  # Roxo Nobre
    "Observado": "#64748B",  # Ardósia
    "Solar": "#EAB308",  # Âmbar Solar
    "Demanda_Liquida": "#059669",  # Verde Floresta
    "Random_Forest": "#EA580C",  # Laranja Queimado
}


def build_cmu_q5_chart(
    raw_data: Dict[str, Any],
    fitted_data: Dict[str, Any],
    selected_models: List[str],
    loss_type: str = "L2",
    show_scatter: bool = True,
) -> go.Figure:
    """Constrói o gráfico de dispersão e curvas ajustadas para o CMU Q5."""
    fig = go.Figure()

    # Pontos de dispersão observados
    if show_scatter and "records" in raw_data:
        temps = [r["temperature"] for r in raw_data["records"]]
        demands = [r["demand"] for r in raw_data["records"]]
        fig.add_trace(
            go.Scatter(
                x=temps,
                y=demands,
                mode="markers",
                name="Demanda Real Observada",
                marker=dict(size=5, color=COLOR_PALETTE["Observado"], opacity=0.5),
                hovertemplate="Temperatura: %{x:.1f} °F<br>Demanda: %{y:.3f} GW<extra></extra>",
            )
        )

    # Curvas dos modelos selecionados
    grid_temps = fitted_data.get("grid_temperatures", [])
    models_dict = fitted_data.get("models", {}).get(loss_type, {})

    for model_key in selected_models:
        if model_key in models_dict:
            m_info = models_dict[model_key]
            color = COLOR_PALETTE.get(model_key, "#000000")
            r2_val = m_info["metrics"]["r2"]
            rmse_val = m_info["metrics"]["rmse"]
            name_label = f"{m_info['model_name']} (R²: {r2_val:.3f} | RMSE: {rmse_val:.3f} GW)"

            fig.add_trace(
                go.Scatter(
                    x=grid_temps,
                    y=m_info["grid_predictions"],
                    mode="lines",
                    name=name_label,
                    line=dict(color=color, width=2.5),
                    hovertemplate=(
                        f"<b>{m_info['model_name']}</b><br>"
                        "Temp: %{x:.1f} °F<br>Pred: %{y:.3f} GW<extra></extra>"
                    ),
                )
            )

    loss_label = (
        "Perda Quadrática (L2 - OLS)" if loss_type == "L2" else "Perda Absoluta Robusta (L1 - LAD)"
    )
    fig.update_layout(
        title=dict(
            text=f"Ajuste de Modelos de Demanda de Pico vs. Temperatura ({loss_label})",
            font=dict(size=16, family="Arial, sans-serif"),
        ),
        xaxis_title="Temperatura Máxima Diária (°F)",
        yaxis_title="Pico de Demanda Diária (GW)",
        template="plotly_white",
        hovermode="closest",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
        ),
        margin=dict(l=50, r=30, t=80, b=50),
        height=520,
    )
    return fig


def build_residuals_chart(
    raw_data: Dict[str, Any],
    fitted_data: Dict[str, Any],
    model_key: str,
    loss_type: str = "L2",
) -> go.Figure:
    """Constrói o gráfico de resíduos (erro = real - predito)."""
    fig = go.Figure()
    models_dict = fitted_data.get("models", {}).get(loss_type, {})

    if model_key in models_dict and "records" in raw_data:
        m_info = models_dict[model_key]
        temps = [r["temperature"] for r in raw_data["records"]]
        residuals = m_info.get("residuals", [])

        fig.add_trace(
            go.Scatter(
                x=temps,
                y=residuals,
                mode="markers",
                name="Resíduos (y - ŷ)",
                marker=dict(
                    size=6,
                    color=residuals,
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title="Erro (GW)"),
                    opacity=0.7,
                ),
                hovertemplate="Temperatura: %{x:.1f} °F<br>Resíduo: %{y:.3f} GW<extra></extra>",
            )
        )

        fig.add_hline(y=0.0, line_dash="dash", line_color="red", line_width=1.5)

    fig.update_layout(
        title=f"Distribuição de Resíduos: {model_key} ({loss_type})",
        xaxis_title="Temperatura Máxima Diária (°F)",
        yaxis_title="Resíduo de Demanda (GW)",
        template="plotly_white",
        margin=dict(l=50, r=30, t=60, b=50),
        height=380,
    )
    return fig


def build_cmu_q6_comparison_chart(cycle_06_data: Dict[str, Any]) -> go.Figure:
    """Constrói gráfico comparativo de barras provando o benefício do multivariado."""
    fig = go.Figure()
    m_uni = cycle_06_data["univariate_model"]["metrics"]
    m_multi = cycle_06_data["multivariate_model"]["metrics"]

    categories = ["RMSE (MW)", "MAE (MW)"]
    uni_values = [m_uni["rmse"], m_uni["mae"]]
    multi_values = [m_multi["rmse"], m_multi["mae"]]

    fig.add_trace(
        go.Bar(
            name="Univariado (Apenas T_max)",
            x=categories,
            y=uni_values,
            marker_color="#3B82F6",
            text=[f"{v:.1f} MW" for v in uni_values],
            textposition="auto",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Multivariado (+ Clima Completo)",
            x=categories,
            y=multi_values,
            marker_color="#10B981",
            text=[f"{v:.1f} MW" for v in multi_values],
            textposition="auto",
        )
    )

    reduction = cycle_06_data["comparison"]["mse_reduction_percentage"]
    fig.update_layout(
        title=f"CMU Item 6: Prova Empírica da Redução de Erro (Redução de MSE: {reduction}%)",
        barmode="group",
        template="plotly_white",
        yaxis_title="Magnitude do Erro (MW)",
        margin=dict(l=50, r=30, t=60, b=50),
        height=400,
    )
    return fig


def build_zenodo_chart(
    cycle_07_data: Dict[str, Any],
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
    pred_rf = [s["pred_rf_w"] for s in samples]
    solar_pv = [s["solar_pv_w"] for s in samples]
    net_demand = [s["net_demand_w"] for s in samples]

    fig.add_trace(
        go.Scatter(
            x=hours,
            y=real_power,
            mode="lines",
            name="Consumo Real Medido (W)",
            line=dict(color="#1E293B", width=2.0),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=pred_rf,
            mode="lines",
            name="Previsão Random Forest (W)",
            line=dict(color=COLOR_PALETTE["Linear"], dash="dash", width=2.0),
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
