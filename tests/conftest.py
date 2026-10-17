"""Configuração global e fixtures reutilizáveis para os testes automatizados."""

import numpy as np
import pytest


@pytest.fixture
def synthetic_linear_data():
    """Gera dados sintéticos lineares simples com ruído controlado."""
    np.random.seed(42)
    x = np.linspace(20.0, 100.0, 50)
    # y = 2.5 * x + 10.0 + ruido
    noise = np.random.normal(0, 1.5, size=len(x))
    y = 2.5 * x + 10.0 + noise
    return x, y


@pytest.fixture
def synthetic_nonlinear_data():
    """Gera dados sintéticos quadráticos para validação de modelos flexíveis."""
    np.random.seed(42)
    x = np.linspace(0.0, 10.0, 40)
    y = 3.0 * (x**2) - 5.0 * x + 12.0 + np.random.normal(0, 2.0, size=len(x))
    return x, y


@pytest.fixture
def data_with_outliers():
    """Gera dados com outliers extremos para testar a robustez da perda L1 vs L2."""
    np.random.seed(42)
    x = np.linspace(10.0, 50.0, 30)
    y = 1.8 * x + 5.0
    # Injeta outliers severos nos índices 5 e 20
    y[5] += 150.0
    y[20] -= 120.0
    return x, y
