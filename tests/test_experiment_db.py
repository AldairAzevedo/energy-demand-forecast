"""Testes unitários e de fluxo para esquema de parâmetros e banco JSON."""

from copy import deepcopy

import numpy as np
import pandas as pd

from src.core.diagnostics import (
    compute_error_diagnostics,
    compute_multi_criteria_score,
    criterion_rank_key,
    diagnose_learning_status,
)
from src.core.parameter_schema import (
    MODEL_KEYS,
    get_default_all_configs,
    get_parameter_taxonomy,
    normalize_int_list,
    sanitize_model_config,
)
from src.pipelines.cycle_manager import CycleManager
from src.pipelines.zenodo_pipeline import ZenodoPipeline
from src.utils.experiment_db import ExperimentDatabase
from src.utils.file_resilience import read_bytes_resilient


def test_parameter_taxonomy_covers_ml_and_domain():
    """Verifica que a taxonomia separa variáveis globais de ML e variáveis de domínio."""
    taxonomy = get_parameter_taxonomy()
    escopos = {item["escopo"] for item in taxonomy}
    assert any("Global de ML" in esc for esc in escopos)
    assert any("Domínio" in esc for esc in escopos)


def test_normalize_and_sanitize_guards():
    """Garante normalização segura de lags e proteção contra matriz sem atributos."""
    assert normalize_int_list("168, 1, 24, 1, -5, abc, 9999", [1, 24]) == [1, 24, 168]

    cfg = sanitize_model_config(
        "Hist_Gradient_Boosting",
        {
            "features": {
                "power_lags": [],
                "rolling_mean_windows": [],
                "rolling_std_windows": [],
                "use_cyclical_hour": False,
                "use_raw_hour": False,
                "use_temperature": False,
                "use_generation": False,
                "use_electrical_lags": False,
            },
            "split": {"train_ratio": 0.99},
            "hyperparameters": {"learning_rate": 0.0001},
        },
    )
    assert cfg["features"]["use_cyclical_hour"] is True
    assert cfg["split"]["train_ratio"] == 0.95
    assert cfg["hyperparameters"]["learning_rate"] == 0.005


def test_experiment_db_promotion_and_per_model_reset(tmp_path):
    """Valida que o banco promove o menor RMSE por modelo e reseta corretamente."""
    db = ExperimentDatabase(str(tmp_path / "db"))

    cfg_good = get_default_all_configs()
    cfg_good["Ridge_Linear"]["hyperparameters"]["alpha"] = 5.0
    cfg_good["Hist_Gradient_Boosting"]["features"]["power_lags"] = [1, 24]

    forecast_good = {
        "total_hourly_samples": 100,
        "best_model_key": "Hist_Gradient_Boosting",
        "models_benchmarking": {
            "Ridge_Linear": {
                "metrics": {"rmse": 320.0, "mae": 200.0, "r2": 0.91},
                "features_used": ["hour_sin", "hour_cos"],
            },
            "Random_Forest": {
                "metrics": {"rmse": 290.0, "mae": 150.0, "r2": 0.93},
                "features_used": ["hour_sin", "hour_cos"],
            },
            "Hist_Gradient_Boosting": {
                "metrics": {"rmse": 280.0, "mae": 145.0, "r2": 0.94},
                "features_used": ["power_lag_1", "power_lag_24"],
            },
        },
    }
    res1 = db.record_run(forecast_good, cfg_good)
    assert set(res1["new_records"]) == set(MODEL_KEYS)

    # Segunda execução: apenas Random_Forest melhora; os outros pioram
    cfg_mixed = deepcopy(cfg_good)
    cfg_mixed["Ridge_Linear"]["hyperparameters"]["alpha"] = 99.0
    cfg_mixed["Random_Forest"]["hyperparameters"]["n_estimators"] = 250
    cfg_mixed["Hist_Gradient_Boosting"]["features"]["power_lags"] = [1]

    forecast_mixed = {
        "total_hourly_samples": 100,
        "best_model_key": "Random_Forest",
        "models_benchmarking": {
            "Ridge_Linear": {
                "metrics": {"rmse": 410.0, "mae": 260.0, "r2": 0.85},
                "features_used": ["hour_sin", "hour_cos"],
            },
            "Random_Forest": {
                "metrics": {"rmse": 275.0, "mae": 140.0, "r2": 0.95},
                "features_used": ["hour_sin", "hour_cos"],
            },
            "Hist_Gradient_Boosting": {
                "metrics": {"rmse": 350.0, "mae": 190.0, "r2": 0.89},
                "features_used": ["power_lag_1"],
            },
        },
    }
    res2 = db.record_run(forecast_mixed, cfg_mixed)
    assert res2["new_records"] == ["Random_Forest"]

    db.save_active_configs(cfg_mixed)
    db.reset_model_to_best("Hist_Gradient_Boosting")
    active_after_one = db.load_active_configs()
    assert active_after_one["Hist_Gradient_Boosting"]["features"]["power_lags"] == [1, 24]
    assert active_after_one["Ridge_Linear"]["hyperparameters"]["alpha"] == 99.0

    active_after_all = db.reset_all_to_best()
    assert active_after_all["Ridge_Linear"]["hyperparameters"]["alpha"] == 5.0
    assert active_after_all["Random_Forest"]["hyperparameters"]["n_estimators"] == 250
    assert len(db.load_experiment_runs()) == 2


def test_pipeline_and_cycle_manager_with_custom_params(tmp_path):
    """Testa pipeline parametrizado e CycleManager com persistência em tmp_path."""
    data_dir = tmp_path / "data" / "zenodo"
    db_dir = tmp_path / "data" / "db"
    results_dir = tmp_path / "results"
    data_dir.mkdir(parents=True)
    db_dir.mkdir(parents=True)
    results_dir.mkdir(parents=True)

    n_samples = 576
    np.random.seed(42)
    times = [f"{(i * 5 // 60) % 24:02d}:{(i * 5) % 60:02d}:00" for i in range(n_samples)]
    df = pd.DataFrame(
        {
            "time": times,
            "power (W)": 1400.0 + 250.0 * np.sin(np.linspace(0, 4 * np.pi, n_samples)),
            "voltage (V)": np.full(n_samples, 230.0),
            "amperage (A)": np.full(n_samples, 6.0),
            "generation (w)": np.maximum(0, 900.0 * np.sin(np.linspace(0, 4 * np.pi, n_samples))),
            "temperature (ºC)": 22.0 + 4.0 * np.cos(np.linspace(0, 4 * np.pi, n_samples)),
        }
    )
    df.to_excel(data_dir / "data_v1.0.xlsx", index=False)

    cfgs = get_default_all_configs()
    cfgs["Ridge_Linear"]["features"]["power_lags"] = [1, 24]
    cfgs["Ridge_Linear"]["features"]["use_generation"] = False
    cfgs["Ridge_Linear"]["features"]["use_raw_hour"] = True

    pipe = ZenodoPipeline(str(data_dir), str(db_dir), str(results_dir))
    res = pipe.run(model_configs=cfgs)
    ridge_feats = res["models_benchmarking"]["Ridge_Linear"]["features_used"]
    assert "power_lag_1" in ridge_feats
    assert "power_lag_24" in ridge_feats
    assert "hour_raw" in ridge_feats
    assert "gen_w" not in ridge_feats

    manager = CycleManager(str(tmp_path))
    run_out = manager.run_all(model_configs=cfgs)
    assert run_out["experiment"]["run_id"] == "run_0001"
    assert (tmp_path / "data" / "db" / "best_models_registry.json").exists()


def test_read_bytes_resilient_permission_fallback(tmp_path, monkeypatch):
    """Garante leitura via cópia temporária quando o arquivo original lança PermissionError."""
    target = tmp_path / "locked.xlsx"
    target.write_bytes(b"zenodo-payload")

    real_open = open

    def blocked_open(file, mode="r", *args, **kwargs):
        if str(file) == str(target) and "r" in mode:
            raise PermissionError("Locked by Excel")
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", blocked_open)
    assert read_bytes_resilient(str(target)) == b"zenodo-payload"


def test_diagnostics_overfit_and_error_map(tmp_path):
    """Valida classificação Overfitting/Bom Ajuste e mapa de erros por turno."""
    overfit = diagnose_learning_status(
        train_r2=0.99, test_r2=0.88, train_rmse=40.0, test_rmse=310.0
    )
    assert "Overfitting" in overfit["status"]

    balanced = diagnose_learning_status(
        train_r2=0.93, test_r2=0.92, train_rmse=280.0, test_rmse=300.0
    )
    assert "Bom Ajuste" in balanced["status"]

    y_true = np.array([1000.0, 1200.0, 2000.0, 2500.0])
    y_pred = np.array([1050.0, 1180.0, 1600.0, 2510.0])
    hours = np.array([2.0, 9.0, 14.0, 20.0])
    err_diag = compute_error_diagnostics(y_true, y_pred, hours)

    assert err_diag["hit_rate_100w_pct"] == 75.0
    assert len(err_diag["period_breakdown"]) == 4
    assert err_diag["top_worst_hours"][0]["abs_error_w"] == 400.0
    assert err_diag["top_best_hours"][0]["abs_error_w"] == 10.0


def test_pipeline_and_db_persist_train_test_and_delta(tmp_path):
    """Garante que treino, teste, diagnóstico e delta entre runs vão para o banco JSON."""
    data_dir = tmp_path / "data" / "zenodo"
    db_dir = tmp_path / "data" / "db"
    results_dir = tmp_path / "results"
    data_dir.mkdir(parents=True)
    db_dir.mkdir(parents=True)
    results_dir.mkdir(parents=True)

    n_samples = 576
    np.random.seed(42)
    times = [f"{(i * 5 // 60) % 24:02d}:{(i * 5) % 60:02d}:00" for i in range(n_samples)]
    df = pd.DataFrame(
        {
            "time": times,
            "power (W)": 1500.0 + 300.0 * np.sin(np.linspace(0, 4 * np.pi, n_samples)),
            "voltage (V)": np.full(n_samples, 230.0),
            "amperage (A)": np.full(n_samples, 6.5),
            "generation (w)": np.maximum(0, 900.0 * np.sin(np.linspace(0, 4 * np.pi, n_samples))),
            "temperature (ºC)": 22.0 + 4.0 * np.cos(np.linspace(0, 4 * np.pi, n_samples)),
        }
    )
    df.to_excel(data_dir / "data_v1.0.xlsx", index=False)

    manager = CycleManager(str(tmp_path))
    manager.run_all()
    manager.run_all()

    runs = manager.db.load_experiment_runs()
    assert len(runs) == 2
    latest_hgb = runs[0]["models"]["Hist_Gradient_Boosting"]
    assert "rmse" in latest_hgb["train_metrics"]
    assert "status" in latest_hgb["learning_diagnosis"]
    assert "hit_rate_200w_pct" in latest_hgb["error_diagnostics"]
    assert latest_hgb["delta_vs_prev_rmse_w"] == 0.0


def test_multi_criteria_scoring_and_restore_by_run_id(tmp_path):
    """Valida score multi-critério, seleção por critério e restauração por run_id."""
    balanced_entry = {
        "metrics": {"rmse": 322.0, "mae": 160.0, "r2": 0.91, "runtime_ms": 200.0},
        "train_metrics": {"r2": 0.92, "rmse": 300.0},
    }
    overfit_entry = {
        "metrics": {"rmse": 320.0, "mae": 160.0, "r2": 0.91, "runtime_ms": 2000.0},
        "train_metrics": {"r2": 0.99, "rmse": 50.0},
    }

    s_bal = compute_multi_criteria_score(balanced_entry["metrics"], balanced_entry["train_metrics"])
    s_ovf = compute_multi_criteria_score(overfit_entry["metrics"], overfit_entry["train_metrics"])
    assert s_bal > s_ovf
    assert criterion_rank_key(balanced_entry) < criterion_rank_key(overfit_entry)

    db = ExperimentDatabase(str(tmp_path / "db"))
    cfgs_1 = get_default_all_configs()
    cfgs_1["Ridge_Linear"]["hyperparameters"]["alpha"] = 2.5
    f1 = {
        "total_hourly_samples": 100,
        "mean_test_power_w": 2000.0,
        "best_model_key": "Ridge_Linear",
        "models_benchmarking": {
            k: {
                "metrics": {"rmse": 322.0, "mae": 160.0, "r2": 0.91, "runtime_ms": 200.0},
                "train_metrics": {"r2": 0.92, "rmse": 300.0},
                "features_used": ["hour_sin"],
            }
            for k in MODEL_KEYS
        },
    }
    db.record_run(f1, cfgs_1)

    cfgs_2 = get_default_all_configs()
    cfgs_2["Ridge_Linear"]["hyperparameters"]["alpha"] = 99.0
    f2 = {
        "total_hourly_samples": 100,
        "mean_test_power_w": 2000.0,
        "best_model_key": "Ridge_Linear",
        "models_benchmarking": {
            k: {
                "metrics": {"rmse": 320.0, "mae": 160.0, "r2": 0.91, "runtime_ms": 2000.0},
                "train_metrics": {"r2": 0.99, "rmse": 50.0},
                "features_used": ["hour_sin"],
            }
            for k in MODEL_KEYS
        },
    }
    db.record_run(f2, cfgs_2)

    db.reset_model_to_best("Ridge_Linear")
    assert db.load_active_configs()["Ridge_Linear"]["hyperparameters"]["alpha"] == 2.5

    db.restore_run_config("run_0002", model_key="Ridge_Linear")
    assert db.load_active_configs()["Ridge_Linear"]["hyperparameters"]["alpha"] == 99.0

    db.restore_run_config("run_0001", model_key="Ridge_Linear")
    assert db.load_active_configs()["Ridge_Linear"]["hyperparameters"]["alpha"] == 2.5
