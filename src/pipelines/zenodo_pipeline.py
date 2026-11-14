"""Pipeline parametrizável cross-dataset de previsão 1h (Competição Zenodo 2025)."""

import hashlib
import json
import os
import time
from collections import OrderedDict
from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge

from src.core.diagnostics import (
    compute_error_diagnostics,
    compute_multi_criteria_score,
    diagnose_learning_status,
    rank_benchmarking_models,
)
from src.core.forecasting import (
    SCENARIO_LABELS,
    build_context_records,
    build_post_cutoff_records,
    resolve_effective_feature_config,
    resolve_warmup_length,
    sanitize_scenario,
    scenario_supports_generation,
)
from src.core.metrics import MetricsCalculator
from src.core.parameter_schema import (
    MODEL_DISPLAY_NAMES,
    MODEL_KEYS,
    get_default_all_configs,
    get_parameter_taxonomy,
    sanitize_model_config,
)
from src.pipelines.dataset_loader import load_hourly_series, load_v4_days
from src.utils.file_resilience import read_bytes_resilient
from src.utils.json_io import load_json, save_json

DatasetBundle = Tuple[pd.DataFrame, Dict[str, Optional[str]], int]
_MAX_FORECAST_CACHE = 16
_FORECAST_MEMORY_CACHE: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()


def clear_pipeline_cache() -> None:
    """Limpa o cache em memória de execuções completas do pipeline."""
    _FORECAST_MEMORY_CACHE.clear()


class ZenodoPipeline:
    """Orquestra atributos causais, treino 1h e validação cross-dataset com Ponto de Corte."""

    def __init__(self, data_dir: str, output_dir: str, results_dir: str) -> None:
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.results_dir = results_dir
        self.main_file = os.path.join(data_dir, "data_v1.0.xlsx")
        self.v2_file = os.path.join(data_dir, "data_v2.0.xlsx")

    def _load_scenario_tables(self, scenario: str) -> Dict[str, DatasetBundle]:
        """Carrega apenas os arquivos Excel exigidos pelo cenário escolhido."""
        tables: Dict[str, DatasetBundle] = {
            "v1": load_hourly_series(self.main_file, dataset_tag="v1")
        }
        if scenario in ("v1_to_v2", "v1_v2_to_v4"):
            tables["v2"] = load_hourly_series(self.v2_file, dataset_tag="v2")
        if scenario == "v1_v2_to_v4":
            tables["v4"] = load_v4_days(self.data_dir, days=(1, 2, 3))
        return tables

    @staticmethod
    def _append_time_features(
        features: pd.DataFrame,
        hourly: pd.DataFrame,
        feat_cfg: Dict[str, Any],
    ) -> None:
        hours = hourly["hour_of_day"].astype(float)
        if feat_cfg.get("use_cyclical_hour", True):
            features["hour_sin"] = np.sin(2.0 * np.pi * hours / 24.0)
            features["hour_cos"] = np.cos(2.0 * np.pi * hours / 24.0)
        if feat_cfg.get("use_raw_hour", False):
            features["hour_raw"] = hours

    @staticmethod
    def _append_covariate_features(
        features: pd.DataFrame,
        hourly: pd.DataFrame,
        col_map: Dict[str, Optional[str]],
        feat_cfg: Dict[str, Any],
    ) -> None:
        if feat_cfg.get("use_temperature", True) and col_map["temp"]:
            features["temp_c"] = hourly[col_map["temp"]].astype(float)
        if feat_cfg.get("use_generation", True) and col_map["gen"]:
            features["gen_w"] = hourly[col_map["gen"]].astype(float)
        if feat_cfg.get("use_electrical_lags", True):
            if col_map["volt"]:
                features["voltage_lag_1"] = (
                    hourly[col_map["volt"]].astype(float).shift(1).bfill().fillna(0.0)
                )
            if col_map["amp"]:
                features["amperage_lag_1"] = (
                    hourly[col_map["amp"]].astype(float).shift(1).bfill().fillna(0.0)
                )

    @staticmethod
    def _append_lag_and_rolling_features(
        features: pd.DataFrame,
        y_series: pd.Series,
        feat_cfg: Dict[str, Any],
    ) -> None:
        fallback_power = float(y_series.mean()) if len(y_series) > 0 else 0.0
        for lag in feat_cfg.get("power_lags", []):
            features[f"power_lag_{lag}"] = y_series.shift(lag).bfill().fillna(fallback_power)

        shifted = y_series.shift(1)
        for win in feat_cfg.get("rolling_mean_windows", []):
            features[f"power_roll_mean_{win}"] = (
                shifted.rolling(win, min_periods=1).mean().bfill().fillna(fallback_power)
            )
        for win in feat_cfg.get("rolling_std_windows", []):
            features[f"power_roll_std_{win}"] = (
                shifted.rolling(win, min_periods=1).std().fillna(0.0)
            )

    def _build_feature_matrix(
        self,
        hourly: pd.DataFrame,
        col_map: Dict[str, Optional[str]],
        feat_cfg: Dict[str, Any],
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Constrói matriz causal X e vetor alvo y conforme hiperparâmetros e covariáveis."""
        power_col = col_map["power"]
        if not power_col:
            raise ValueError("Coluna de potência ativa 'power (W)' não encontrada no dataset.")

        y_series = hourly[power_col].astype(float)
        features = pd.DataFrame(index=hourly.index)

        self._append_time_features(features, hourly, feat_cfg)
        self._append_covariate_features(features, hourly, col_map, feat_cfg)
        self._append_lag_and_rolling_features(features, y_series, feat_cfg)

        if features.shape[1] == 0:
            hours = hourly["hour_of_day"].astype(float)
            features["hour_sin"] = np.sin(2.0 * np.pi * hours / 24.0)
            features["hour_cos"] = np.cos(2.0 * np.pi * hours / 24.0)

        feature_names = list(features.columns)
        return (
            features.fillna(0.0).to_numpy(dtype=float),
            y_series.to_numpy(dtype=float),
            feature_names,
        )

    @staticmethod
    def _build_estimator(model_key: str, cfg: Dict[str, Any]) -> Any:
        hp = cfg["hyperparameters"]
        seed = int(cfg["split"]["random_state"])

        if model_key == "Ridge_Linear":
            return Ridge(alpha=float(hp["alpha"]))

        if model_key == "Random_Forest":
            return RandomForestRegressor(
                n_estimators=int(hp["n_estimators"]),
                max_depth=int(hp["max_depth"]),
                min_samples_leaf=int(hp["min_samples_leaf"]),
                random_state=seed,
                n_jobs=min(2, os.cpu_count() or 1),
            )

        hgb_depth = int(hp["max_depth"])
        return HistGradientBoostingRegressor(
            max_iter=int(hp["max_iter"]),
            learning_rate=float(hp["learning_rate"]),
            max_depth=None if hgb_depth == 0 else hgb_depth,
            l2_regularization=float(hp["l2_regularization"]),
            random_state=seed,
        )

    @staticmethod
    def _train_and_evaluate(
        model: Any,
        x_train: np.ndarray,
        y_train: np.ndarray,
        x_test: np.ndarray,
        y_test: np.ndarray,
    ) -> Tuple[np.ndarray, Dict[str, Any], Dict[str, Any]]:
        t_train_start = time.perf_counter()
        model.fit(x_train, y_train)
        train_time_ms = (time.perf_counter() - t_train_start) * 1000.0

        preds_train = model.predict(x_train)
        train_metrics = MetricsCalculator.evaluate_all(y_train, preds_train)

        t_inf_start = time.perf_counter()
        preds_test = model.predict(x_test)
        inference_time_ms = (time.perf_counter() - t_inf_start) * 1000.0

        test_metrics = MetricsCalculator.evaluate_all(
            y_test,
            preds_test,
            train_time_ms=train_time_ms,
            inference_time_ms=inference_time_ms,
        )
        return preds_test, test_metrics, train_metrics

    def _prepare_scenario_arrays(
        self,
        scenario: str,
        eff_feat: Dict[str, Any],
        split_cfg: Dict[str, Any],
        tables: Dict[str, DatasetBundle],
    ) -> Dict[str, Any]:
        """Prepara matrizes Treino/Teste, warm-up sem leakage e fatias de contexto/corte."""
        ctx_hours = int(split_cfg.get("context_hours", 72))

        if scenario == "v1_to_v2":
            hourly_v1, col_v1, _ = tables["v1"]
            hourly_v2, col_v2, _ = tables["v2"]
            x_train, y_train, feat_names = self._build_feature_matrix(hourly_v1, col_v1, eff_feat)
            x_v2, y_v2, _ = self._build_feature_matrix(hourly_v2, col_v2, eff_feat)
            warmup = resolve_warmup_length(len(y_v2), ctx_hours)
            return {
                "x_train": x_train,
                "y_train": y_train,
                "x_test": x_v2[warmup:],
                "y_test": y_v2[warmup:],
                "feature_names": feat_names,
                "context_df": hourly_v2.iloc[max(0, warmup - ctx_hours) : warmup],
                "context_col_map": col_v2,
                "test_df": hourly_v2.iloc[warmup:],
                "test_col_map": col_v2,
                "cutoff_label": f"Corte em v2.0 após {warmup}h de aquecimento (Treino 100% v1.0)",
            }

        if scenario == "v1_v2_to_v4":
            hourly_v1, col_v1, _ = tables["v1"]
            hourly_v2, col_v2, _ = tables["v2"]
            hourly_v4, col_v4, _ = tables["v4"]
            x_v1, y_v1, feat_names = self._build_feature_matrix(hourly_v1, col_v1, eff_feat)
            x_v2, y_v2, _ = self._build_feature_matrix(hourly_v2, col_v2, eff_feat)
            x_v4, y_v4, _ = self._build_feature_matrix(hourly_v4, col_v4, eff_feat)
            warmup = min(24, max(1, len(y_v4) // 3))
            return {
                "x_train": np.vstack([x_v1, x_v2]),
                "y_train": np.concatenate([y_v1, y_v2]),
                "x_test": x_v4[warmup:],
                "y_test": y_v4[warmup:],
                "feature_names": feat_names,
                "context_df": hourly_v4.iloc[:warmup],
                "context_col_map": col_v4,
                "test_df": hourly_v4.iloc[warmup:],
                "test_col_map": col_v4,
                "cutoff_label": "Corte após Dia 1 (24h) de v4 → Teste Dias 2–3 (48h)",
            }

        hourly_v1, col_v1, _ = tables["v1"]
        x_mat, y_arr, feat_names = self._build_feature_matrix(hourly_v1, col_v1, eff_feat)
        split_idx = max(1, min(len(y_arr) - 1, int(float(split_cfg["train_ratio"]) * len(y_arr))))
        return {
            "x_train": x_mat[:split_idx],
            "y_train": y_arr[:split_idx],
            "x_test": x_mat[split_idx:],
            "y_test": y_arr[split_idx:],
            "feature_names": feat_names,
            "context_df": hourly_v1.iloc[max(0, split_idx - ctx_hours) : split_idx],
            "context_col_map": col_v1,
            "test_df": hourly_v1.iloc[split_idx:],
            "test_col_map": col_v1,
            "cutoff_label": f"Corte em t={split_idx}h ({int(split_cfg['train_ratio'] * 100)}%)",
        }

    def _scenario_cache_hash(
        self, scenario: str, resolved_cfgs: Dict[str, Dict[str, Any]], horizon_pref: int
    ) -> str:
        """Constrói hash SHA-256 portável entre Windows/Linux por cenário, configs e dados."""
        files_to_check = [self.main_file]
        if scenario in ("v1_to_v2", "v1_v2_to_v4"):
            files_to_check.append(self.v2_file)
        if scenario == "v1_v2_to_v4":
            for day_idx in (1, 2, 3):
                files_to_check.append(
                    os.path.join(
                        self.data_dir, f"data_v4.{day_idx}.1_weather_forecast_day_{day_idx}.xlsx"
                    )
                )
                files_to_check.append(
                    os.path.join(
                        self.data_dir, f"data_v4.{day_idx}.2_real_consumption_day_{day_idx}.xlsx"
                    )
                )
        file_sigs: Dict[str, Dict[str, Any]] = {}
        for path in files_to_check:
            raw = read_bytes_resilient(path)
            file_sigs[os.path.basename(path)] = {
                "size": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        canonical = json.dumps(
            {
                "cache_version": "1",
                "scenario": scenario,
                "horizon_pref": horizon_pref,
                "configs": resolved_cfgs,
                "files": file_sigs,
            },
            sort_keys=True,
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]

    def _run_single_model(
        self,
        model_key: str,
        cfg: Dict[str, Any],
        scenario: str,
        tables: Dict[str, DatasetBundle],
        arrays_cache: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Tuple[Dict[str, Any], np.ndarray, Dict[str, Any]]:
        eff_feat = resolve_effective_feature_config(scenario, cfg["features"])
        split_cfg = cfg["split"]
        arrays_key = json.dumps(
            {
                "eff_feat": eff_feat,
                "train_ratio": float(split_cfg.get("train_ratio", 0.8)),
                "context_hours": int(split_cfg.get("context_hours", 72)),
            },
            sort_keys=True,
        )
        if arrays_cache is not None and arrays_key in arrays_cache:
            arrays = arrays_cache[arrays_key]
        else:
            arrays = self._prepare_scenario_arrays(scenario, eff_feat, split_cfg, tables)
            if arrays_cache is not None:
                arrays_cache[arrays_key] = arrays
        x_train, y_train = arrays["x_train"], arrays["y_train"]
        x_test, y_test = arrays["x_test"], arrays["y_test"]
        test_hours = arrays["test_df"]["hour_of_day"].to_numpy(dtype=float)

        estimator = self._build_estimator(model_key, cfg)
        preds_test, test_metrics, train_metrics = self._train_and_evaluate(
            estimator, x_train, y_train, x_test, y_test
        )
        test_metrics["multi_criteria_score"] = compute_multi_criteria_score(
            test_metrics,
            train_metrics,
            mean_ref_power_w=float(np.mean(y_test)) if len(y_test) > 0 else 2000.0,
        )

        learning_diagnosis = diagnose_learning_status(
            train_metrics["r2"],
            test_metrics["r2"],
            train_metrics["rmse"],
            test_metrics["rmse"],
        )
        error_diagnostics = compute_error_diagnostics(y_test, preds_test, test_hours)

        bench_entry = {
            "name": MODEL_DISPLAY_NAMES[model_key],
            "metrics": test_metrics,
            "train_metrics": train_metrics,
            "learning_diagnosis": learning_diagnosis,
            "error_diagnostics": error_diagnostics,
            "features_used": arrays["feature_names"],
            "num_features": len(arrays["feature_names"]),
            "train_samples": len(y_train),
            "test_samples": len(y_test),
            "config_used": cfg,
            "effective_features": eff_feat,
        }
        return bench_entry, preds_test, arrays

    @staticmethod
    def _extract_col_list(df: pd.DataFrame, col_name: Optional[str]) -> Optional[List[float]]:
        if not col_name or col_name not in df.columns:
            return None
        return df[col_name].astype(float).tolist()

    def _build_forecast_payload(
        self,
        scenario: str,
        tables: Dict[str, DatasetBundle],
        benchmarking: Dict[str, Any],
        predictions: Dict[str, np.ndarray],
        ref_arrays: Dict[str, Any],
        horizon_pref: int,
    ) -> Dict[str, Any]:
        ranked = rank_benchmarking_models(benchmarking)
        best_key = ranked[0][0]
        y_test = ref_arrays["y_test"]
        horizon_len = min(horizon_pref, len(y_test))

        ctx_df: pd.DataFrame = ref_arrays["context_df"]
        ctx_map: Dict[str, Optional[str]] = ref_arrays["context_col_map"]
        test_df: pd.DataFrame = ref_arrays["test_df"].iloc[:horizon_len]
        test_map: Dict[str, Optional[str]] = ref_arrays["test_col_map"]

        context_sample = build_context_records(
            y_context=self._extract_col_list(ctx_df, ctx_map["power"]) or [],
            timestamps=ctx_df["timestamp_label"].astype(str).tolist(),
            temp_values=self._extract_col_list(ctx_df, ctx_map["temp"]),
            gen_values=self._extract_col_list(ctx_df, ctx_map["gen"]),
        )
        post_sample = build_post_cutoff_records(
            y_test=y_test[:horizon_len],
            preds_by_model={k: predictions[k][:horizon_len] for k in MODEL_KEYS},
            timestamps=test_df["timestamp_label"].astype(str).tolist(),
            horizon_len=horizon_len,
            temp_values=self._extract_col_list(test_df, test_map["temp"]),
            gen_values=self._extract_col_list(test_df, test_map["gen"]),
        )

        total_5min = sum(bundle[2] for bundle in tables.values())
        total_hourly = sum(len(bundle[0]) for bundle in tables.values())
        any_temp = any(
            bool(benchmarking[k].get("effective_features", {}).get("use_temperature", True))
            for k in benchmarking
        )
        any_gen = any(
            bool(benchmarking[k].get("effective_features", {}).get("use_generation", True))
            for k in benchmarking
        )
        return {
            "competition": "2025 Competition on Electric Energy Consumption Forecast (Zenodo)",
            "title": "Previsão de Consumo Elétrico em Smart Building (Zenodo 2025)",
            "target_variable": "power (W)",
            "evaluation_scenario": scenario,
            "scenario_label": SCENARIO_LABELS[scenario],
            "cutoff_label": ref_arrays["cutoff_label"],
            "has_generation": scenario_supports_generation(scenario),
            "active_covariates": {
                "use_temperature": any_temp,
                "use_generation": any_gen and scenario_supports_generation(scenario),
            },
            "active_run_id": "-",
            "context_hours": len(context_sample),
            "horizon_hours": len(post_sample),
            "total_5min_samples": total_5min,
            "total_hourly_samples": total_hourly,
            "train_samples": benchmarking[best_key]["train_samples"],
            "test_samples": benchmarking[best_key]["test_samples"],
            "mean_test_power_w": round(float(np.mean(y_test)), 2),
            "best_model_key": best_key,
            "best_model_name": benchmarking[best_key]["name"],
            "parameter_taxonomy": get_parameter_taxonomy(),
            "models_benchmarking": benchmarking,
            "context_sample": context_sample,
            "recent_predictions_sample": post_sample,
        }

    def _load_cached_forecast(
        self,
        scenario: str,
        mem_key: str,
        disk_cache_path: str,
    ) -> Optional[Dict[str, Any]]:
        """Recupera previsão em cache (RAM ou JSON em disco) quando idêntica ao pedido."""
        cached_payload = _FORECAST_MEMORY_CACHE.get(mem_key)
        if cached_payload is not None:
            _FORECAST_MEMORY_CACHE.move_to_end(mem_key)
            return deepcopy(cached_payload)

        if not os.path.exists(disk_cache_path):
            return None
        try:
            disk_payload = load_json(disk_cache_path)
            is_valid = (
                isinstance(disk_payload, dict)
                and "models_benchmarking" in disk_payload
                and disk_payload.get("evaluation_scenario") == scenario
            )
            if is_valid:
                self._store_memory_forecast(mem_key, disk_payload)
                return disk_payload
        except (OSError, ValueError):
            return None
        return None

    @staticmethod
    def _store_memory_forecast(mem_key: str, forecast_data: Dict[str, Any]) -> None:
        _FORECAST_MEMORY_CACHE[mem_key] = deepcopy(forecast_data)
        if len(_FORECAST_MEMORY_CACHE) > _MAX_FORECAST_CACHE:
            _FORECAST_MEMORY_CACHE.popitem(last=False)

    def run(
        self,
        model_configs: Optional[Dict[str, Dict[str, Any]]] = None,
        export_figure: bool = True,
    ) -> Dict[str, Any]:
        """Executa o pipeline completo no cenário ativo com corte causal e previsão 1h."""
        raw_cfgs = model_configs if model_configs is not None else get_default_all_configs()
        resolved_cfgs = {key: sanitize_model_config(key, raw_cfgs.get(key)) for key in MODEL_KEYS}

        base_split = resolved_cfgs[MODEL_KEYS[0]]["split"]
        scenario = sanitize_scenario(base_split.get("evaluation_scenario"))
        horizon_pref = int(base_split.get("horizon_hours", 168))

        out_path = os.path.join(self.output_dir, "zenodo_forecast_results.json")
        cache_hash = self._scenario_cache_hash(scenario, resolved_cfgs, horizon_pref)
        mem_key = f"{os.path.abspath(self.data_dir)}::{cache_hash}"
        disk_cache_path = os.path.join(self.output_dir, "_forecast_cache", f"{cache_hash}.json")

        cached_forecast = self._load_cached_forecast(scenario, mem_key, disk_cache_path)
        if cached_forecast is not None:
            save_json(cached_forecast, out_path)
            if export_figure:
                self._export_figure(cached_forecast)
            return cached_forecast

        tables = self._load_scenario_tables(scenario)

        benchmarking: Dict[str, Any] = {}
        predictions: Dict[str, np.ndarray] = {}
        ref_arrays: Optional[Dict[str, Any]] = None
        arrays_cache: Dict[str, Dict[str, Any]] = {}

        for key in MODEL_KEYS:
            entry, preds, arrays = self._run_single_model(
                key,
                resolved_cfgs[key],
                scenario,
                tables,
                arrays_cache=arrays_cache,
            )
            benchmarking[key] = entry
            predictions[key] = preds
            if ref_arrays is None:
                ref_arrays = arrays

        assert ref_arrays is not None
        forecast_data = self._build_forecast_payload(
            scenario, tables, benchmarking, predictions, ref_arrays, horizon_pref
        )

        self._store_memory_forecast(mem_key, forecast_data)
        try:
            save_json(forecast_data, disk_cache_path)
        except OSError:
            pass

        save_json(forecast_data, out_path)
        if export_figure:
            self._export_figure(forecast_data)
        return forecast_data

    def _export_figure(self, forecast_data: Dict[str, Any]) -> None:
        """Gera e salva figura 300 DPI com contexto pré-corte, linha de corte e previsões."""
        os.makedirs(self.results_dir, exist_ok=True)
        fig = Figure(figsize=(14, 5.5))
        FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)

        ctx = forecast_data.get("context_sample", [])
        post = forecast_data.get("recent_predictions_sample", [])

        if ctx:
            x_ctx = [item["hour"] for item in ctx]
            y_ctx = [item["real_power_w"] for item in ctx]
            ax.plot(
                x_ctx,
                y_ctx,
                label="Contexto Pré-Corte (Real)",
                color="#A78BFA",
                linewidth=2.0,
                alpha=0.85,
            )

        x_post = [item["hour"] for item in post]
        ax.plot(
            x_post,
            [item["real_power_w"] for item in post],
            label="Consumo Real Medido (W)",
            color="#8B5CF6",
            linewidth=2.5,
        )
        style_map = {
            "Hist_Gradient_Boosting": ("pred_hgb_w", "HistGradientBoosting", "#0284C7", "-"),
            "Random_Forest": ("pred_rf_w", "Random Forest", "#059669", "--"),
            "Ridge_Linear": ("pred_ridge_w", "Ridge Linear", "#EA580C", ":"),
        }
        bench = forecast_data.get("models_benchmarking", {})
        ranked = rank_benchmarking_models(bench) if bench else [(k, {}) for k in style_map]
        for idx, (m_key, _) in enumerate(ranked):
            field, short_name, color, lstyle = style_map[m_key]
            rank_tag = "1º Campeão" if idx == 0 else f"{idx + 1}º"
            lw = 2.2 if idx == 0 else 1.8
            ax.plot(
                x_post,
                [item[field] for item in post],
                label=f"[{rank_tag}] {short_name} (W)",
                color=color,
                linestyle=lstyle,
                linewidth=lw,
            )

        ax.axvline(x=0.5, color="#EF4444", linestyle="--", linewidth=1.6, label="Ponto de Corte")
        sc_label = forecast_data.get("scenario_label", "Zenodo 2025")
        ax.set_title(
            f"{sc_label} — Previsão 1h com Ponto de Corte",
            fontsize=13,
            fontweight="bold",
        )
        ax.set_xlabel("Tempo Relativo ao Ponto de Corte (horas)", fontsize=11)
        ax.set_ylabel("Potência Ativa Consumida (W)", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.45)
        ax.legend(loc="upper right", framealpha=0.95)
        fig.tight_layout()

        fig_path = os.path.join(self.results_dir, "zenodo_forecast.png")
        fig.savefig(fig_path, dpi=300, bbox_inches="tight")
