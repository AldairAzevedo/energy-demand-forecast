"""Pipeline de execução para os Itens 6 do CMU 15-884 (Ciclos 03, 04, 05 e 06)."""

import os
import time
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np

from src.core.losses import L2SquaredLoss
from src.core.metrics import MetricsCalculator
from src.core.models import PolynomialRegressionModel
from src.core.preprocessor import DataCleaner, FeatureEngineer, TimeSeriesInterpolator
from src.utils.json_io import save_json


class CMUQ6Pipeline:
    """Orquestra o tratamento de dados brutos, interpolação e modelagem multivariada."""

    def __init__(self, data_dir: str, output_dir: str, results_dir: str) -> None:
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.results_dir = results_dir

        self.demand_file = os.path.join(data_dir, "q6_demand.txt")
        self.weather_file = os.path.join(data_dir, "q6_weather.txt")

    def run_cycle_03(self) -> Dict[str, Any]:
        """Ciclo 03: Tratamento de valores sentinelas (-9999) e deduplicação de timestamps."""
        weather_raw = np.loadtxt(self.weather_file, dtype=float)

        raw_times = weather_raw[:, 0]
        n_original = len(raw_times)

        # Detecta e contabiliza sentinelas antes da limpeza
        feature_names = [
            "Temperatura (°F)",
            "Ponto de Orvalho (°F)",
            "Umidade Relativa (%)",
            "Pressão Atmosférica (inHg)",
            "Velocidade do Vento (mph)",
        ]

        sentinels_count = {}
        cleaned_features = []

        for idx, name in enumerate(feature_names, start=1):
            col_raw = weather_raw[:, idx]
            n_sentinels = int(np.sum((col_raw <= -9000.0) | np.isclose(col_raw, -9999.0)))
            sentinels_count[name] = n_sentinels

            col_clean = DataCleaner.replace_sentinel(col_raw, sentinel=-9999.0)
            col_filled = DataCleaner.fill_missing_linear(col_clean)
            cleaned_features.append(col_filled)

        cleaned_matrix = np.column_stack([raw_times] + cleaned_features)

        # Deduplica timestamps
        times_unique, unique_indices = np.unique(cleaned_matrix[:, 0], return_index=True)
        cleaned_matrix = cleaned_matrix[unique_indices]

        cycle_03_data = {
            "cycle_id": 3,
            "title": "Limpeza de Sensores Meteorológicos: Sentinelas e Deduplicação",
            "original_records_count": n_original,
            "cleaned_records_count": int(len(cleaned_matrix)),
            "sentinels_detected": sentinels_count,
            "features_summary": {
                name: {
                    "min": float(np.min(cleaned_matrix[:, i])),
                    "max": float(np.max(cleaned_matrix[:, i])),
                    "mean": float(np.mean(cleaned_matrix[:, i])),
                    "std": float(np.std(cleaned_matrix[:, i])),
                }
                for i, name in enumerate(feature_names, start=1)
            },
        }

        out_path = os.path.join(self.output_dir, "cycle_03_cmu_q6_cleaned_weather.json")
        save_json(cycle_03_data, out_path)
        return cycle_03_data

    def run_cycle_04(self) -> Dict[str, Any]:
        """Ciclo 04: Interpolação temporal linear para sincronizar clima com demanda horária."""
        demand_raw = np.loadtxt(self.demand_file, dtype=float)
        weather_raw = np.loadtxt(self.weather_file, dtype=float)

        target_times = demand_raw[:, 0]
        weather_times = weather_raw[:, 0]

        interpolated_cols = []
        for col_idx in range(1, 6):
            col_raw = weather_raw[:, col_idx]
            col_clean = DataCleaner.replace_sentinel(col_raw)
            col_filled = DataCleaner.fill_missing_linear(col_clean)
            col_interp = TimeSeriesInterpolator.interpolate_1d(
                source_times=weather_times,
                source_values=col_filled,
                target_times=target_times,
            )
            interpolated_cols.append(col_interp)

        synced_weather = np.column_stack(interpolated_cols)

        cycle_04_data = {
            "cycle_id": 4,
            "title": "Sincronização Temporal Horária: Interpolação Linear de Clima",
            "total_hourly_timestamps": int(len(target_times)),
            "start_timestamp": float(target_times[0]),
            "end_timestamp": float(target_times[-1]),
            "mean_hourly_demand_mw": float(np.mean(demand_raw[:, 1])),
            "mean_hourly_temperature_f": float(np.mean(synced_weather[:, 0])),
        }

        out_path = os.path.join(self.output_dir, "cycle_04_cmu_q6_interpolated_sync.json")
        save_json(cycle_04_data, out_path)
        return cycle_04_data

    def run_cycle_05(self) -> Dict[str, Any]:
        """Ciclo 05: Agregação diária e geração da matriz de atributos multivariados."""
        demand_raw = np.loadtxt(self.demand_file, dtype=float)
        weather_raw = np.loadtxt(self.weather_file, dtype=float)

        target_times = demand_raw[:, 0]
        weather_times = weather_raw[:, 0]

        # Interpola colunas para as horas de demanda
        interp_cols = []
        for col_idx in range(1, 6):
            col_clean = DataCleaner.fill_missing_linear(
                DataCleaner.replace_sentinel(weather_raw[:, col_idx])
            )
            col_interp = TimeSeriesInterpolator.interpolate_1d(
                weather_times, col_clean, target_times
            )
            interp_cols.append(col_interp)

        # Agregação Diária (24 horas por dia)
        daily_peak_demand = FeatureEngineer.aggregate_daily_max(demand_raw[:, 1])
        daily_max_temp = FeatureEngineer.aggregate_daily_max(interp_cols[0])
        daily_mean_dewpoint = FeatureEngineer.aggregate_daily_mean(interp_cols[1])
        daily_mean_humidity = FeatureEngineer.aggregate_daily_mean(interp_cols[2])
        daily_mean_pressure = FeatureEngineer.aggregate_daily_mean(interp_cols[3])
        daily_mean_wind = FeatureEngineer.aggregate_daily_mean(interp_cols[4])

        n_days = len(daily_peak_demand)
        features_matrix = np.column_stack(
            [
                daily_max_temp,
                daily_mean_dewpoint,
                daily_mean_humidity,
                daily_mean_pressure,
                daily_mean_wind,
            ]
        )

        # Matriz de correlação linear com a demanda de pico
        correlations = {}
        names = ["temp_max", "dewpoint_mean", "humidity_mean", "pressure_mean", "wind_mean"]
        for idx, name in enumerate(names):
            corr = float(np.corrcoef(features_matrix[:, idx], daily_peak_demand)[0, 1])
            correlations[name] = round(corr, 4)

        cycle_05_data = {
            "cycle_id": 5,
            "title": "Engenharia de Atributos: Agregação Diária e Matriz Multivariada",
            "total_days": n_days,
            "correlations_with_peak_demand": correlations,
            "daily_samples": [
                {
                    "day": d + 1,
                    "peak_demand_mw": round(float(daily_peak_demand[d]), 2),
                    "temp_max_f": round(float(daily_max_temp[d]), 2),
                    "dewpoint_mean_f": round(float(daily_mean_dewpoint[d]), 2),
                    "humidity_mean_pct": round(float(daily_mean_humidity[d]), 2),
                    "pressure_mean_inhg": round(float(daily_mean_pressure[d]), 2),
                    "wind_mean_mph": round(float(daily_mean_wind[d]), 2),
                }
                for d in range(min(n_days, 100))  # Amostra representativa no JSON
            ],
        }

        out_path = os.path.join(self.output_dir, "cycle_05_cmu_q6_daily_features.json")
        save_json(cycle_05_data, out_path)
        return cycle_05_data

    def run_cycle_06(self) -> Dict[str, Any]:
        """Ciclo 06: Benchmarking e prova empírica da redução do MSE multivariado."""
        demand_raw = np.loadtxt(self.demand_file, dtype=float)
        weather_raw = np.loadtxt(self.weather_file, dtype=float)

        target_times = demand_raw[:, 0]
        weather_times = weather_raw[:, 0]

        interp_cols = []
        for col_idx in range(1, 6):
            col_clean = DataCleaner.fill_missing_linear(
                DataCleaner.replace_sentinel(weather_raw[:, col_idx])
            )
            col_interp = TimeSeriesInterpolator.interpolate_1d(
                weather_times, col_clean, target_times
            )
            interp_cols.append(col_interp)

        daily_peak_demand = FeatureEngineer.aggregate_daily_max(demand_raw[:, 1])
        daily_max_temp = FeatureEngineer.aggregate_daily_max(interp_cols[0])
        daily_mean_dewpoint = FeatureEngineer.aggregate_daily_mean(interp_cols[1])
        daily_mean_humidity = FeatureEngineer.aggregate_daily_mean(interp_cols[2])
        daily_mean_pressure = FeatureEngineer.aggregate_daily_mean(interp_cols[3])
        daily_mean_wind = FeatureEngineer.aggregate_daily_mean(interp_cols[4])

        y = daily_peak_demand

        # 1. Modelo Univariado: Polinomial grau 5 em T_max
        poly_univariate = PolynomialRegressionModel(degree=5)
        t0 = time.perf_counter()
        poly_univariate.fit(daily_max_temp, y, loss_function=L2SquaredLoss())
        runtime_uni_ms = (time.perf_counter() - t0) * 1000.0

        preds_univariate = poly_univariate.predict(daily_max_temp)
        metrics_uni = MetricsCalculator.evaluate_all(y, preds_univariate, runtime_ms=runtime_uni_ms)

        # 2. Modelo Multivariado: Matriz multivariada estendida
        # (Polinômio em T_max + variáveis lineares do clima)
        # phi_multi = [1, T, T^2, T^3, T^4, T^5, dewpoint, humidity, pressure, wind]
        phi_t = poly_univariate.transform_features(daily_max_temp)
        climate_extra = np.column_stack(
            [
                daily_mean_dewpoint,
                daily_mean_humidity,
                daily_mean_pressure,
                daily_mean_wind,
            ]
        )
        # Padroniza variáveis extras para estabilidade numérica
        norm_climate, _, _ = FeatureEngineer.standardize(climate_extra)
        phi_multivariate = np.column_stack([phi_t, norm_climate])

        # Ajuste via L2 com regularização Ridge leve para o multivariado
        l2_solver = L2SquaredLoss()
        t0 = time.perf_counter()
        theta_multi = l2_solver.optimize(phi_multivariate, y, reg_lambda=1e-3)
        runtime_multi_ms = (time.perf_counter() - t0) * 1000.0

        preds_multivariate = phi_multivariate @ theta_multi
        metrics_multi = MetricsCalculator.evaluate_all(
            y, preds_multivariate, runtime_ms=runtime_multi_ms
        )

        # Cálculo da redução percentual de MSE
        mse_uni = metrics_uni["mse"]
        mse_multi = metrics_multi["mse"]
        mse_reduction_pct = round(((mse_uni - mse_multi) / mse_uni) * 100.0, 2)

        cycle_06_data = {
            "cycle_id": 6,
            "title": "Benchmarking Univariado vs. Multivariado: Validação de Feature Engineering",
            "univariate_model": {
                "name": "Polinomial (Grau 5) - Apenas Temperatura Máxima",
                "features_count": 1,
                "metrics": metrics_uni,
            },
            "multivariate_model": {
                "name": "Multivariado Completo (T_max^5 + Orvalho + Umidade + Pressão + Vento)",
                "features_count": 5,
                "metrics": metrics_multi,
            },
            "comparison": {
                "mse_univariate": mse_uni,
                "mse_multivariate": mse_multi,
                "mse_reduction_percentage": mse_reduction_pct,
                "r2_univariate": metrics_uni["r2"],
                "r2_multivariate": metrics_multi["r2"],
            },
        }

        out_path = os.path.join(self.output_dir, "cycle_06_cmu_q6_multivariate_comparison.json")
        save_json(cycle_06_data, out_path)

        # Exporta figura comparativa em alta resolução para os slides de sábado
        self._export_figure(y, preds_univariate, preds_multivariate, metrics_uni, metrics_multi)
        return cycle_06_data

    def _export_figure(
        self,
        y_true: np.ndarray,
        y_uni: np.ndarray,
        y_multi: np.ndarray,
        m_uni: Dict[str, Any],
        m_multi: Dict[str, Any],
    ) -> None:
        """Gera e salva gráfico comparativo do benefício da engenharia de atributos."""
        os.makedirs(self.results_dir, exist_ok=True)
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))

        # Painel 1: Gráfico de Dispersão Predito vs Observado
        axes[0].scatter(
            y_true, y_uni, alpha=0.5, color="#2563EB", label=f"Univariado (R²: {m_uni['r2']:.3f})"
        )
        axes[0].scatter(
            y_true,
            y_multi,
            alpha=0.5,
            color="#16A34A",
            label=f"Multivariado (R²: {m_multi['r2']:.3f})",
        )
        min_v, max_v = min(y_true), max(y_true)
        axes[0].plot(
            [min_v, max_v], [min_v, max_v], "r--", linewidth=2.0, label="Linha Ideal (y=x)"
        )
        axes[0].set_title(
            "Acurácia Preditiva: Observado vs. Predito", fontsize=12, fontweight="bold"
        )
        axes[0].set_xlabel("Demanda de Pico Real (MW)", fontsize=11)
        axes[0].set_ylabel("Demanda de Pico Predita (MW)", fontsize=11)
        axes[0].grid(True, linestyle="--", alpha=0.5)
        axes[0].legend(loc="upper left")

        # Painel 2: Comparação em Barras do MSE e RMSE
        labels = ["MSE (MW² / 1000)", "RMSE (MW)", "MAE (MW)"]
        uni_vals = [m_uni["mse"] / 1000.0, m_uni["rmse"], m_uni["mae"]]
        multi_vals = [m_multi["mse"] / 1000.0, m_multi["rmse"], m_multi["mae"]]

        x_pos = np.arange(len(labels))
        width = 0.35

        axes[1].bar(x_pos - width / 2, uni_vals, width, label="Univariado (T_max)", color="#3B82F6")
        axes[1].bar(
            x_pos + width / 2,
            multi_vals,
            width,
            label="Multivariado (+ Clima Completo)",
            color="#10B981",
        )
        axes[1].set_title(
            "Redução Quantitativa dos Erros de Previsão", fontsize=12, fontweight="bold"
        )
        axes[1].set_xticks(x_pos)
        axes[1].set_xticklabels(labels, fontsize=10)
        axes[1].grid(True, linestyle="--", alpha=0.5, axis="y")
        axes[1].legend(loc="upper right")

        plt.suptitle(
            "CMU 15-884 - Item 6: Impacto da Engenharia de Features na Previsão de Carga",
            fontsize=14,
            fontweight="bold",
            y=0.98,
        )
        plt.tight_layout()

        fig_path = os.path.join(self.results_dir, "cmu_q6_features.png")
        fig.savefig(fig_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
