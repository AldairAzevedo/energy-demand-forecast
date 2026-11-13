"""Testes unitários para o pipeline de previsão Zenodo Smart Building."""

import os

import numpy as np
import pandas as pd
import pytest

from src.pipelines.zenodo_pipeline import ZenodoPipeline


@pytest.fixture
def mock_zenodo_env(tmp_path):
    """Cria um ambiente temporário com dados sintéticos no formato do Zenodo."""
    data_dir = tmp_path / "data" / "zenodo"
    cycles_dir = tmp_path / "data" / "cycles"
    results_dir = tmp_path / "results"
    data_dir.mkdir(parents=True)
    cycles_dir.mkdir(parents=True)
    results_dir.mkdir(parents=True)

    # 48 horas de dados (amostras a cada 5 min = 12 * 48 = 576 leituras)
    n_samples = 576
    np.random.seed(42)
    df = pd.DataFrame(
        {
            "active_power": 1500.0 + 300.0 * np.sin(np.linspace(0, 4 * np.pi, n_samples))
            + np.random.normal(0, 50, n_samples),
            "pv_generation": np.maximum(
                0, 1000.0 * np.sin(np.linspace(0, 4 * np.pi, n_samples))
            ),
            "temperature": 25.0 + 5.0 * np.cos(np.linspace(0, 4 * np.pi, n_samples)),
        }
    )
    excel_path = data_dir / "data_v1.0.xlsx"
    df.to_excel(excel_path, index=False)

    return str(data_dir), str(cycles_dir), str(results_dir)


def test_zenodo_pipeline_run(mock_zenodo_env):
    """Verifica a execução completa do ZenodoPipeline e geração de métricas."""
    data_dir, cycles_dir, results_dir = mock_zenodo_env
    pipeline = ZenodoPipeline(data_dir, cycles_dir, results_dir)

    result = pipeline.run_cycle_07()

    assert result["cycle_id"] == 7
    assert "models_benchmarking" in result
    assert "Ridge_Linear" in result["models_benchmarking"]
    assert "Random_Forest" in result["models_benchmarking"]

    metrics_rf = result["models_benchmarking"]["Random_Forest"]["metrics"]
    assert metrics_rf["rmse"] > 0.0
    assert metrics_rf["mae"] > 0.0
    assert "r2" in metrics_rf

    solar = result["solar_energy_impact"]
    assert solar["mean_consumption_w"] > 0.0
    assert "solar_coverage_ratio_pct" in solar

    json_path = os.path.join(cycles_dir, "cycle_07_zenodo_smart_building.json")
    assert os.path.exists(json_path)

    fig_path = os.path.join(results_dir, "zenodo_forecast.png")
    assert os.path.exists(fig_path)
