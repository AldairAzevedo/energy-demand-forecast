"""Classes abstratas base para modelos e funções de perda (SOLID / POO)."""

from abc import ABC, abstractmethod
from typing import Optional

import numpy as np


class BaseLossFunction(ABC):
    """Interface abstrata para cálculo de perda e otimização paramétrica."""

    @abstractmethod
    def calculate_loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calcula o custo escalar da função de perda.

        Args:
            y_true: Vetor com valores observados reais.
            y_pred: Vetor com valores preditos pelo modelo.

        Returns:
            Valor escalar da perda calculada.
        """
        pass

    @abstractmethod
    def optimize(
        self,
        phi: np.ndarray,
        y: np.ndarray,
        reg_lambda: float = 0.0,
    ) -> np.ndarray:
        """Determina o vetor de parâmetros ótimo minimizando a perda.

        Args:
            phi: Matriz de atributos projetada (N x D).
            y: Vetor de alvos reais (N,).
            reg_lambda: Fator de regularização L2 (opcional).

        Returns:
            Vetor ótimo de pesos theta (D,).
        """
        pass


class BaseRegressionModel(ABC):
    """Interface base para modelos de regressão de demanda elétrica."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.theta: Optional[np.ndarray] = None
        self.loss_name: Optional[str] = None

    @abstractmethod
    def transform_features(self, x: np.ndarray) -> np.ndarray:
        """Mapeia a variável de entrada no espaço de features do modelo.

        Args:
            x: Vetor unidimensional de entrada (ex: temperatura).

        Returns:
            Matriz de design phi de dimensões (N, D).
        """
        pass

    def fit(
        self,
        x: np.ndarray,
        y: np.ndarray,
        loss_function: BaseLossFunction,
        reg_lambda: float = 0.0,
    ) -> "BaseRegressionModel":
        """Ajusta os parâmetros do modelo minimizando a perda especificada.

        Args:
            x: Vetor de entrada com medições.
            y: Vetor com alvos observados (demanda).
            loss_function: Instância da função de perda (L1 ou L2).
            reg_lambda: Fator de regularização L2.

        Returns:
            A própria instância do modelo ajustada.
        """
        phi = self.transform_features(x)
        self.theta = loss_function.optimize(phi, y, reg_lambda=reg_lambda)
        self.loss_name = loss_function.__class__.__name__
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        """Calcula as estimativas de demanda para novas entradas.

        Args:
            x: Vetor de entrada.

        Returns:
            Vetor com valores preditos.

        Raises:
            RuntimeError: Caso o modelo ainda não tenha sido ajustado.
        """
        if self.theta is None:
            raise RuntimeError(f"O modelo '{self.name}' precisa ser ajustado antes de prever.")
        phi = self.transform_features(x)
        return phi @ self.theta
