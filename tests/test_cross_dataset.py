"""Testes cross-dataset (v1, v2, v4), Ponto de Corte, isolamento por cenário e compactação."""

import os
from copy import deepcopy
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from src.core.forecasting import (
    resolve_effective_feature_config,
    resolve_warmup_length,
)
from src.core.parameter_schema import get_default_all_configs
from src.pipelines.cycle_manager import CycleManager
from src.pipelines.dataset_loader import clear_dataset_caches, load_hourly_series, load_v4_days
from src.ui.charts import MODEL_UI_META, build_zenodo_chart
from src.utils.json_io import load_json


def _write_5min_excel(path: str, hours: int, temp_col_name: str, base_power: float) -> None:
    n_samples = hours * 12
    rng = np.random.default_rng(42)
    times = [
        (
            datetime(1900, 1, 1, (i * 5 // 60) % 24, (i * 5) % 60)
            if i < 24
            else f"{(i * 5 // 60) % 24:02d}:{(i * 5) % 60:02d}:00"
        )
        for i in range(n_samples)
    ]
    phase = np.linspace(0, max(2.0, hours / 12.0) * np.pi, n_samples)
    df = pd.DataFrame(
        {
            "time": times,
            "power (W)": base_power + 350.0 * np.sin(phase) + rng.normal(0, 35, n_samples),
            "voltage (V)": np.full(n_samples, 231.0),
            "amperage (A)": np.full(n_samples, 6.2),
            "generation (w)": np.maximum(0.0, 900.0 * np.sin(phase)),
            temp_col_name: 15.0 + 4.0 * np.cos(phase),
        }
    )
    df.to_excel(path, index=False)


def _write_v4_day_files(data_dir: str, day_idx: int, base_power: float) -> None:
    times = [f"{h:02d}:00:00" for h in list(range(1, 24)) + [0]]
    rng = np.random.default_rng(100 + day_idx)
    temps = 10.0 + 3.0 * np.sin(np.linspace(0, 2 * np.pi, 24))
    powers = base_power + 400.0 * np.sin(np.linspace(0, 2 * np.pi, 24)) + rng.normal(0, 25, 24)
    pd.DataFrame({"time": times, "temperature (ºC)": temps}).to_excel(
        os.path.join(data_dir, f"data_v4.{day_idx}.1_weather_forecast_day_{day_idx}.xlsx"),
        index=False,
    )
    pd.DataFrame({"time": times, "power (W)": powers}).to_excel(
        os.path.join(data_dir, f"data_v4.{day_idx}.2_real_consumption_day_{day_idx}.xlsx"),
        index=False,
    )


@pytest.fixture
def full_cross_dataset_env(tmp_path):
    """Cria workspace temporário contendo v1.0 (ºC), v2.0 (˚C) e v4 (Dias 1–3)."""
    data_dir = tmp_path / "data" / "zenodo"
    db_dir = tmp_path / "data" / "db"
    results_dir = tmp_path / "results"
    data_dir.mkdir(parents=True)
    db_dir.mkdir(parents=True)
    results_dir.mkdir(parents=True)

    _write_5min_excel(
        str(data_dir / "data_v1.0.xlsx"),
        hours=240,
        temp_col_name="temperature (ºC)",
        base_power=1800.0,
    )
    _write_5min_excel(
        str(data_dir / "data_v2.0.xlsx"),
        hours=260,
        temp_col_name="temperature (˚C)",
        base_power=2050.0,
    )
    for d in (1, 2, 3):
        _write_v4_day_files(str(data_dir), day_idx=d, base_power=2400.0)

    return str(tmp_path)


def test_dataset_loaders_and_v4_constraints(full_cross_dataset_env):
    """Valida leitura de v2.0 (˚C unicode), v4 (72h) e restrição causal <= 24h."""
    data_dir = os.path.join(full_cross_dataset_env, "data", "zenodo")
    hourly_v2, col_v2, _ = load_hourly_series(os.path.join(data_dir, "data_v2.0.xlsx"), "v2")
    assert col_v2["temp"] == "temperature (˚c)"
    assert len(hourly_v2) == 260
    assert hourly_v2["hour_of_day"].iloc[:24].tolist() == [float(h) for h in range(24)]

    hourly_v4, col_v4, n_v4 = load_v4_days(data_dir, days=(1, 2, 3))
    assert n_v4 == 72
    assert col_v4["gen"] is None
    assert "v4 Dia 1" in hourly_v4["timestamp_label"].iloc[0]

    eff = resolve_effective_feature_config(
        "v1_v2_to_v4",
        {
            "power_lags": [1, 24, 168],
            "rolling_mean_windows": [6, 48],
            "rolling_std_windows": [24, 168],
            "use_generation": True,
            "use_electrical_lags": True,
        },
    )
    assert eff["power_lags"] == [1, 24]
    assert eff["rolling_mean_windows"] == [6]
    assert eff["rolling_std_windows"] == [24]
    assert eff["use_generation"] is False
    assert eff["use_electrical_lags"] is False
    assert resolve_warmup_length(960, 72) == 168


def test_cross_dataset_scenarios_cutoff_charts_and_compact(full_cross_dataset_env):
    """Valida execução dos 3 cenários, active_run_id, isolamento e Limpar Só Campeão."""
    manager = CycleManager(full_cross_dataset_env)

    # Rodada 1: v1_internal_split (config ruim proposital para perder no ranking)
    cfg_bad = get_default_all_configs()
    for key in cfg_bad:
        cfg_bad[key]["features"]["power_lags"] = [168]
        cfg_bad[key]["features"]["rolling_mean_windows"] = []
        cfg_bad[key]["features"]["rolling_std_windows"] = []
        cfg_bad[key]["features"]["use_temperature"] = False
    res_1 = manager.run_all(model_configs=cfg_bad)
    assert res_1["forecast"]["active_run_id"] == "run_0001"

    # Rodada 2: v1_internal_split (config completa boa — Campeã)
    cfg_good = get_default_all_configs()
    res_2 = manager.run_all(model_configs=cfg_good)
    assert res_2["forecast"]["active_run_id"] == "run_0002"
    assert len(res_2["forecast"]["context_sample"]) > 0
    assert res_2["forecast"]["context_sample"][-1]["hour"] == 0
    assert res_2["forecast"]["recent_predictions_sample"][0]["hour"] == 1

    # Rodada 3: v1_to_v2
    cfg_v2 = deepcopy(cfg_good)
    for key in cfg_v2:
        cfg_v2[key]["split"]["evaluation_scenario"] = "v1_to_v2"
    res_3 = manager.run_all(model_configs=cfg_v2)
    assert res_3["forecast"]["evaluation_scenario"] == "v1_to_v2"
    assert res_3["forecast"]["active_run_id"] == "run_0003"

    # Rodada 4: v1_v2_to_v4
    cfg_v4 = deepcopy(cfg_good)
    for key in cfg_v4:
        cfg_v4[key]["split"]["evaluation_scenario"] = "v1_v2_to_v4"
    res_4 = manager.run_all(model_configs=cfg_v4)
    f4 = res_4["forecast"]
    assert f4["evaluation_scenario"] == "v1_v2_to_v4"
    assert f4["has_generation"] is False
    assert f4["context_hours"] == 24
    assert f4["horizon_hours"] == 48
    assert f4["active_run_id"] == "run_0004"

    # Gráficos Plotly unificados em v1 (Potência+Temp+Solar) e v4 (Potência+Temp)
    fig_v1 = build_zenodo_chart(res_2["forecast"])
    fig_v4 = build_zenodo_chart(f4)
    assert len(fig_v1.data) == 9
    assert len(fig_v4.data) == 7
    winner_v1 = MODEL_UI_META[res_2["forecast"]["best_model_key"]]["short"]
    assert f"🏆 1º {winner_v1}" in str(fig_v1.data[2].name)

    # Campeão de v1_internal_split deve ser run_0002, nunca misturado com v2 ou v4
    champ_v1 = manager.db.select_champion_run(
        "Hist_Gradient_Boosting",
        evaluation_scenario="v1_internal_split",
    )
    assert champ_v1 is not None
    assert champ_v1["evaluation_scenario"] == "v1_internal_split"

    # Compactar histórico deixando somente o Campeão geral (renumerado para run_0001)
    compact = manager.compact_to_champion()
    assert compact["summary"]["run_id"] == "run_0001"
    runs_after = manager.db.load_experiment_runs()
    assert len(runs_after) == 1
    assert runs_after[0]["run_id"] == "run_0001"

    snap = load_json(
        os.path.join(full_cross_dataset_env, "data", "db", "zenodo_forecast_results.json")
    )
    assert snap["active_run_id"] == "run_0001"


def test_hourly_cache_roundtrip_and_invalidation(tmp_path):
    """Garante paridade total do cache CSV/meta e invalidação via SHA-256 ao alterar o .xlsx."""
    xlsx_path = tmp_path / "data_v1.0.xlsx"
    _write_5min_excel(str(xlsx_path), hours=24, temp_col_name="temperature (ºC)", base_power=1200.0)

    clear_dataset_caches()
    df_xlsx, map_xlsx, count_xlsx = load_hourly_series(str(xlsx_path), dataset_tag="v1")
    cache_dir = tmp_path / "_hourly_cache"
    assert (cache_dir / "data_v1.0__v1.csv").exists()
    assert (cache_dir / "data_v1.0__v1.meta.json").exists()

    clear_dataset_caches()
    df_csv, map_csv, count_csv = load_hourly_series(str(xlsx_path), dataset_tag="v1")
    pd.testing.assert_frame_equal(df_xlsx, df_csv, rtol=1e-12, atol=1e-12)
    assert map_csv == map_xlsx
    assert count_csv == count_xlsx

    # Alterar conteúdo do .xlsx deve invalidar o cache SHA-256 automaticamente
    _write_5min_excel(str(xlsx_path), hours=24, temp_col_name="temperature (ºC)", base_power=2500.0)
    clear_dataset_caches()
    df_updated, _, _ = load_hourly_series(str(xlsx_path), dataset_tag="v1")
    assert float(df_updated["power (w)"].mean()) > float(df_csv["power (w)"].mean()) + 900.0


def test_pipeline_optional_figure_and_memory_replay(full_cross_dataset_env):
    """Modo UI (export_figure=False) evita PNG 300 DPI mas preserva resultados e export CLI."""
    manager = CycleManager(full_cross_dataset_env)
    fig_path = os.path.join(full_cross_dataset_env, "results", "zenodo_forecast.png")
    if os.path.exists(fig_path):
        os.remove(fig_path)

    cfg = get_default_all_configs()
    res_fast = manager.run_all(model_configs=cfg, export_figure=False)
    assert not os.path.exists(fig_path)

    res_replay = manager.run_all(model_configs=cfg, export_figure=False)
    assert (
        res_replay["forecast"]["models_benchmarking"]["Hist_Gradient_Boosting"]["metrics"]["rmse"]
        == res_fast["forecast"]["models_benchmarking"]["Hist_Gradient_Boosting"]["metrics"]["rmse"]
    )

    manager.run_all(model_configs=cfg, export_figure=True)
    assert os.path.exists(fig_path)
