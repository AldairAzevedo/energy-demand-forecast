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
            "power (W)": 1500.0
            + 300.0 * np.sin(np.linspace(0, 4 * np.pi, n_samples))
            + np.random.normal(0, 50, n_samples),
            "voltage (V)": np.full(n_samples, 230.0),
            "amperage (A)": np.full(n_samples, 6.5),
            "generation (w)": np.maximum(0, 1000.0 * np.sin(np.linspace(0, 4 * np.pi, n_samples))),
            "temperature (ºC)": 25.0 + 5.0 * np.cos(np.linspace(0, 4 * np.pi, n_samples)),
        }
    )
    excel_path = data_dir / "data_v1.0.xlsx"
    df.to_excel(excel_path, index=False)

    return str(data_dir), str(db_dir), str(results_dir)


def test_zenodo_pipeline_run(mock_zenodo_env):
    """Verifica a execução completa do ZenodoPipeline e geração de métricas multi-critério."""
    data_dir, db_dir, results_dir = mock_zenodo_env
    pipeline = ZenodoPipeline(data_dir, db_dir, results_dir)

    result = pipeline.run()

    assert result["target_variable"] == "power (W)"
    assert "models_benchmarking" in result
    assert "Ridge_Linear" in result["models_benchmarking"]
    assert "Random_Forest" in result["models_benchmarking"]
    assert "Hist_Gradient_Boosting" in result["models_benchmarking"]

    metrics_hgb = result["models_benchmarking"]["Hist_Gradient_Boosting"]["metrics"]
    assert metrics_hgb["rmse"] > 0.0
    assert metrics_hgb["mae"] > 0.0
    assert "train_time_ms" in metrics_hgb
    assert "inference_time_ms" in metrics_hgb

    json_path = os.path.join(db_dir, "zenodo_forecast_results.json")
    assert os.path.exists(json_path)

    fig_path = os.path.join(results_dir, "zenodo_forecast.png")
    assert os.path.exists(fig_path)
