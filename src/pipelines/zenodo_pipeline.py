"""Pipeline de previsão de consumo energético para Smart Buildings (Competição Zenodo 2025)."""

import os
import time
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge

from src.core.metrics import MetricsCalculator
from src.utils.json_io import save_json


class ZenodoPipeline:
    """Orquestra o treinamento e avaliação multi-critério de previsão em Smart Buildings."""

    def __init__(self, data_dir: str, output_dir: str, results_dir: str) -> None:
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.results_dir = results_dir
        self.main_file = os.path.join(data_dir, "data_v1.0.xlsx")

    def run_cycle_07(self) -> Dict[str, Any]:
        """Ciclo 07: Previsão em Smart Building, Demanda Líquida e Métricas Multi-critério."""
        df = pd.read_excel(self.main_file)

        # Padroniza nomes das colunas
        df.columns = [c.strip().lower() for c in df.columns]
        power_col = [c for c in df.columns if "power" in c and "gen" not in c][0]
        gen_col = [c for c in df.columns if "gen" in c][0]
        temp_col = [c for c in df.columns if "temp" in c][0]

        df_clean = df.dropna(subset=[power_col, gen_col, temp_col]).copy()

        # Calcula a Demanda Líquida (Consumo - Geração Solar Fotovoltaica)
        df_clean["net_power"] = df_clean[power_col] - df_clean[gen_col]

        # Amostragem horária (agregação de 12 amostras de 5 min) para treino e validação robustos
        df_clean["hour_index"] = np.arange(len(df_clean)) // 12
        hourly = (
            df_clean.groupby("hour_index")
            .agg(
                {
                    power_col: "mean",
                    gen_col: "mean",
                    temp_col: "mean",
                    "net_power": "mean",
                }
            )
            .reset_index()
        )

        y = hourly[power_col].to_numpy()
        x_temp = hourly[temp_col].to_numpy()
        x_gen = hourly[gen_col].to_numpy()

        # Criação de Lags temporais (t-1 e t-24) para previsão em séries temporais
        lag_1 = np.roll(y, 1)
        lag_1[0] = y[0]
        lag_24 = np.roll(y, 24)
        lag_24[:24] = y[:24]

        x_matrix = np.column_stack([x_temp, x_gen, lag_1, lag_24])

        # Divisão Treino (80%) e Teste (20%)
        split_idx = int(0.8 * len(y))
        x_train, x_test = x_matrix[:split_idx], x_matrix[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # Modelo 1: Regressão Linear Regularizada (Ridge)
        t0 = time.perf_counter()
        ridge_model = Ridge(alpha=1.0)
        ridge_model.fit(x_train, y_train)
        time_ridge_ms = (time.perf_counter() - t0) * 1000.0
        preds_ridge = ridge_model.predict(x_test)
        metrics_ridge = MetricsCalculator.evaluate_all(
            y_test, preds_ridge, runtime_ms=time_ridge_ms
        )

        # Modelo 2: Floresta Aleatória Não-Linear (Random Forest)
        t0 = time.perf_counter()
        rf_model = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
        rf_model.fit(x_train, y_train)
        time_rf_ms = (time.perf_counter() - t0) * 1000.0
        preds_rf = rf_model.predict(x_test)
        metrics_rf = MetricsCalculator.evaluate_all(y_test, preds_rf, runtime_ms=time_rf_ms)

        # Análise de Demanda Líquida nos dados de teste
        net_test = hourly["net_power"].to_numpy()[split_idx:]
        solar_generation_test = x_gen[split_idx:]

        cycle_07_data = {
            "cycle_id": 7,
            "title": "Smart Building: Previsão de Carga e Métricas Multi-critério (Zenodo 2025)",
            "total_5min_samples": len(df_clean),
            "total_hourly_samples": len(hourly),
            "train_samples": len(y_train),
            "test_samples": len(y_test),
            "models_benchmarking": {
                "Ridge_Linear": {
                    "name": "Regressão Ridge com Lags Temporais",
                    "metrics": metrics_ridge,
                },
                "Random_Forest": {
                    "name": "Random Forest Regressor (50 árvores)",
                    "metrics": metrics_rf,
                },
            },
            "solar_energy_impact": {
                "mean_consumption_w": float(np.mean(y_test)),
                "mean_solar_generation_w": float(np.mean(solar_generation_test)),
                "mean_net_demand_w": float(np.mean(net_test)),
                "peak_solar_generation_w": float(np.max(solar_generation_test)),
                "solar_coverage_ratio_pct": round(
                    float(np.sum(solar_generation_test) / np.sum(y_test)) * 100.0, 2
                ),
            },
            "recent_predictions_sample": [
                {
                    "hour": idx + 1,
                    "real_power_w": round(float(y_test[idx]), 1),
                    "pred_ridge_w": round(float(preds_ridge[idx]), 1),
                    "pred_rf_w": round(float(preds_rf[idx]), 1),
                    "solar_pv_w": round(float(solar_generation_test[idx]), 1),
                    "net_demand_w": round(float(net_test[idx]), 1),
                }
                for idx in range(min(168, len(y_test)))  # Amostra de 1 semana (168h)
            ],
        }

        out_path = os.path.join(self.output_dir, "cycle_07_zenodo_smart_building.json")
        save_json(cycle_07_data, out_path)

        # Exporta figura de alta qualidade (300 DPI) para os slides de sábado
        self._export_figure(
            y_test[:168], preds_rf[:168], solar_generation_test[:168], net_test[:168]
        )
        return cycle_07_data

    def _export_figure(
        self,
        y_real: np.ndarray,
        y_pred: np.ndarray,
        solar_gen: np.ndarray,
        net_demand: np.ndarray,
    ) -> None:
        """Gera e salva gráfico da curva de carga do Smart Building e impacto solar."""
        os.makedirs(self.results_dir, exist_ok=True)
        fig, axes = plt.subplots(2, 1, figsize=(15, 8), sharex=True)
        hours = np.arange(len(y_real))

        # Painel 1: Previsão de Consumo (Real vs Random Forest)
        axes[0].plot(hours, y_real, label="Consumo Real (W)", color="#1E293B", linewidth=2.0)
        axes[0].plot(
            hours,
            y_pred,
            label="Previsão Random Forest (W)",
            color="#2563EB",
            linestyle="--",
            linewidth=1.8,
        )
        axes[0].set_title(
            "Previsão de Carga em Edifício Inteligente (Semana de Teste - 168 horas)",
            fontsize=12,
            fontweight="bold",
        )
        axes[0].set_ylabel("Potência Elétrica (W)", fontsize=11)
        axes[0].grid(True, linestyle="--", alpha=0.5)
        axes[0].legend(loc="upper right", framealpha=0.9)

        # Painel 2: Efeito da Geração Fotovoltaica e a Curva do Pato (Demanda Líquida)
        axes[1].plot(hours, y_real, label="Demanda Bruta Total (W)", color="#64748B", linewidth=1.5)
        axes[1].plot(
            hours, solar_gen, label="Geração Solar FV Telhado (W)", color="#EAB308", linewidth=1.8
        )
        axes[1].plot(
            hours,
            net_demand,
            label="Demanda Líquida da Rede (W)",
            color="#059669",
            linewidth=2.0,
        )
        axes[1].fill_between(hours, net_demand, y_real, color="#FEF08A", alpha=0.3)
        axes[1].set_title(
            "Impacto da Transição Energética: Geração Solar Distribuída e Demanda Líquida",
            fontsize=12,
            fontweight="bold",
        )
        axes[1].set_xlabel("Hora da Semana", fontsize=11)
        axes[1].set_ylabel("Potência (W)", fontsize=11)
        axes[1].grid(True, linestyle="--", alpha=0.5)
        axes[1].legend(loc="upper right", framealpha=0.9)

        plt.suptitle(
            "Competição Zenodo 2025: Previsão de Demanda e Integração Solar em Smart Buildings",
            fontsize=14,
            fontweight="bold",
            y=0.98,
        )
        plt.tight_layout()

        fig_path = os.path.join(self.results_dir, "zenodo_forecast.png")
        fig.savefig(fig_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
