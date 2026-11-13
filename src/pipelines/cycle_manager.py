"""Gerenciador centralizado de execução e validação do pipeline Zenodo Smart Building."""

import argparse
import os
from typing import Callable, Dict, Optional

from src.pipelines.zenodo_pipeline import ZenodoPipeline
from src.utils.json_io import load_json


class CycleManager:
    """Orquestra a execução e validação de integridade do pipeline Zenodo."""

    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        self.data_zenodo = os.path.join(base_dir, "data", "zenodo")
        self.cycles_dir = os.path.join(base_dir, "data", "cycles")
        self.results_dir = os.path.join(base_dir, "results")

        self.zenodo_pipe = ZenodoPipeline(self.data_zenodo, self.cycles_dir, self.results_dir)

    def run_all(self, callback: Optional[Callable[[str], None]] = None) -> None:
        """Executa o pipeline completo de previsão de consumo elétrico (Zenodo 2025)."""
        log = callback if callback is not None else print

        log("[CycleManager] Iniciando processamento do desafio Zenodo 2025...")
        log(
            " -> Executando Pipeline Zenodo "
            "(Ingestão, Lags/Sazonalidade e Avaliação Multi-critério)..."
        )
        self.zenodo_pipe.run()
        log("[CycleManager] ✅ Pipeline Zenodo gerado e validado com sucesso!")

    def check_integrity(self) -> Dict[str, bool]:
        """Verifica a integridade do arquivo JSON gerado pelo pipeline Zenodo."""
        output_files = [
            "zenodo_forecast_results.json",
        ]
        status = {}
        for filename in output_files:
            path = os.path.join(self.cycles_dir, filename)
            if os.path.exists(path) and os.path.getsize(path) > 0:
                try:
                    data = load_json(path)
                    status[filename] = isinstance(data, dict) and "models_benchmarking" in data
                except Exception:
                    status[filename] = False
            else:
                status[filename] = False
        return status


def main() -> None:
    """Ponto de entrada de linha de comando para o gerenciador de pipeline."""
    parser = argparse.ArgumentParser(description="CycleManager: Orquestrador do Pipeline Zenodo")
    parser.add_argument("--run-all", action="store_true", help="Executa o pipeline Zenodo")
    parser.add_argument("--check", action="store_true", help="Verifica a integridade dos JSONs")
    args = parser.parse_args()

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
