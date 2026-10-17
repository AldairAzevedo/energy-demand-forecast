"""Módulo para cálculo de métricas quantitativas de acurácia e desempenho."""

from typing import Any, Dict

import numpy as np


class MetricsCalculator:
    """Calculadora de métricas de avaliação multi-critério (CMU e Zenodo 2025)."""

    @staticmethod
    def mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calcula o Erro Quadrático Médio (Mean Squared Error)."""
        residuals = np.asarray(y_true).ravel() - np.asarray(y_pred).ravel()
        return float(np.mean(residuals**2))

    @staticmethod
    def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calcula a Raiz do Erro Quadrático Médio (Root Mean Squared Error)."""
        return float(np.sqrt(MetricsCalculator.mse(y_true, y_pred)))

    @staticmethod
    def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calcula o Erro Absoluto Médio (Mean Absolute Error)."""
        residuals = np.asarray(y_true).ravel() - np.asarray(y_pred).ravel()
        return float(np.mean(np.abs(residuals)))

    @staticmethod
    def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calcula o Coeficiente de Determinação (R² Score)."""
        y_true_arr = np.asarray(y_true).ravel()
        y_pred_arr = np.asarray(y_pred).ravel()
        total_ss = np.sum((y_true_arr - np.mean(y_true_arr)) ** 2)
        if total_ss < 1e-12:
            return 1.0 if np.allclose(y_true_arr, y_pred_arr) else 0.0
        residual_ss = np.sum((y_true_arr - y_pred_arr) ** 2)
        return float(1.0 - (residual_ss / total_ss))

    @staticmethod
    def evaluate_all(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        runtime_ms: float = 0.0,
    ) -> Dict[str, Any]:
        """Calcula simultaneamente todas as métricas multi-critério."""
        return {
            "mse": round(MetricsCalculator.mse(y_true, y_pred), 4),
            "rmse": round(MetricsCalculator.rmse(y_true, y_pred), 4),
            "mae": round(MetricsCalculator.mae(y_true, y_pred), 4),
            "r2": round(MetricsCalculator.r2_score(y_true, y_pred), 4),
            "runtime_ms": round(runtime_ms, 2),
        }
