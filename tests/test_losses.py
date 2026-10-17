"""Testes unitários para as funções de perda L2 (Squared Loss) e L1 (LAD)."""

import numpy as np

from src.core.losses import L1AbsoluteLoss, L2SquaredLoss


def test_l2_loss_calculation():
    """Testa o cálculo numérico da perda quadrática."""
    y_true = np.array([2.0, 4.0, 6.0])
    y_pred = np.array([1.0, 4.0, 8.0])
    # Residuos: [1, 0, -2] -> Quadrados: [1, 0, 4] -> Soma: 5.0
    loss_fn = L2SquaredLoss()
    assert np.isclose(loss_fn.calculate_loss(y_true, y_pred), 5.0)


def test_l1_loss_calculation():
    """Testa o cálculo numérico da perda absoluta."""
    y_true = np.array([2.0, 4.0, 6.0])
    y_pred = np.array([1.0, 4.0, 9.0])
    # Residuos: [1, 0, -3] -> Absolutos: [1, 0, 3] -> Soma: 4.0
    loss_fn = L1AbsoluteLoss()
    assert np.isclose(loss_fn.calculate_loss(y_true, y_pred), 4.0)


def test_l1_robustness_against_outliers(data_with_outliers):
    """Verifica que a perda L1 preserva o coeficiente angular real na presença de outliers."""
    x, y = data_with_outliers
    phi = np.column_stack([np.ones_like(x), x])

    l2_fn = L2SquaredLoss()
    l1_fn = L1AbsoluteLoss()

    theta_l2 = l2_fn.optimize(phi, y)
    theta_l1 = l1_fn.optimize(phi, y)

    true_slope = 1.8
    # O slope do L1 deve estar muito mais próximo de 1.8 do que o L2
    err_l1 = abs(theta_l1[1] - true_slope)
    err_l2 = abs(theta_l2[1] - true_slope)

    assert err_l1 < err_l2
    assert err_l1 < 0.2
