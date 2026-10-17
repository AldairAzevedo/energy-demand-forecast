"""Testes de integração end-to-end para os 7 ciclos de dados do sistema."""

import os

import pytest

from src.pipelines.cycle_manager import CycleManager
from src.utils.json_io import load_json


@pytest.fixture
def base_project_dir():
    """Retorna o diretório base do projeto work_1."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_cycle_manager_integrity_check(base_project_dir):
    """Verifica que todos os 7 arquivos de ciclos existem e possuem formato válido."""
    manager = CycleManager(base_project_dir)
    status = manager.check_integrity()

    assert len(status) == 7
    for filename, is_valid in status.items():
        assert is_valid, f"O arquivo de ciclo {filename} falhou na validação de integridade."


def test_cycle_02_contains_all_models_and_losses(base_project_dir):
    """Valida que o Ciclo 02 possui os 4 modelos sob ambas as funções de perda."""
    path = os.path.join(base_project_dir, "data", "cycles", "cycle_02_cmu_q5_fitted_models.json")
    data = load_json(path)

    assert "models" in data
    assert "L2" in data["models"]
    assert "L1" in data["models"]

    expected_models = ["Linear", "Polinomial_d5", "RBF", "Kernel_Gaussiano"]
    for loss in ["L2", "L1"]:
        for m in expected_models:
            assert m in data["models"][loss]
            metrics = data["models"][loss][m]["metrics"]
            assert "rmse" in metrics
            assert "mae" in metrics
            assert "r2" in metrics


def test_cycle_06_proves_mse_reduction(base_project_dir):
    """Verifica se a engenharia multivariada comprova a redução do erro MSE."""
    path = os.path.join(
        base_project_dir, "data", "cycles", "cycle_06_cmu_q6_multivariate_comparison.json"
    )
    data = load_json(path)

    comparison = data["comparison"]
    assert comparison["mse_reduction_percentage"] > 0.0
    assert comparison["mse_multivariate"] < comparison["mse_univariate"]


def test_cycle_07_zenodo_solar_impact(base_project_dir):
    """Valida as métricas do benchmark Zenodo e a cobertura de energia solar fotovoltaica."""
    path = os.path.join(base_project_dir, "data", "cycles", "cycle_07_zenodo_smart_building.json")
    data = load_json(path)

    solar_impact = data["solar_energy_impact"]
    assert solar_impact["solar_coverage_ratio_pct"] > 0.0
    assert "models_benchmarking" in data
