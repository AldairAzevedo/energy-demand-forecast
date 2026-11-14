"""Diagnóstico puro de aprendizado (Treino vs. Teste) e mapa de acertos/erros."""

from typing import Any, Dict, List, Tuple

import numpy as np

DAY_PERIODS: Tuple[Tuple[str, int, int], ...] = (
    ("Madrugada (00h–05h)", 0, 5),
    ("Manhã (06h–11h)", 6, 11),
    ("Tarde (12h–17h)", 12, 17),
    ("Noite (18h–23h)", 18, 23),
)

SELECTION_CRITERIA: Dict[str, str] = {
    "multi_criteria": "🏆 Multi-Critério Zenodo (Acurácia + Equilíbrio + Velocidade)",
}

CRITERION_DESCRIPTIONS: Dict[str, str] = {
    "multi_criteria": (
        "Combina acurácia no teste (RMSE + MAE + R² = 80%), equilíbrio Treino-Teste (15%) "
        "e velocidade de execução (5%) em uma nota de 0 a 100."
    ),
}

RANK_BADGES: Tuple[str, ...] = ("🏆 1º Campeão", "🥈 2º Lugar", "🥉 3º Lugar")


def format_rank_badge(pos: int) -> str:
    """Retorna o selo dinâmico de classificação (0-indexado)."""
    if 0 <= pos < len(RANK_BADGES):
        return RANK_BADGES[pos]
    return f"{pos + 1}º Lugar"


def compute_multi_criteria_score(
    test_metrics: Dict[str, Any],
    train_metrics: Dict[str, Any],
    mean_ref_power_w: float = 2000.0,
) -> float:
    """Calcula nota composta (0 a 100) alinhada à avaliação multi-critério Zenodo 2025."""
    ref_power = max(float(mean_ref_power_w), 1.0)
    rmse = float(test_metrics.get("rmse", ref_power))
    mae = float(test_metrics.get("mae", ref_power))
    test_r2 = float(test_metrics.get("r2", 0.0))
    runtime_ms = max(float(test_metrics.get("runtime_ms", 0.0)), 0.0)

    train_r2 = float(train_metrics.get("r2", test_r2))
    gap_pct = max(0.0, (train_r2 - test_r2) * 100.0)

    acc_rmse = max(0.0, 1.0 - rmse / (0.6 * ref_power))
    acc_mae = max(0.0, 1.0 - mae / (0.5 * ref_power))
    acc_r2 = max(0.0, min(1.0, test_r2))
    accuracy_score = 0.50 * acc_rmse + 0.35 * acc_mae + 0.15 * acc_r2

    underfit_penalty = 1.0 if test_r2 >= 0.70 else max(0.0, test_r2 / 0.70)
    excess_gap = max(0.0, gap_pct - 6.0)
    generalization_score = max(0.0, 1.0 - excess_gap / 14.0) * underfit_penalty
    speed_score = 1.0 / (1.0 + runtime_ms / 5000.0)

    total = 100.0 * (0.80 * accuracy_score + 0.15 * generalization_score + 0.05 * speed_score)
    return round(max(0.0, min(100.0, total)), 2)


def criterion_rank_key(
    model_entry: Dict[str, Any],
    criterion: str = "multi_criteria",
) -> Tuple[float, float]:
    """Retorna tupla de ordenação (menor = melhor) pelo Multi-Critério oficial Zenodo."""
    _ = criterion
    metrics = model_entry.get("metrics", {})
    train_metrics = model_entry.get("train_metrics", {})
    rmse = float(metrics.get("rmse", float("inf")))
    score = float(
        metrics.get(
            "multi_criteria_score",
            compute_multi_criteria_score(metrics, train_metrics),
        )
    )
    return (-score, rmse)


def rank_benchmarking_models(
    benchmarking: Dict[str, Any],
    criterion: str = "multi_criteria",
) -> List[Tuple[str, Dict[str, Any]]]:
    """Ordena dinamicamente os modelos do 1º (Campeão) ao último pelo critério ativo."""
    items = [(key, info) for key, info in benchmarking.items() if isinstance(info, dict)]
    return sorted(items, key=lambda kv: criterion_rank_key(kv[1], criterion))


def diagnose_learning_status(
    train_r2: float,
    test_r2: float,
    train_rmse: float,
    test_rmse: float,
) -> Dict[str, Any]:
    """Classifica o comportamento entre Treino e Teste (Overfitting / Underfitting / Bom Ajuste)."""
    gap_r2_pct = round((float(train_r2) - float(test_r2)) * 100.0, 2)
    safe_train_rmse = max(float(train_rmse), 1e-6)
    overfit_ratio = round(float(test_rmse) / safe_train_rmse, 2)

    if test_r2 < 0.75 and train_r2 < 0.80:
        status = "Underfitting (Aprendeu Pouco)"
        summary = "Erro alto tanto no treino quanto no teste; faltam atributos ou flexibilidade."
    elif gap_r2_pct >= 6.0 or overfit_ratio >= 1.8:
        status = "Overfitting (Decorou Treino)"
        summary = "Acertou muito no treino, mas perdeu precisão ao enfrentar dados novos no teste."
    elif gap_r2_pct >= 3.0 or overfit_ratio >= 1.35:
        status = "Leve Sobreajuste"
        summary = "Treino perceptivelmente melhor que o teste; vale regularizar ou podar atributos."
    else:
        status = "Bom Ajuste (Equilibrado)"
        summary = "Aprendizado generalizou bem do treino para o teste."

    return {
        "status": status,
        "summary": summary,
        "gap_r2_pct": gap_r2_pct,
        "overfit_ratio": overfit_ratio,
    }


def _compute_period_breakdown(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    hours: np.ndarray,
) -> List[Dict[str, Any]]:
    breakdown: List[Dict[str, Any]] = []
    errors = y_pred - y_true
    abs_err = np.abs(errors)

    for label, start_h, end_h in DAY_PERIODS:
        mask = (hours >= start_h) & (hours <= end_h)
        count = int(np.sum(mask))
        if count == 0:
            breakdown.append(
                {
                    "period": label,
                    "samples": 0,
                    "mae_w": 0.0,
                    "rmse_w": 0.0,
                    "hit_rate_200w_pct": 0.0,
                }
            )
            continue

        p_abs = abs_err[mask]
        p_err = errors[mask]
        breakdown.append(
            {
                "period": label,
                "samples": count,
                "mae_w": round(float(np.mean(p_abs)), 2),
                "rmse_w": round(float(np.sqrt(np.mean(p_err**2))), 2),
                "hit_rate_200w_pct": round(float(np.mean(p_abs <= 200.0) * 100.0), 1),
            }
        )
    return breakdown


def _extract_extreme_cases(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    hours: np.ndarray,
    indices: np.ndarray,
) -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    for idx in indices:
        i = int(idx)
        real_v = float(y_true[i])
        pred_v = float(y_pred[i])
        cases.append(
            {
                "test_hour_index": i + 1,
                "hour_of_day": int(round(float(hours[i]))) % 24,
                "real_w": round(real_v, 1),
                "pred_w": round(pred_v, 1),
                "abs_error_w": round(abs(pred_v - real_v), 1),
            }
        )
    return cases


def compute_error_diagnostics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    hours_of_day: np.ndarray,
) -> Dict[str, Any]:
    """Calcula mapa de acertos e erros (faixas de tolerância, turnos do dia e extremos)."""
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    hrs = np.asarray(hours_of_day, dtype=float)

    if len(y_t) == 0:
        return {
            "hit_rate_100w_pct": 0.0,
            "hit_rate_200w_pct": 0.0,
            "high_error_rate_300w_pct": 0.0,
            "mean_bias_w": 0.0,
            "p95_abs_error_w": 0.0,
            "max_abs_error_w": 0.0,
            "period_breakdown": [],
            "top_worst_hours": [],
            "top_best_hours": [],
        }

    signed_err = y_p - y_t
    abs_err = np.abs(signed_err)
    sorted_idx = np.argsort(abs_err)
    top_k = min(5, len(abs_err))

    return {
        "hit_rate_100w_pct": round(float(np.mean(abs_err <= 100.0) * 100.0), 1),
        "hit_rate_200w_pct": round(float(np.mean(abs_err <= 200.0) * 100.0), 1),
        "high_error_rate_300w_pct": round(float(np.mean(abs_err > 300.0) * 100.0), 1),
        "mean_bias_w": round(float(np.mean(signed_err)), 2),
        "p95_abs_error_w": round(float(np.percentile(abs_err, 95)), 2),
        "max_abs_error_w": round(float(np.max(abs_err)), 2),
        "period_breakdown": _compute_period_breakdown(y_t, y_p, hrs),
        "top_worst_hours": _extract_extreme_cases(y_t, y_p, hrs, sorted_idx[-top_k:][::-1]),
        "top_best_hours": _extract_extreme_cases(y_t, y_p, hrs, sorted_idx[:top_k]),
    }
