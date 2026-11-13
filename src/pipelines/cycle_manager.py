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
        """Executa o pipeline completo de previsão de carga e energia solar (Zenodo)."""
        log = callback if callback is not None else print

        log("[CycleManager] Iniciando processamento do desafio Zenodo Smart Building...")
        log(
            " -> Executando Pipeline Zenodo "
            "(Ingestão, Treinamento Ridge & Random Forest, Curva do Pato)..."
        )
        self.zenodo_pipe.run_cycle_07()
        log("[CycleManager] ✅ Pipeline Zenodo gerado e validado com sucesso!")

    def check_integrity(self) -> Dict[str, bool]:
        """Verifica a integridade do arquivo JSON gerado pelo pipeline Zenodo."""
        cycle_files = [
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
    """Ponto de entrada de linha de comando para o gerenciador de pipeline."""
    parser = argparse.ArgumentParser(description="CycleManager: Orquestrador do Pipeline Zenodo")
    parser.add_argument("--run-all", action="store_true", help="Executa o pipeline Zenodo")
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
