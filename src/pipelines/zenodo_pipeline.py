"""Pipeline de previsão de consumo elétrico em Smart Buildings (Competição Zenodo 2025)."""

import os
import time
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge

from src.core.metrics import MetricsCalculator
from src.utils.json_io import save_json


class ZenodoPipeline:
    """Orquestra o treinamento e avaliação multi-critério de previsão de consumo elétrico."""

    def __init__(self, data_dir: str, output_dir: str, results_dir: str) -> None:
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.results_dir = results_dir
        self.main_file = os.path.join(data_dir, "data_v1.0.xlsx")

    @staticmethod
    def _find_col(columns: List[str], keyword: str, exclude: str = "") -> str | None:
        for col in columns:
            if keyword in col and (not exclude or exclude not in col):
                return col
        return None

    @staticmethod
    def _extract_hours(df: pd.DataFrame, time_col: str | None) -> np.ndarray:
        if time_col is None:
            return np.arange(len(df)) % 24
        parsed = pd.to_datetime(df[time_col].astype(str), format="%H:%M:%S", errors="coerce")
        if parsed.notna().all():
            return parsed.dt.hour.to_numpy(dtype=float)
        return np.arange(len(df)) % 24

    def _prepare_hourly_dataset(self) -> Tuple[np.ndarray, np.ndarray, int]:
        """Lê a telemetria de 5 min, agrega em base horária e cria atributos causais."""
        df = pd.read_excel(self.main_file)
        df.columns = [c.strip().lower() for c in df.columns]
        cols = list(df.columns)

        power_col = self._find_col(cols, "power", exclude="gen")
        gen_col = self._find_col(cols, "gen")
        temp_col = self._find_col(cols, "temp")
        volt_col = self._find_col(cols, "volt")
        amp_col = self._find_col(cols, "amp")
        time_col = self._find_col(cols, "time")

        required = [c for c in [power_col, gen_col, temp_col] if c is not None]
        df_clean = df.dropna(subset=required).copy()
        total_5min_samples = len(df_clean)

        agg_map: Dict[str, str] = {power_col: "mean"}
        if gen_col:
            agg_map[gen_col] = "mean"
        if temp_col:
            agg_map[temp_col] = "mean"
        if volt_col:
            agg_map[volt_col] = "mean"
        if amp_col:
            agg_map[amp_col] = "mean"

        df_clean["hour_bucket"] = np.arange(len(df_clean)) // 12
        df_clean["hour_of_day"] = self._extract_hours(df_clean, time_col)
        agg_map["hour_of_day"] = "first"

        hourly = df_clean.groupby("hour_bucket").agg(agg_map).reset_index(drop=True)

        features = pd.DataFrame(index=hourly.index)
        y_series = hourly[power_col].astype(float)

        hours = hourly["hour_of_day"].astype(float)
        features["hour_sin"] = np.sin(2.0 * np.pi * hours / 24.0)
        features["hour_cos"] = np.cos(2.0 * np.pi * hours / 24.0)

        if temp_col:
            features["temp_c"] = hourly[temp_col].astype(float)
        if gen_col:
            features["gen_w"] = hourly[gen_col].astype(float)

        fallback_power = float(y_series.mean()) if len(y_series) > 0 else 0.0
        for lag in (1, 2, 3, 24, 48, 168):
            features[f"power_lag_{lag}"] = y_series.shift(lag).bfill().fillna(fallback_power)

        features["power_roll_mean_6"] = (
            y_series.shift(1).rolling(6, min_periods=1).mean().bfill().fillna(fallback_power)
        )
        features["power_roll_mean_24"] = (
            y_series.shift(1).rolling(24, min_periods=1).mean().bfill().fillna(fallback_power)
        )
        features["power_roll_std_24"] = (
            y_series.shift(1).rolling(24, min_periods=1).std().fillna(0.0)
        )

        if volt_col:
            features["voltage_lag_1"] = hourly[volt_col].astype(float).shift(1).bfill().fillna(0.0)
        if amp_col:
            features["amperage_lag_1"] = hourly[amp_col].astype(float).shift(1).bfill().fillna(0.0)

        return (
            features.fillna(0.0).to_numpy(dtype=float),
            y_series.to_numpy(dtype=float),
            total_5min_samples,
        )

    @staticmethod
    def _train_and_evaluate(
        model: Any,
        x_train: np.ndarray,
        y_train: np.ndarray,
        x_test: np.ndarray,
        y_test: np.ndarray,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        t_train_start = time.perf_counter()
        model.fit(x_train, y_train)
        train_time_ms = (time.perf_counter() - t_train_start) * 1000.0

        t_inf_start = time.perf_counter()
        preds = model.predict(x_test)
        inference_time_ms = (time.perf_counter() - t_inf_start) * 1000.0

        metrics = MetricsCalculator.evaluate_all(
            y_test,
            preds,
            train_time_ms=train_time_ms,
            inference_time_ms=inference_time_ms,
        )
        return preds, metrics

    def run(self) -> Dict[str, Any]:
        """Executa o pipeline completo de previsão de consumo elétrico (Zenodo 2025)."""
        x_matrix, y, total_5min_samples = self._prepare_hourly_dataset()

        split_idx = int(0.8 * len(y))
        x_train, x_test = x_matrix[:split_idx], x_matrix[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        models_spec = [
            ("Ridge_Linear", "Ridge Linear (Baseline)", Ridge(alpha=1.0)),
            (
                "Random_Forest",
                "Random Forest (100 árvores)",
                RandomForestRegressor(n_estimators=100, max_depth=16, random_state=42, n_jobs=-1),
            ),
            (
                "Hist_Gradient_Boosting",
                "HistGradientBoosting (Tabular)",
                HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, random_state=42),
            ),
        ]

        benchmarking: Dict[str, Any] = {}
        predictions: Dict[str, np.ndarray] = {}

        for key, display_name, estimator in models_spec:
            preds, metrics = self._train_and_evaluate(estimator, x_train, y_train, x_test, y_test)
            benchmarking[key] = {"name": display_name, "metrics": metrics}
            predictions[key] = preds

        best_key = min(benchmarking, key=lambda k: benchmarking[k]["metrics"]["rmse"])

        sample_len = min(168, len(y_test))
        forecast_data = {
            "competition": "2025 Competition on Electric Energy Consumption Forecast (Zenodo)",
            "title": "Previsão de Consumo Elétrico em Smart Building (Zenodo 2025)",
            "target_variable": "power (W)",
            "total_5min_samples": total_5min_samples,
            "total_hourly_samples": len(y),
            "train_samples": len(y_train),
            "test_samples": len(y_test),
            "mean_test_power_w": round(float(np.mean(y_test)), 2),
            "best_model_key": best_key,
            "best_model_name": benchmarking[best_key]["name"],
            "models_benchmarking": benchmarking,
            "recent_predictions_sample": [
                {
                    "hour": idx + 1,
                    "real_power_w": round(float(y_test[idx]), 1),
                    "pred_ridge_w": round(float(predictions["Ridge_Linear"][idx]), 1),
                    "pred_rf_w": round(float(predictions["Random_Forest"][idx]), 1),
                    "pred_hgb_w": round(float(predictions["Hist_Gradient_Boosting"][idx]), 1),
                }
                for idx in range(sample_len)
            ],
        }

        out_path = os.path.join(self.output_dir, "zenodo_forecast_results.json")
        save_json(forecast_data, out_path)

        self._export_figure(
            y_test[:sample_len],
            predictions["Ridge_Linear"][:sample_len],
            predictions["Random_Forest"][:sample_len],
            predictions["Hist_Gradient_Boosting"][:sample_len],
        )
        return forecast_data

    def _export_figure(
        self,
        y_real: np.ndarray,
        y_pred_ridge: np.ndarray,
        y_pred_rf: np.ndarray,
        y_pred_hgb: np.ndarray,
    ) -> None:
        """Gera e salva gráfico em 300 DPI comparando consumo real vs. modelos preditivos."""
        os.makedirs(self.results_dir, exist_ok=True)
        fig, ax = plt.subplots(figsize=(14, 5.5))
        hours = np.arange(len(y_real))

        ax.plot(hours, y_real, label="Consumo Real Medido (W)", color="#8B5CF6", linewidth=2.4)
        ax.plot(
            hours,
            y_pred_hgb,
            label="HistGradientBoosting (W)",
            color="#0284C7",
            linewidth=2.0,
        )
        ax.plot(
            hours,
            y_pred_rf,
            label="Random Forest (W)",
            color="#059669",
            linestyle="--",
            linewidth=1.8,
        )
        ax.plot(
            hours,
            y_pred_ridge,
            label="Ridge Linear (W)",
            color="#EA580C",
            linestyle=":",
            linewidth=1.8,
        )

        ax.set_title(
            "Competição Zenodo 2025: Previsão Horária de Consumo Elétrico (Semana de Teste - 168h)",
            fontsize=13,
            fontweight="bold",
        )
        ax.set_xlabel("Hora da Amostra de Teste", fontsize=11)
        ax.set_ylabel("Potência Ativa Consumida (W)", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.45)
        ax.legend(loc="upper right", framealpha=0.95)
        plt.tight_layout()

        fig_path = os.path.join(self.results_dir, "zenodo_forecast.png")
        fig.savefig(fig_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
