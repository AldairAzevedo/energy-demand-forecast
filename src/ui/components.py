"""Componentes visuais reutilizáveis para o dashboard monolítico."""

from typing import Any, Dict

import streamlit as st


def apply_custom_styles() -> None:
    """Aplica estilos CSS minimalistas e modernos para uma experiência visual premium."""
    st.markdown(
        """
        <style>
        .metric-card {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .metric-label {
            font-size: 13px;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-value {
            font-size: 26px;
            font-weight: 700;
            color: #0F172A;
            margin-top: 4px;
        }
        .metric-delta {
            font-size: 13px;
            color: #10B981;
            font-weight: 500;
            margin-top: 2px;
        }
        .badge-cycle {
            display: inline-block;
            background-color: #EFF6FF;
            color: #1D4ED8;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(title: str, value: str, subtext: str = "") -> None:
    """Renderiza um card de KPI compacto e elegante."""
    sub_html = f'<div class="metric-delta">{subtext}</div>' if subtext else ""
    card_html = f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
        {sub_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_cycle_summary(cycle_data: Dict[str, Any]) -> None:
    """Exibe um cabeçalho resumido para a auditoria de cada ciclo."""
    cycle_id = cycle_data.get("cycle_id", "?")
    title = cycle_data.get("title", "Ciclo de Processamento")
    st.markdown(f'<span class="badge-cycle">Ciclo {cycle_id} de 7</span>', unsafe_allow_html=True)
    st.subheader(title)
