"""Testes unitários para os 4 modelos de regressão de demanda."""

import numpy as np

from src.core.losses import L2SquaredLoss
from src.core.models import (
    GaussianKernelRidgeModel,
    LinearRegressionModel,
    PolynomialRegressionModel,
    RBFRegressionModel,
)


def test_linear_model_fit_predict(synthetic_linear_data):
    """Verifica o ajuste e a predição do modelo linear."""
    x, y = synthetic_linear_data
    model = LinearRegressionModel()
    model.fit(x, y, loss_function=L2SquaredLoss())

    assert model.theta is not None
    assert len(model.theta) == 2
    # Slope esperado em torno de 2.5
    assert np.isclose(model.theta[1], 2.5, atol=0.2)

    preds = model.predict(x)
    assert len(preds) == len(x)


def test_polynomial_model_feature_transformation():
    """Valida a matriz de atributos do polinômio de grau 5."""
    x = np.array([2.0, 3.0])
    model = PolynomialRegressionModel(degree=5)
    phi = model.transform_features(x)

    # phi deve ter dimensões (2, 6): [1, x, x^2, x^3, x^4, x^5]
    assert phi.shape == (2, 6)
    assert np.allclose(phi[0], [1.0, 2.0, 4.0, 8.0, 16.0, 32.0])


def test_rbf_model_fit(synthetic_nonlinear_data):
    """Testa a regressão com 5 centros RBF e largura de banda sigma."""
    x, y = synthetic_nonlinear_data
    centers = np.linspace(min(x), max(x), 5)
    model = RBFRegressionModel(centers=centers, sigma=3.0)
    model.fit(x, y, loss_function=L2SquaredLoss())

    assert model.theta is not None
    assert len(model.theta) == 6  # 1 bias + 5 centros
    preds = model.predict(x)
    assert len(preds) == len(x)


def test_gaussian_kernel_ridge_fit():
    """Valida a regressão não-linear via Kernel Gaussiano com regularização Ridge."""
    np.random.seed(42)
    x = np.linspace(0, 10, 20)
    y = np.sin(x)

    model = GaussianKernelRidgeModel(sigma=2.0, reg_lambda=1e-4)
    model.fit(x, y, loss_function=L2SquaredLoss())

    preds = model.predict(x)
    # A curva ajustada deve acompanhar a senoide
    correlation = np.corrcoef(y, preds)[0, 1]
    assert correlation > 0.95
