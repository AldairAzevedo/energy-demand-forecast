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
        assert is_valid, f"O arquivo de ciclo {filename} falhou na validação de integridade."


def test_cycle_07_zenodo_solar_impact(base_project_dir):
    """Valida as métricas do benchmark Zenodo e a cobertura de energia solar fotovoltaica."""
    path = os.path.join(base_project_dir, "data", "cycles", "cycle_07_zenodo_smart_building.json")
    data = load_json(path)

    solar_impact = data["solar_energy_impact"]
    assert solar_impact["solar_coverage_ratio_pct"] > 0.0
    assert "models_benchmarking" in data
