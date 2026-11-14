"""Módulo de gráficos interativos Plotly unificados com Ponto de Corte e Covariáveis."""

from typing import Any, Dict, List, Sequence, Tuple

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.core.diagnostics import rank_benchmarking_models

COLOR_PALETTE = {
    "Contexto": "#A78BFA",
    "Observado": "#8B5CF6",  # Violeta Vivo (Contraste alto no Light e Dark)
    "Hist_Gradient_Boosting": "#0284C7",  # Azul Cobalto
    "Random_Forest": "#059669",  # Verde Esmeralda
    "Ridge_Linear": "#EA580C",  # Laranja Âmbar
    "Temperatura": "#F59E0B",  # Âmbar (Covariável Climática)
    "Geracao_FV": "#10B981",  # Esmeralda Claro (Covariável Solar FV)
}

MODEL_UI_META: Dict[str, Dict[str, Any]] = {
    "Hist_Gradient_Boosting": {
        "short": "HistGradientBoosting",
        "color_label": "Azul",
        "field": "pred_hgb_w",
        "dash": "solid",
        "pill_symbol": "━━",
    },
    "Random_Forest": {
        "short": "Random Forest",
        "color_label": "Verde",
        "field": "pred_rf_w",
        "dash": "dash",
        "pill_symbol": "╌╌",
    },
    "Ridge_Linear": {
        "short": "Ridge Linear",
        "color_label": "Laranja",
        "field": "pred_ridge_w",
        "dash": "dot",
        "pill_symbol": "┈┈",
    },
}


def _relative_label(hour: int) -> str:
    return f"Corte +{hour}h" if hour >= 1 else f"Corte {hour}h"


def _build_axis_ticks(combined: Sequence[Dict[str, Any]]) -> Tuple[List[int], List[str]]:
    """Seleciona até 10 marcas espaçadas uniformemente no eixo X (Dia · Hora)."""
    if not combined:
        return [], []
    n_pts = len(combined)
    n_ticks = min(10, n_pts)
    if n_ticks == 1:
        indices = [0]
    else:
        indices = sorted({round(i * (n_pts - 1) / (n_ticks - 1)) for i in range(n_ticks)})
    tickvals = [int(combined[i]["hour"]) for i in indices]
    ticktext = [str(combined[i].get("timestamp", f"{combined[i]['hour']}h")) for i in indices]
    return tickvals, ticktext


def _add_cutoff_marker(fig: go.Figure, x_end: int, has_context: bool) -> None:
    if not has_context:
        return
    fig.add_vrect(
        x0=0.5,
        x1=max(1, x_end),
        fillcolor="rgba(2, 132, 199, 0.05)",
        layer="below",
        line_width=0,
        row="all",
        col=1,
    )
    fig.add_vline(
        x=0.5,
        line_width=1.8,
        line_dash="dash",
        line_color="#EF4444",
        row="all",
        col=1,
    )
    fig.add_annotation(
        x=0.5,
        y=1.0,
        yref="y domain",
        xref="x",
        text="✂️ Ponto de Corte (Previsão 1h)",
        showarrow=False,
        xanchor="left",
        xshift=6,
        yanchor="top",
        font=dict(color="#EF4444", size=12),
        bgcolor="rgba(15, 23, 42, 0.55)",
    )


def _resolve_covariate_state(forecast_data: Dict[str, Any]) -> Tuple[bool, bool]:
    cov_meta = forecast_data.get("active_covariates")
    if isinstance(cov_meta, dict):
        return (
            bool(cov_meta.get("use_temperature", True)),
            bool(cov_meta.get("use_generation", True)),
        )
    bench = forecast_data.get("models_benchmarking", {})
    use_temp = any(
        bool(info.get("effective_features", {}).get("use_temperature", True))
        for info in bench.values()
        if isinstance(info, dict)
    )
    use_gen = any(
        bool(info.get("effective_features", {}).get("use_generation", True))
        for info in bench.values()
        if isinstance(info, dict)
    )
    return (use_temp if bench else True), (use_gen if bench else True)


def _add_power_traces(
    fig: go.Figure,
    ctx: Sequence[Dict[str, Any]],
    post: Sequence[Dict[str, Any]],
    bench: Dict[str, Any],
    visibility: Dict[str, bool],
) -> None:
    if ctx:
        ctx_bridge = list(ctx) + [post[0]]
        fig.add_trace(
            go.Scatter(
                x=[item["hour"] for item in ctx_bridge],
                y=[item["real_power_w"] for item in ctx_bridge],
                mode="lines",
                name="Contexto Pré-Corte (Real)",
                line=dict(color=COLOR_PALETTE["Contexto"], width=2.2),
                customdata=[
                    [item.get("timestamp", ""), _relative_label(int(item["hour"]))]
                    for item in ctx_bridge
                ],
                hovertemplate=(
                    "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
                    "Contexto Real: <b>%{y:.0f} W</b><extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )

    post_hours = [item["hour"] for item in post]
    post_custom = [[item.get("timestamp", ""), _relative_label(int(item["hour"]))] for item in post]
    fig.add_trace(
        go.Scatter(
            x=post_hours,
            y=[item["real_power_w"] for item in post],
            mode="lines",
            name=(
                f"<span style='color:{COLOR_PALETTE['Observado']}'>"
                "<b>Consumo Real Medido (W)</b></span>"
            ),
            line=dict(color=COLOR_PALETTE["Observado"], width=2.8),
            fill="tozeroy",
            fillcolor="rgba(139, 92, 246, 0.08)",
            customdata=post_custom,
            hovertemplate=(
                "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
                "Consumo Real: <b>%{y:.0f} W</b><extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )

    ranked = rank_benchmarking_models(bench) if bench else [(k, {}) for k in MODEL_UI_META]
    for idx, (m_key, _) in enumerate(ranked):
        if not visibility.get(m_key, True) or m_key not in MODEL_UI_META:
            continue
        meta = MODEL_UI_META[m_key]
        color = COLOR_PALETTE[m_key]
        rank_prefix = "🏆 1º " if idx == 0 else f"{idx + 1}º "
        label = f"{rank_prefix}{meta['short']}"
        width = 2.6 if idx == 0 else 2.1
        fig.add_trace(
            go.Scatter(
                x=post_hours,
                y=[item.get(meta["field"], 0.0) for item in post],
                mode="lines",
                name=f"<span style='color:{color}'><b>{label}</b></span>",
                line=dict(color=color, dash=meta["dash"], width=width),
                customdata=post_custom,
                hovertemplate=f"{label}: <b>%{{y:.0f}} W</b><extra></extra>",
            ),
            row=1,
            col=1,
        )


def _add_covariate_strip(
    fig: go.Figure,
    row_idx: int,
    ctx: Sequence[Dict[str, Any]],
    post: Sequence[Dict[str, Any]],
    field: str,
    label: str,
    unit: str,
    y_title: str,
    active_color: str,
    fill_rgba: str,
    is_active: bool,
) -> None:
    if ctx:
        ctx_bridge = list(ctx) + [post[0]]
        fig.add_trace(
            go.Scatter(
                x=[item["hour"] for item in ctx_bridge],
                y=[item.get(field) for item in ctx_bridge],
                mode="lines",
                name=f"{label} (Contexto)",
                showlegend=False,
                line=dict(color=active_color, width=1.8),
                customdata=[
                    [item.get("timestamp", ""), _relative_label(int(item["hour"]))]
                    for item in ctx_bridge
                ],
                hovertemplate=(
                    f"<b>%{{customdata[0]}}</b> (%{{customdata[1]}})<br>"
                    f"{label}: <b>%{{y:.1f}} {unit}</b><extra></extra>"
                ),
            ),
            row=row_idx,
            col=1,
        )

    post_line = (
        dict(color=active_color, width=2.0)
        if is_active
        else dict(color="rgba(148, 163, 184, 0.34)", width=1.4, dash="dot")
    )
    status_txt = "Ativa no modelo" if is_active else "Desativada no modelo"
    fig.add_trace(
        go.Scatter(
            x=[item["hour"] for item in post],
            y=[item.get(field) for item in post],
            mode="lines",
            name=f"{label} ({status_txt})",
            showlegend=False,
            line=post_line,
            fill="tozeroy" if is_active else None,
            fillcolor=fill_rgba if is_active else None,
            customdata=[
                [item.get("timestamp", ""), _relative_label(int(item["hour"]))] for item in post
            ],
            hovertemplate=(
                f"<b>%{{customdata[0]}}</b> (%{{customdata[1]}})<br>"
                f"{label} ({status_txt}): <b>%{{y:.1f}} {unit}</b><extra></extra>"
            ),
        ),
        row=row_idx,
        col=1,
    )
    fig.update_yaxes(
        title_text=y_title,
        gridcolor="rgba(148, 163, 184, 0.16)",
        row=row_idx,
        col=1,
    )


def build_zenodo_chart(
    forecast_data: Dict[str, Any],
    show_ridge: bool = True,
    show_rf: bool = True,
    show_hgb: bool = True,
) -> go.Figure:
    """Constrói gráfico unificado: Potência (Real vs. 1h) + Covariáveis alinhadas ao corte."""
    ctx = forecast_data.get("context_sample", [])
    post = forecast_data.get("recent_predictions_sample", [])
    if not post:
        return go.Figure()

    combined = list(ctx) + list(post)
    has_temp = any(item.get("temp_c") is not None for item in combined)
    has_gen = bool(forecast_data.get("has_generation", True)) and any(
        item.get("gen_w") is not None for item in combined
    )
    use_temp, use_gen = _resolve_covariate_state(forecast_data)

    row_heights = [0.64]
    if has_temp:
        row_heights.append(0.18 if has_gen else 0.36)
    if has_gen:
        row_heights.append(0.18)

    n_rows = len(row_heights)
    fig = make_subplots(
        rows=n_rows,
        cols=1,
        shared_xaxes=True,
        row_heights=row_heights,
        vertical_spacing=0.04,
    )

    _add_power_traces(
        fig,
        ctx,
        post,
        forecast_data.get("models_benchmarking", {}),
        {
            "Hist_Gradient_Boosting": show_hgb,
            "Random_Forest": show_rf,
            "Ridge_Linear": show_ridge,
        },
    )

    next_row = 2
    if has_temp:
        _add_covariate_strip(
            fig,
            next_row,
            ctx,
            post,
            "temp_c",
            "🌡️ Temperatura",
            "°C",
            "Temp (°C)",
            COLOR_PALETTE["Temperatura"],
            "rgba(245, 158, 11, 0.12)",
            use_temp,
        )
        next_row += 1
    if has_gen:
        _add_covariate_strip(
            fig,
            next_row,
            ctx,
            post,
            "gen_w",
            "☀️ Geração FV",
            "W",
            "Solar FV (W)",
            COLOR_PALETTE["Geracao_FV"],
            "rgba(16, 185, 129, 0.12)",
            use_gen,
        )

    _add_cutoff_marker(fig, x_end=int(post[-1]["hour"]), has_context=bool(ctx))
    tickvals, ticktext = _build_axis_ticks(combined)
    scenario_title = forecast_data.get("scenario_label", "Semana Pós-Corte")

    fig.update_yaxes(
        title_text="Potência Elétrica (W)",
        gridcolor="rgba(148, 163, 184, 0.22)",
        row=1,
        col=1,
    )
    fig.update_xaxes(gridcolor="rgba(148, 163, 184, 0.16)")
    fig.update_xaxes(
        title_text="Linha do Tempo Real (Pré-Corte → Pós-Corte 1h)",
        tickmode="array" if tickvals else "auto",
        tickvals=tickvals or None,
        ticktext=ticktext or None,
        row=n_rows,
        col=1,
    )
    fig.update_layout(
        title=(
            f"Consumo Real vs. Previsões 1h com Ponto de Corte — "
            f"{scenario_title} ({len(post)}h pós-corte)"
        ),
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=13),
        ),
        margin=dict(l=60, r=25, t=88, b=50),
        height=690 if n_rows == 3 else (600 if n_rows == 2 else 500),
    )
    return fig


def build_train_vs_test_chart(forecast_data: Dict[str, Any]) -> go.Figure:
    """Compara erro RMSE no Treino vs. no Teste por modelo (detector visual de overfitting)."""
    fig = go.Figure()
    bench = forecast_data.get("models_benchmarking", {})
    if not bench:
        return fig

    model_names: list[str] = []
    train_rmses: list[float] = []
    test_rmses: list[float] = []
    train_r2s: list[float] = []
    test_r2s: list[float] = []

    for idx, (m_key, info) in enumerate(rank_benchmarking_models(bench)):
        prefix = "🏆 1º " if idx == 0 else f"{idx + 1}º "
        short_name = MODEL_UI_META.get(m_key, {}).get("short", info.get("name", m_key))
        model_names.append(f"{prefix}{short_name}")
        train_m = info.get("train_metrics", {})
        test_m = info.get("metrics", {})
        train_rmses.append(float(train_m.get("rmse", 0.0)))
        test_rmses.append(float(test_m.get("rmse", 0.0)))
        train_r2s.append(float(train_m.get("r2", 0.0)) * 100.0)
        test_r2s.append(float(test_m.get("r2", 0.0)) * 100.0)

    fig.add_trace(
        go.Bar(
            name="Treino (Passado Aprendido)",
            x=model_names,
            y=train_rmses,
            marker_color="#059669",
            customdata=train_r2s,
            hovertemplate="Treino RMSE: <b>%{y:.1f} W</b> (R²: %{customdata:.1f}%)<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Teste (Dados Novos)",
            x=model_names,
            y=test_rmses,
            marker_color="#0284C7",
            customdata=test_r2s,
            hovertemplate="Teste RMSE: <b>%{y:.1f} W</b> (R²: %{customdata:.1f}%)<extra></extra>",
        )
    )

    fig.update_layout(
        title="Aprendizado: Erro no Treino vs. Teste — RMSE (Menor = Melhor)",
        barmode="group",
        yaxis_title="Erro Típico — RMSE (W)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        xaxis=dict(gridcolor="rgba(148, 163, 184, 0.22)"),
        yaxis=dict(gridcolor="rgba(148, 163, 184, 0.22)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=50, r=20, t=75, b=45),
        height=380,
    )
    return fig


def build_period_error_chart(forecast_data: Dict[str, Any]) -> go.Figure:
    """Mostra em qual turno do dia cada modelo erra mais ou acerta mais (MAE em Watts)."""
    fig = go.Figure()
    bench = forecast_data.get("models_benchmarking", {})
    if not bench:
        return fig

    for idx, (key, info) in enumerate(rank_benchmarking_models(bench)):
        periods = info.get("error_diagnostics", {}).get("period_breakdown", [])
        if not periods:
            continue
        prefix = "🏆 1º " if idx == 0 else f"{idx + 1}º "
        short_name = MODEL_UI_META.get(key, {}).get("short", info.get("name", key))
        fig.add_trace(
            go.Bar(
                name=f"{prefix}{short_name}",
                x=[p["period"] for p in periods],
                y=[p["mae_w"] for p in periods],
                marker_color=COLOR_PALETTE.get(key, "#8B5CF6"),
                customdata=[p["hit_rate_200w_pct"] for p in periods],
                hovertemplate=(
                    f"{short_name}<br>"
                    "MAE: <b>%{y:.1f} W</b><br>"
                    "Acerto ≤ 200 W: <b>%{customdata:.1f}%</b><extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title="Erro por Período do Dia — MAE (Menor = Melhor)",
        barmode="group",
        yaxis_title="Erro Médio — MAE (W)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        xaxis=dict(gridcolor="rgba(148, 163, 184, 0.22)"),
        yaxis=dict(gridcolor="rgba(148, 163, 184, 0.22)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=50, r=20, t=75, b=45),
        height=380,
    )
    return fig
