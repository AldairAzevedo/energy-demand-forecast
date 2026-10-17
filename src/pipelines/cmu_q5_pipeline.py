"""Pipeline de execução para os Itens 5 do CMU 15-884 (Ciclos 01 e 02)."""

import os
import time
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np

from src.core.losses import L1AbsoluteLoss, L2SquaredLoss
from src.core.metrics import MetricsCalculator
from src.core.models import (
    GaussianKernelRidgeModel,
    LinearRegressionModel,
    PolynomialRegressionModel,
    RBFRegressionModel,
)
from src.utils.json_io import save_json


class CMUQ5Pipeline:
    """Orquestra o carregamento de dados e ajuste dos 4 modelos com perdas L1 e L2."""

    def __init__(self, data_dir: str, output_dir: str, results_dir: str) -> None:
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.results_dir = results_dir

        self.temp_file = os.path.join(data_dir, "q5_max_temp.txt")
        self.demand_file = os.path.join(data_dir, "q5_max_demand.txt")

    def run_cycle_01(self) -> Dict[str, Any]:
        """Executa o Ciclo 01: Ingestão e validação estruturada dos dados brutos."""
        temps = np.loadtxt(self.temp_file, dtype=float)
        demands = np.loadtxt(self.demand_file, dtype=float)

        cycle_01_data = {
            "cycle_id": 1,
            "title": "Dados Brutos: Temperatura Máxima e Pico de Demanda (CMU Q5)",
            "sample_size": int(len(temps)),
            "units": {"temperature": "°F", "demand": "GW"},
            "summary_stats": {
                "temperature": {
                    "min": float(np.min(temps)),
                    "max": float(np.max(temps)),
                    "mean": float(np.mean(temps)),
                    "std": float(np.std(temps)),
                },
                "demand": {
                    "min": float(np.min(demands)),
                    "max": float(np.max(demands)),
                    "mean": float(np.mean(demands)),
                    "std": float(np.std(demands)),
                },
            },
            "records": [
                {"day": idx + 1, "temperature": float(t), "demand": float(d)}
                for idx, (t, d) in enumerate(zip(temps, demands))
            ],
        }

        out_path = os.path.join(self.output_dir, "cycle_01_cmu_q5_raw.json")
        save_json(cycle_01_data, out_path)
        return cycle_01_data

    def run_cycle_02(self) -> Dict[str, Any]:
        """Executa o Ciclo 02: Ajuste dos 4 modelos sob perdas L2 (OLS) e L1 (LAD)."""
        temps = np.loadtxt(self.temp_file, dtype=float)
        demands = np.loadtxt(self.demand_file, dtype=float)

        t_min, t_max = float(np.min(temps)), float(np.max(temps))
        # Malha contínua densa para renderização no dashboard
        t_grid = np.linspace(0.0, 110.0, 220)

        # 5 centros RBF distribuídos na faixa térmica dos dados
        rbf_centers = np.linspace(t_min, t_max, 5)

        loss_functions = [("L2", L2SquaredLoss()), ("L1", L1AbsoluteLoss())]
        models_configs = [
            ("Linear", lambda: LinearRegressionModel()),
            ("Polinomial_d5", lambda: PolynomialRegressionModel(degree=5)),
            ("RBF", lambda: RBFRegressionModel(centers=rbf_centers, sigma=20.0)),
            ("Kernel_Gaussiano", lambda: GaussianKernelRidgeModel(sigma=20.0, reg_lambda=1e-4)),
        ]

        fitted_results = {}
        for loss_key, loss_fn in loss_functions:
            fitted_results[loss_key] = {}
            for model_key, model_factory in models_configs:
                model = model_factory()
                t0 = time.perf_counter()
                model.fit(temps, demands, loss_function=loss_fn)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0

                train_preds = model.predict(temps)
                grid_preds = model.predict(t_grid)
                metrics = MetricsCalculator.evaluate_all(
                    demands, train_preds, runtime_ms=elapsed_ms
                )

                fitted_results[loss_key][model_key] = {
                    "model_name": model.name,
                    "loss_type": loss_key,
                    "theta": [float(val) for val in model.theta],
                    "metrics": metrics,
                    "train_predictions": [float(p) for p in train_preds],
                    "grid_predictions": [float(p) for p in grid_preds],
                    "residuals": [float(r) for r in (demands - train_preds)],
                }

        cycle_02_data = {
            "cycle_id": 2,
            "title": "Modelos Ajustados: 4 Arquiteturas sob Perdas L2 e L1",
            "grid_temperatures": [float(t) for t in t_grid],
            "models": fitted_results,
        }

        out_path = os.path.join(self.output_dir, "cycle_02_cmu_q5_fitted_models.json")
        save_json(cycle_02_data, out_path)

        # Exporta figura estática de alta qualidade (300 DPI) para os slides de sábado
        self._export_figure(temps, demands, t_grid, fitted_results)
        return cycle_02_data

    def _export_figure(
        self,
        temps: np.ndarray,
        demands: np.ndarray,
        t_grid: np.ndarray,
        fitted_results: Dict[str, Any],
    ) -> None:
        """Gera e salva gráfico comparativo dos modelos para os slides de apresentação."""
        os.makedirs(self.results_dir, exist_ok=True)
        fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=True)

        colors = {
            "Linear": "#2563EB",  # Azul
            "Polinomial_d5": "#DC2626",  # Vermelho
            "RBF": "#16A34A",  # Verde
            "Kernel_Gaussiano": "#9333EA",  # Roxo
        }

        titles = [
            ("L2", "Função de Perda Quadrática (L2 - OLS)"),
            ("L1", "Função de Perda Absoluta Robusta (L1 - LAD)"),
        ]

        for ax, (loss_key, loss_title) in zip(axes, titles):
            ax.scatter(
                temps,
                demands,
                color="#64748B",
                alpha=0.6,
                s=20,
                label="Demanda Real Observada",
                edgecolors="none",
            )
            for model_key, style_color in colors.items():
                m_info = fitted_results[loss_key][model_key]
                label_txt = f"{m_info['model_name']} (R²: {m_info['metrics']['r2']:.3f})"
                ax.plot(
                    t_grid,
                    m_info["grid_predictions"],
                    label=label_txt,
                    color=style_color,
                    linewidth=2.0,
                )

            ax.set_title(loss_title, fontsize=12, fontweight="bold", pad=10)
            ax.set_xlabel("Temperatura Máxima Diária (°F)", fontsize=11)
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.legend(loc="upper left", fontsize=9, framealpha=0.9)

        axes[0].set_ylabel("Pico de Demanda Diária (GW)", fontsize=11)
        plt.suptitle(
            "CMU 15-884 - Item 5: Regressões Demanda de Pico vs. Temperatura",
            fontsize=14,
            fontweight="bold",
            y=0.98,
        )
        plt.tight_layout()

        fig_path = os.path.join(self.results_dir, "cmu_q5_fits.png")
        fig.savefig(fig_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
