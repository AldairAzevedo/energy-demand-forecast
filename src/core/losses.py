"""Implementação das funções de perda L2 (Squared Loss) e L1 (LAD / Absolute Loss)."""

import numpy as np
from scipy.optimize import minimize

from src.core.base import BaseLossFunction


class L2SquaredLoss(BaseLossFunction):
    """Função de perda quadrática (Mínimos Quadrados Ordinários / OLS).

    Calcula a soma dos quadrados dos resíduos:
        J(theta) = sum (y_i - phi_i * theta)^2 + lambda * ||theta||^2
    Solução analítica exata via Equações Normais:
        theta = (phi^T * phi + lambda * I)^(-1) * phi^T * y
    """

    def calculate_loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calcula o somatório dos quadrados dos erros."""
        residuals = y_true - y_pred
        return float(np.sum(residuals**2))

    def optimize(
        self,
        phi: np.ndarray,
        y: np.ndarray,
        reg_lambda: float = 0.0,
    ) -> np.ndarray:
        """Resolve analiticamente o problema de mínimos quadrados regularizados."""
        phi_t_phi = phi.T @ phi
        if reg_lambda > 0.0:
            reg_matrix = reg_lambda * np.eye(phi_t_phi.shape[0])
            # Preserva o bias sem penalização se desejado, ou penaliza toda a diagonal
            phi_t_phi = phi_t_phi + reg_matrix
        phi_t_y = phi.T @ y
        return np.linalg.solve(phi_t_phi, phi_t_y)


class L1AbsoluteLoss(BaseLossFunction):
    """Função de perda absoluta (Least Absolute Deviations - LAD).

    Robusta a valores discrepantes (outliers):
        J(theta) = sum |y_i - phi_i * theta| + lambda * ||theta||^2
    """

    def calculate_loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calcula o somatório dos erros absolutos."""
        residuals = y_true - y_pred
        return float(np.sum(np.abs(residuals)))

    def optimize(
        self,
        phi: np.ndarray,
        y: np.ndarray,
        reg_lambda: float = 0.0,
    ) -> np.ndarray:
        """Minimiza a soma dos desvios absolutos via otimização numérica convexa."""
        # Inicialização quente utilizando a solução dos mínimos quadrados
        l2_solver = L2SquaredLoss()
        initial_theta = l2_solver.optimize(phi, y, reg_lambda=reg_lambda)

        def objective(theta: np.ndarray) -> float:
            errors = y - phi @ theta
            cost = np.sum(np.abs(errors))
            if reg_lambda > 0.0:
                cost += reg_lambda * np.sum(theta**2)
            return float(cost)

        result = minimize(
            objective,
            initial_theta,
            method="Powell",
            options={"xtol": 1e-5, "ftol": 1e-5, "maxiter": 2000},
        )
        return result.x
