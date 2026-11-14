"""Gerenciador centralizado de execução e persistência de experimentos Zenodo."""

import argparse
import os
from typing import Any, Callable, Dict, Optional

from src.pipelines.zenodo_pipeline import ZenodoPipeline
from src.utils.experiment_db import ExperimentDatabase
from src.utils.json_io import load_json, save_json


class CycleManager:
    """Orquestra a execução, histórico e validação de integridade do pipeline Zenodo."""

    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        self.data_zenodo = os.path.join(base_dir, "data", "zenodo")
        self.results_dir = os.path.join(base_dir, "results")
        self.db_dir = os.path.join(base_dir, "data", "db")

        self.db = ExperimentDatabase(self.db_dir)
        self.zenodo_pipe = ZenodoPipeline(self.data_zenodo, self.db_dir, self.results_dir)

    def run_all(
        self,
        callback: Optional[Callable[[str], None]] = None,
        model_configs: Optional[Dict[str, Dict[str, Any]]] = None,
        export_figure: bool = True,
    ) -> Dict[str, Any]:
        """Executa o pipeline completo e registra o experimento no banco JSON."""
        log = callback if callback is not None else print

        configs = (
            self.db.save_active_configs(model_configs)
            if model_configs is not None
            else self.db.load_active_configs()
        )

        log("[CycleManager] Iniciando processamento do desafio Zenodo 2025...")
        log(" -> Construindo atributos configuráveis e avaliando modelos...")
        forecast_data = self.zenodo_pipe.run(model_configs=configs, export_figure=export_figure)

        record_summary = self.db.record_run(forecast_data, configs)
        forecast_data["active_run_id"] = record_summary["run_id"]
        save_json(forecast_data, os.path.join(self.db_dir, "zenodo_forecast_results.json"))

        log(f"[CycleManager] Experimento {record_summary['run_id']} salvo em data/db/.")
        if record_summary["new_records"]:
            recs = ", ".join(record_summary["new_records"])
            log(f"[CycleManager] 🏆 Novo campeão multi-critério registrado para: {recs}")
        log("[CycleManager] ✅ Pipeline Zenodo gerado e validado com sucesso!")
        return {"forecast": forecast_data, "experiment": record_summary}

    def compact_to_champion(
        self,
        callback: Optional[Callable[[str], None]] = None,
        export_figure: bool = True,
    ) -> Dict[str, Any]:
        """Limpa o histórico mantendo apenas o Campeão (run_0001) e sincroniza o gráfico."""
        log = callback if callback is not None else print
        summary = self.db.compact_history_to_champion()
        if summary.get("empty"):
            return summary

        log(
            f"[CycleManager] Histórico compactado para o Campeão "
            f"(origem: {summary['kept_original_run_id']} → run_0001)."
        )
        forecast_data = self.zenodo_pipe.run(
            model_configs=summary["configs"],
            export_figure=export_figure,
        )
        forecast_data["active_run_id"] = "run_0001"
        save_json(forecast_data, os.path.join(self.db_dir, "zenodo_forecast_results.json"))
        return {"summary": summary, "forecast": forecast_data}

    def check_integrity(self) -> Dict[str, bool]:
        """Verifica a integridade do arquivo JSON principal gerado pelo pipeline."""
        output_files = [
            "zenodo_forecast_results.json",
        ]
        status: Dict[str, bool] = {}
        for filename in output_files:
            path = os.path.join(self.db_dir, filename)
            if os.path.exists(path) and os.path.getsize(path) > 0:
                try:
                    data = load_json(path)
                    status[filename] = isinstance(data, dict) and "models_benchmarking" in data
                except (OSError, ValueError):
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
