"""Testes de integração end-to-end para o pipeline Zenodo Smart Building."""

import os

import pytest

from src.pipelines.cycle_manager import CycleManager
from src.utils.json_io import load_json


@pytest.fixture
def base_project_dir():
    """Retorna o diretório base do projeto."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_cycle_manager_integrity_check(base_project_dir):
    """Verifica que o arquivo JSON do pipeline Zenodo existe e possui formato válido."""
    manager = CycleManager(base_project_dir)
    status = manager.check_integrity()

    assert len(status) == 1
    for filename, is_valid in status.items():
        assert is_valid, f"O arquivo {filename} falhou na validação de integridade."


def test_zenodo_forecast_benchmark_structure(base_project_dir):
    """Valida as métricas multi-critério de previsão de consumo no JSON gerado."""
    path = os.path.join(base_project_dir, "data", "db", "zenodo_forecast_results.json")
    data = load_json(path)

    assert data["target_variable"] == "power (W)"
    assert data["mean_test_power_w"] > 0.0
    assert "models_benchmarking" in data
    assert "Hist_Gradient_Boosting" in data["models_benchmarking"]
