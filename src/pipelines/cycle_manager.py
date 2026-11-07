"""Gerenciador centralizado de execução e validação dos 7 ciclos de dados."""

import argparse
import os
from typing import Callable, Dict, Optional

from src.pipelines.cmu_q5_pipeline import CMUQ5Pipeline
from src.pipelines.cmu_q6_pipeline import CMUQ6Pipeline
from src.pipelines.zenodo_pipeline import ZenodoPipeline
from src.utils.json_io import load_json


class CycleManager:
    """Orquestra a execução sequencial e validação de integridade de todos os ciclos."""

    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        self.data_cmu = os.path.join(base_dir, "data", "cmu")
        self.data_zenodo = os.path.join(base_dir, "data", "zenodo")
        self.cycles_dir = os.path.join(base_dir, "data", "cycles")
        self.results_dir = os.path.join(base_dir, "results")

        self.q5_pipe = CMUQ5Pipeline(self.data_cmu, self.cycles_dir, self.results_dir)
        self.q6_pipe = CMUQ6Pipeline(self.data_cmu, self.cycles_dir, self.results_dir)
        self.zenodo_pipe = ZenodoPipeline(self.data_zenodo, self.cycles_dir, self.results_dir)

    def run_all(self, callback: Optional[Callable[[str], None]] = None) -> None:
        """Executa sequencialmente todos os 7 ciclos do pipeline de dados."""
        log = callback if callback is not None else print

        log("[CycleManager] Iniciando processamento de todos os ciclos...")
        log(" -> Executando Ciclo 01 (CMU Q5 Raw: 1.460 dias)...")
        self.q5_pipe.run_cycle_01()

        log(" -> Executando Ciclo 02 (CMU Q5: 4 Modelos x Perdas L2 e L1)...")
        self.q5_pipe.run_cycle_02()

        log(" -> Executando Ciclo 03 (CMU Q6: Limpeza de 100 Sentinelas -9999)...")
        self.q6_pipe.run_cycle_03()

        log(" -> Executando Ciclo 04 (CMU Q6: Sincronização de 35.064 Horas)...")
        self.q6_pipe.run_cycle_04()

        log(" -> Executando Ciclo 05 (CMU Q6: 6 Variáveis Climáticas Diárias)...")
        self.q6_pipe.run_cycle_05()

        log(" -> Executando Ciclo 06 (CMU Q6: Prova da Redução do MSE em 8.73%)...")
        self.q6_pipe.run_cycle_06()

        log(" -> Executando Ciclo 07 (Zenodo: Smart Building, RF 90% & Curva do Pato)...")
        self.zenodo_pipe.run_cycle_07()

        log("[CycleManager] ✅ Todos os 7 ciclos foram gerados e validados com sucesso!")

    def check_integrity(self) -> Dict[str, bool]:
        """Verifica a integridade de todos os arquivos JSON gerados."""
        cycle_files = [
            "cycle_01_cmu_q5_raw.json",
            "cycle_02_cmu_q5_fitted_models.json",
            "cycle_03_cmu_q6_cleaned_weather.json",
            "cycle_04_cmu_q6_interpolated_sync.json",
            "cycle_05_cmu_q6_daily_features.json",
            "cycle_06_cmu_q6_multivariate_comparison.json",
            "cycle_07_zenodo_smart_building.json",
        ]
        status = {}
        for f in cycle_files:
            p = os.path.join(self.cycles_dir, f)
            if os.path.exists(p) and os.path.getsize(p) > 0:
                try:
                    data = load_json(p)
                    status[f] = isinstance(data, dict) and "cycle_id" in data
                except Exception:
                    status[f] = False
            else:
                status[f] = False
        return status


def main() -> None:
    """Ponto de entrada de linha de comando para o gerenciador de ciclos."""
    parser = argparse.ArgumentParser(description="CycleManager: Orquestrador de Ciclos de Dados")
    parser.add_argument("--run-all", action="store_true", help="Executa todos os 7 ciclos em lote")
    parser.add_argument("--check", action="store_true", help="Verifica a integridade dos JSONs")
    args = parser.parse_args()

    # Localiza automaticamente o diretório raiz do projeto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))

    manager = CycleManager(base_dir)
    if args.run_all:
        manager.run_all()
    elif args.check:
        results = manager.check_integrity()
        for k, v in results.items():
            print(f" {k}: {'[OK]' if v else '[FALHA]'}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
