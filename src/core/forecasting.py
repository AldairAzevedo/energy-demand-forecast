"""Domínio puro de cenários cross-dataset, compatibilidade causal e Ponto de Corte."""

from copy import deepcopy
from typing import Any, Dict, List, Optional, Sequence, Tuple

EVALUATION_SCENARIOS: Tuple[str, ...] = (
    "v1_internal_split",
    "v1_to_v2",
    "v1_v2_to_v4",
)

DEFAULT_SCENARIO = "v1_internal_split"

SCENARIO_LABELS: Dict[str, str] = {
    "v1_internal_split": "v1.0 Split Interno (80/20)",
    "v1_to_v2": "Cross-Dataset: Treino v1.0 → Teste v2.0",
    "v1_v2_to_v4": "Cross-Dataset Oficial: Treino v1+v2 → Teste v4",
}

SCENARIO_SHORT_LABELS: Dict[str, str] = {
    "v1_internal_split": "v1.0 (80/20)",
    "v1_to_v2": "v1 → v2 (40 Dias)",
    "v1_v2_to_v4": "v1+v2 → v4 (Oficial)",
}

SCENARIO_DESCRIPTIONS: Dict[str, str] = {
    "v1_internal_split": (
        "Treina nos primeiros 80% de data_v1.0.xlsx (7.008 h) e testa nos 20% "
        "finais inéditos (1.752 h), exibindo 72 h de contexto + 168 h após o corte."
    ),
    "v1_to_v2": (
        "Treina em 100% de data_v1.0.xlsx (8.760 h), aquece lags no início de v2.0 "
        "sem vazamento e testa no restante inédito de data_v2.0.xlsx."
    ),
    "v1_v2_to_v4": (
        "Treina em 100% de v1.0 + v2.0 (9.720 h) apenas com atributos compatíveis com v4 "
        "(hora, temperatura e lags <= 24 h); usa Dia 1 (24 h) como contexto e testa Dias 2–3."
    ),
}


def sanitize_scenario(raw_scenario: Any) -> str:
    """Garante identificador de cenário válido, revertendo para o padrão se desconhecido."""
    if isinstance(raw_scenario, str) and raw_scenario in EVALUATION_SCENARIOS:
        return raw_scenario
    return DEFAULT_SCENARIO


def scenario_supports_generation(scenario: str) -> bool:
    """Indica se o cenário possui medições de geração solar, tensão e corrente."""
    return sanitize_scenario(scenario) != "v1_v2_to_v4"


def resolve_effective_feature_config(
    scenario: str,
    feat_cfg: Dict[str, Any],
) -> Dict[str, Any]:
    """Adapta os atributos de entrada às restrições físicas reais do cenário."""
    sc = sanitize_scenario(scenario)
    resolved = deepcopy(feat_cfg)
    if sc != "v1_v2_to_v4":
        return resolved

    resolved["power_lags"] = [lag for lag in resolved.get("power_lags", []) if lag <= 24] or [
        1,
        2,
        3,
        24,
    ]
    resolved["rolling_mean_windows"] = [
        win for win in resolved.get("rolling_mean_windows", []) if win <= 24
    ]
    resolved["rolling_std_windows"] = [
        win for win in resolved.get("rolling_std_windows", []) if win <= 24
    ]
    resolved["use_generation"] = False
    resolved["use_electrical_lags"] = False
    return resolved


def resolve_warmup_length(total_target_len: int, context_hours: int) -> int:
    """Calcula horas iniciais reservadas para aquecimento causal de lags sem bfill."""
    if total_target_len <= 24:
        return max(1, total_target_len // 3)
    desired = max(168, context_hours)
    max_allowed = max(1, total_target_len - 48)
    return min(desired, max_allowed)


def _extract_optional_series_val(values: Optional[Sequence[float]], idx: int) -> Optional[float]:
    if values is None or idx < 0 or idx >= len(values):
        return None
    val = values[idx]
    return round(float(val), 2) if val is not None else None


def build_context_records(
    y_context: Sequence[float],
    timestamps: Sequence[str],
    temp_values: Optional[Sequence[float]] = None,
    gen_values: Optional[Sequence[float]] = None,
) -> List[Dict[str, Any]]:
    """Monta lista ordenada do contexto real pré-corte (hour <= 0)."""
    count = len(y_context)
    records: List[Dict[str, Any]] = []
    for idx in range(count):
        rel_hour = idx - count + 1
        records.append(
            {
                "hour": rel_hour,
                "timestamp": timestamps[idx] if idx < len(timestamps) else f"t={rel_hour}h",
                "real_power_w": round(float(y_context[idx]), 1),
                "temp_c": _extract_optional_series_val(temp_values, idx),
                "gen_w": _extract_optional_series_val(gen_values, idx),
            }
        )
    return records


def build_post_cutoff_records(
    y_test: Sequence[float],
    preds_by_model: Dict[str, Sequence[float]],
    timestamps: Sequence[str],
    horizon_len: int,
    temp_values: Optional[Sequence[float]] = None,
    gen_values: Optional[Sequence[float]] = None,
) -> List[Dict[str, Any]]:
    """Monta lista ordenada imediatamente pós-corte ([:horizon_len], hour >= 1)."""
    count = min(horizon_len, len(y_test))
    records: List[Dict[str, Any]] = []
    for idx in range(count):
        records.append(
            {
                "hour": idx + 1,
                "timestamp": timestamps[idx] if idx < len(timestamps) else f"t=+{idx + 1}h",
                "real_power_w": round(float(y_test[idx]), 1),
                "pred_ridge_w": round(float(preds_by_model["Ridge_Linear"][idx]), 1),
                "pred_rf_w": round(float(preds_by_model["Random_Forest"][idx]), 1),
                "pred_hgb_w": round(float(preds_by_model["Hist_Gradient_Boosting"][idx]), 1),
                "temp_c": _extract_optional_series_val(temp_values, idx),
                "gen_w": _extract_optional_series_val(gen_values, idx),
            }
        )
    return records
