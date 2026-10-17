"""Implementação dos 4 modelos de regressão de demanda elétrica do CMU 15-884."""

from typing import Optional

import numpy as np

from src.core.base import BaseLossFunction, BaseRegressionModel


class LinearRegressionModel(BaseRegressionModel):
    """Modelo 1: Regressão Linear Simples.

    Vetor de atributos: phi(x) = [1, x]
    """

    def __init__(self) -> None:
        super().__init__(name="Linear Simples")

    def transform_features(self, x: np.ndarray) -> np.ndarray:
        x_flat = np.asarray(x).ravel()
        bias = np.ones_like(x_flat)
        return np.column_stack([bias, x_flat])


class PolynomialRegressionModel(BaseRegressionModel):
    """Modelo 2: Regressão Polinomial.

    Vetor de atributos: phi(x) = [1, x, x^2, ..., x^d]
    """

    def __init__(self, degree: int = 5) -> None:
        super().__init__(name=f"Polinomial (Grau {degree})")
        self.degree = degree

    def transform_features(self, x: np.ndarray) -> np.ndarray:
        x_flat = np.asarray(x).ravel()
        cols = [np.ones_like(x_flat)]
        for p in range(1, self.degree + 1):
            cols.append(x_flat**p)
        return np.column_stack(cols)


class RBFRegressionModel(BaseRegressionModel):
    """Modelo 3: Funções de Base Radial (RBF) com centros fixos.

    Vetor de atributos: phi(x) = [1, exp(-(x - mu_1)^2 / (2*sigma^2)), ...]
    """

    def __init__(self, centers: np.ndarray, sigma: float = 20.0) -> None:
        super().__init__(name=f"RBF ({len(centers)} centros, σ={sigma})")
        self.centers = np.asarray(centers).ravel()
        self.sigma = sigma

    def transform_features(self, x: np.ndarray) -> np.ndarray:
        x_flat = np.asarray(x).ravel()
        cols = [np.ones_like(x_flat)]
        for mu in self.centers:
            basis = np.exp(-((x_flat - mu) ** 2) / (2.0 * (self.sigma**2)))
            cols.append(basis)
        return np.column_stack(cols)


class GaussianKernelRidgeModel(BaseRegressionModel):
    """Modelo 4: Regressão com Kernel Gaussiano e Regularização L2.

    Compara cada nova observação com todo o conjunto de treino histórico:
        phi_j(x) = exp(-(x - x_j)^2 / (2*sigma^2))
    Regularização: lambda = 1e-4
    """

    def __init__(self, sigma: float = 20.0, reg_lambda: float = 1e-4) -> None:
        super().__init__(name=f"Kernel Gaussiano (σ={sigma}, λ={reg_lambda})")
        self.sigma = sigma
        self.reg_lambda = reg_lambda
        self.x_train: Optional[np.ndarray] = None

    def fit(
        self,
        x: np.ndarray,
        y: np.ndarray,
        loss_function: BaseLossFunction,
        reg_lambda: Optional[float] = None,
    ) -> "GaussianKernelRidgeModel":
        """Armazena os pontos de treino para composição do Kernel e ajusta pesos."""
        self.x_train = np.asarray(x).ravel()
        effective_lambda = self.reg_lambda if reg_lambda is None else reg_lambda
        return super().fit(x, y, loss_function, reg_lambda=effective_lambda)

    def transform_features(self, x: np.ndarray) -> np.ndarray:
        """Gera a matriz de kernel Gaussiano em relação aos pontos de treino."""
        if self.x_train is None:
            # Caso ainda não ajustado, utiliza x como base preliminar
            base_points = np.asarray(x).ravel()
        else:
            base_points = self.x_train

        x_flat = np.asarray(x).ravel()
        cols = [np.ones_like(x_flat)]
        for x_train_i in base_points:
            kernel_val = np.exp(-((x_flat - x_train_i) ** 2) / (2.0 * (self.sigma**2)))
            cols.append(kernel_val)
        return np.column_stack(cols)
