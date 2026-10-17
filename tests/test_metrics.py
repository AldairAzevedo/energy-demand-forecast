"""Testes unitários para o calculador de métricas de desempenho."""

import numpy as np

from src.core.metrics import MetricsCalculator


def test_mse_exact():
    """Verifica o cálculo exato do Erro Quadrático Médio."""
    y_true = np.array([10.0, 20.0, 30.0])
    y_pred = np.array([12.0, 18.0, 33.0])
    # Erros: [2, -2, 3] -> Quadrados: [4, 4, 9] -> Media: 17 / 3 = 5.66666...
    expected_mse = 17.0 / 3.0
    calc_mse = MetricsCalculator.mse(y_true, y_pred)
    assert np.isclose(calc_mse, expected_mse)


def test_rmse_exact():
    """Verifica a raiz do erro quadrático médio."""
    y_true = np.array([10.0, 20.0])
    y_pred = np.array([13.0, 16.0])
    # Erros: [3, -4] -> Quadrados: [9, 16] -> MSE = 12.5 -> RMSE = sqrt(12.5) = 3.5355...
    expected_rmse = np.sqrt(12.5)
    calc_rmse = MetricsCalculator.rmse(y_true, y_pred)
    assert np.isclose(calc_rmse, expected_rmse)


def test_mae_exact():
    """Verifica o erro absoluto médio."""
    y_true = np.array([10.0, 20.0, 30.0])
    y_pred = np.array([12.0, 17.0, 34.0])
    # Absolutos: [2, 3, 4] -> Media = 3.0
    expected_mae = 3.0
    calc_mae = MetricsCalculator.mae(y_true, y_pred)
    assert np.isclose(calc_mae, expected_mae)


def test_r2_score_perfect_prediction():
    """Verifica se R2 é 1.0 para predições perfeitas."""
    y_true = np.array([5.0, 10.0, 15.0, 20.0])
    y_pred = np.array([5.0, 10.0, 15.0, 20.0])
    r2 = MetricsCalculator.r2_score(y_true, y_pred)
    assert np.isclose(r2, 1.0)


def test_evaluate_all_returns_expected_keys():
    """Valida a estrutura do dicionário de métricas completas."""
    y_true = np.array([10.0, 20.0, 30.0])
    y_pred = np.array([11.0, 19.0, 31.0])
    metrics = MetricsCalculator.evaluate_all(y_true, y_pred, runtime_ms=45.2)

    assert "mse" in metrics
    assert "rmse" in metrics
    assert "mae" in metrics
    assert "r2" in metrics
    assert "runtime_ms" in metrics
    assert metrics["runtime_ms"] == 45.2
