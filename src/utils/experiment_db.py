"""Banco de dados JSON estruturado para configurações, experimentos e campeões multi-critério."""

import os
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.core.diagnostics import (
    SELECTION_CRITERIA,
    compute_multi_criteria_score,
    criterion_rank_key,
)
from src.core.forecasting import EVALUATION_SCENARIOS, sanitize_scenario
from src.core.parameter_schema import (
    MODEL_DISPLAY_NAMES,
    MODEL_KEYS,
    get_default_all_configs,
    get_default_model_config,
    sanitize_model_config,
)
from src.utils.json_io import load_json, save_json

SCHEMA_VERSION = "1.2.0"
MAX_HISTORY_RUNS = 200
DEFAULT_CRITERION = "multi_criteria"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _run_scenario(run: Dict[str, Any]) -> str:
    return sanitize_scenario(run.get("evaluation_scenario"))


class ExperimentDatabase:
    """Persistência atômica em JSON (Config Ativa, Campeões por Cenário e Histórico)."""

    def __init__(self, db_dir: str) -> None:
        self.db_dir = db_dir
        self.active_config_path = os.path.join(db_dir, "active_config.json")
        self.best_registry_path = os.path.join(db_dir, "best_models_registry.json")
        self.runs_history_path = os.path.join(db_dir, "experiment_runs.json")
        self._ensure_initialized()

    def _ensure_initialized(self) -> None:
        os.makedirs(self.db_dir, exist_ok=True)
        if not os.path.exists(self.active_config_path):
            save_json(
                {
                    "schema_version": SCHEMA_VERSION,
                    "updated_at": _utc_now_iso(),
                    "configs": get_default_all_configs(),
                },
                self.active_config_path,
            )
        if not os.path.exists(self.best_registry_path):
            save_json(
                {
                    "schema_version": SCHEMA_VERSION,
                    "updated_at": _utc_now_iso(),
                    "selection_criterion": DEFAULT_CRITERION,
                    "best_by_model": {},
                    "champions_by_criterion": {},
                    "champions_by_scenario": {},
                },
                self.best_registry_path,
            )
        if not os.path.exists(self.runs_history_path):
            save_json(
                {
                    "schema_version": SCHEMA_VERSION,
                    "total_runs_recorded": 0,
                    "runs": [],
                },
                self.runs_history_path,
            )

    def load_active_configs(self) -> Dict[str, Dict[str, Any]]:
        """Carrega e valida as configurações ativas de todos os modelos."""
        payload = load_json(self.active_config_path)
        raw_configs = payload.get("configs", {})
        return {key: sanitize_model_config(key, raw_configs.get(key)) for key in MODEL_KEYS}

    def save_active_configs(self, configs: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Valida e persiste as configurações ativas de todos os modelos."""
        sanitized = {key: sanitize_model_config(key, configs.get(key)) for key in MODEL_KEYS}
        save_json(
            {
                "schema_version": SCHEMA_VERSION,
                "updated_at": _utc_now_iso(),
                "configs": sanitized,
            },
            self.active_config_path,
        )
        return sanitized

    def load_best_registry(self) -> Dict[str, Any]:
        """Retorna o registro de campeões salvos por cenário, critério e modelo."""
        return load_json(self.best_registry_path)

    def load_experiment_runs(self) -> List[Dict[str, Any]]:
        """Retorna a lista de execuções históricas (mais recente primeiro)."""
        payload = load_json(self.runs_history_path)
        runs = payload.get("runs", [])
        return list(reversed(runs)) if isinstance(runs, list) else []

    def select_champion_run(
        self,
        model_key: str,
        criterion: str = DEFAULT_CRITERION,
        train_ratio: Optional[float] = None,
        evaluation_scenario: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Seleciona a melhor execução histórica de um modelo dentro do mesmo cenário."""
        runs_payload = load_json(self.runs_history_path)
        runs = runs_payload.get("runs", [])
        if not isinstance(runs, list):
            return None

        target_scenario = (
            sanitize_scenario(evaluation_scenario)
            if evaluation_scenario is not None
            else sanitize_scenario(
                self.load_active_configs()[model_key]["split"].get("evaluation_scenario")
            )
        )

        candidates = [
            {
                "run_id": r.get("run_id"),
                "timestamp": r.get("timestamp"),
                "evaluation_scenario": _run_scenario(r),
                "entry": r["models"][model_key],
            }
            for r in runs
            if isinstance(r, dict)
            and model_key in r.get("models", {})
            and _run_scenario(r) == target_scenario
        ]
        if not candidates:
            return None

        if target_scenario == "v1_internal_split" and train_ratio is not None:
            matched = [
                c
                for c in candidates
                if abs(
                    float(c["entry"].get("config", {}).get("split", {}).get("train_ratio", 0.8))
                    - train_ratio
                )
                < 1e-4
            ]
            if matched:
                candidates = matched

        return min(candidates, key=lambda c: criterion_rank_key(c["entry"], criterion))

    def reset_model_to_best(
        self,
        model_key: str,
        criterion: str = DEFAULT_CRITERION,
        match_active_split: bool = True,
        evaluation_scenario: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Restaura os parâmetros ativos de um modelo dentro do mesmo cenário de validação."""
        if model_key not in MODEL_KEYS:
            raise ValueError(f"Modelo inválido para reset: {model_key}")

        active = self.load_active_configs()
        active_split = active[model_key]["split"]
        scenario = (
            sanitize_scenario(evaluation_scenario)
            if evaluation_scenario is not None
            else sanitize_scenario(active_split.get("evaluation_scenario"))
        )
        target_ratio = (
            float(active_split["train_ratio"])
            if match_active_split and scenario == "v1_internal_split"
            else None
        )
        winner = self.select_champion_run(
            model_key,
            criterion=criterion,
            train_ratio=target_ratio,
            evaluation_scenario=scenario,
        )

        if winner and isinstance(winner["entry"].get("config"), dict):
            restored_cfg = sanitize_model_config(model_key, deepcopy(winner["entry"]["config"]))
            restored_cfg["split"]["evaluation_scenario"] = scenario
            run_id = str(winner.get("run_id", "-"))
            source = f"{criterion} ({run_id})"
        else:
            restored_cfg = get_default_model_config(model_key)
            restored_cfg["split"]["evaluation_scenario"] = scenario
            run_id = "-"
            source = "factory_baseline"

        active[model_key] = restored_cfg
        self.save_active_configs(active)
        return {
            "model_key": model_key,
            "criterion": criterion,
            "evaluation_scenario": scenario,
            "run_id": run_id,
            "source": source,
            "config": restored_cfg,
        }

    def reset_all_to_best(
        self,
        criterion: str = DEFAULT_CRITERION,
        match_active_split: bool = True,
        evaluation_scenario: Optional[str] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """Restaura todos os modelos para seus respectivos campeões do cenário ativo."""
        for key in MODEL_KEYS:
            self.reset_model_to_best(
                key,
                criterion=criterion,
                match_active_split=match_active_split,
                evaluation_scenario=evaluation_scenario,
            )
        return self.load_active_configs()

    def restore_run_config(
        self,
        run_id: str,
        model_key: Optional[str] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """Restaura parâmetros exatos (e cenário) de uma execução específica (`run_XXXX`)."""
        runs_payload = load_json(self.runs_history_path)
        target_run = next(
            (r for r in runs_payload.get("runs", []) if r.get("run_id") == run_id),
            None,
        )
        if target_run is None:
            raise ValueError(f"Execução '{run_id}' não encontrada no histórico.")

        active = self.load_active_configs()
        models_map = target_run.get("models", {})
        run_scenario = _run_scenario(target_run)
        keys_to_restore = [model_key] if model_key in MODEL_KEYS else list(MODEL_KEYS)
        for key in keys_to_restore:
            cfg = models_map.get(key, {}).get("config")
            if isinstance(cfg, dict):
                restored = sanitize_model_config(key, deepcopy(cfg))
                restored["split"]["evaluation_scenario"] = run_scenario
                active[key] = restored
        if model_key is None:
            for key in MODEL_KEYS:
                active[key]["split"]["evaluation_scenario"] = run_scenario
        return self.save_active_configs(active)

    def reset_to_factory_defaults(
        self, evaluation_scenario: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Restaura os 3 modelos para os padrões iniciais preservando o cenário se pedido."""
        defaults = get_default_all_configs()
        if evaluation_scenario is not None:
            sc = sanitize_scenario(evaluation_scenario)
            for key in MODEL_KEYS:
                defaults[key]["split"]["evaluation_scenario"] = sc
        return self.save_active_configs(defaults)

    @staticmethod
    def _prev_model_rmse(
        runs: List[Dict[str, Any]], model_key: str, scenario: str
    ) -> Optional[float]:
        for prev in reversed(runs):
            if _run_scenario(prev) != scenario:
                continue
            prev_rmse = prev.get("models", {}).get(model_key, {}).get("metrics", {}).get("rmse")
            return float(prev_rmse) if prev_rmse is not None else None
        return None

    @staticmethod
    def _build_champion_record(
        model_key: str,
        entry: Dict[str, Any],
        run_id: str,
        timestamp: str,
        evaluation_scenario: str,
    ) -> Dict[str, Any]:
        metrics = deepcopy(entry.get("metrics", {}))
        features_used = list(entry.get("features_used", []))
        return {
            "model_key": model_key,
            "display_name": MODEL_DISPLAY_NAMES[model_key],
            "evaluation_scenario": evaluation_scenario,
            "best_rmse": float(metrics.get("rmse", 0.0)),
            "multi_criteria_score": float(metrics.get("multi_criteria_score", 0.0)),
            "metrics": metrics,
            "train_metrics": deepcopy(entry.get("train_metrics", {})),
            "learning_diagnosis": deepcopy(entry.get("learning_diagnosis", {})),
            "error_diagnostics": deepcopy(entry.get("error_diagnostics", {})),
            "config": sanitize_model_config(model_key, entry.get("config")),
            "features_used": features_used,
            "num_features": len(features_used),
            "run_id": run_id,
            "achieved_at": timestamp,
        }

    def _compute_champions_for_subset(
        self, runs: List[Dict[str, Any]], scenario: str
    ) -> Dict[str, Dict[str, Any]]:
        champions_by_criterion: Dict[str, Dict[str, Any]] = {}
        for criterion in SELECTION_CRITERIA:
            per_model: Dict[str, Any] = {}
            for key in MODEL_KEYS:
                cands = [r for r in runs if key in r.get("models", {})]
                if not cands:
                    continue
                best_run = min(cands, key=lambda r: criterion_rank_key(r["models"][key], criterion))
                per_model[key] = self._build_champion_record(
                    key,
                    best_run["models"][key],
                    str(best_run.get("run_id", "-")),
                    str(best_run.get("timestamp", "")),
                    scenario,
                )
            champions_by_criterion[criterion] = per_model
        return champions_by_criterion

    def _compute_all_scenario_champions(
        self, runs: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Dict[str, Any]]]:
        by_scenario: Dict[str, Dict[str, Dict[str, Any]]] = {}
        for scenario in EVALUATION_SCENARIOS:
            subset = [r for r in runs if _run_scenario(r) == scenario]
            if subset:
                by_scenario[scenario] = self._compute_champions_for_subset(subset, scenario)
        return by_scenario

    def _save_registry(
        self,
        timestamp: str,
        active_scenario: str,
        champions_by_scenario: Dict[str, Dict[str, Dict[str, Any]]],
    ) -> Dict[str, Any]:
        active_crit_map = champions_by_scenario.get(active_scenario, {})
        best_by_model = active_crit_map.get(DEFAULT_CRITERION, {})
        save_json(
            {
                "schema_version": SCHEMA_VERSION,
                "updated_at": timestamp,
                "active_scenario": active_scenario,
                "selection_criterion": DEFAULT_CRITERION,
                "best_by_model": best_by_model,
                "champions_by_criterion": active_crit_map,
                "champions_by_scenario": champions_by_scenario,
            },
            self.best_registry_path,
        )
        return best_by_model

    def record_run(
        self,
        forecast_data: Dict[str, Any],
        configs_used: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Grava uma execução no histórico e atualiza os campeões por cenário."""
        runs_payload = load_json(self.runs_history_path)
        runs: List[Dict[str, Any]] = list(runs_payload.get("runs", []))
        total_recorded = int(runs_payload.get("total_runs_recorded", len(runs))) + 1
        run_id = f"run_{total_recorded:04d}"
        timestamp = _utc_now_iso()
        scenario = sanitize_scenario(forecast_data.get("evaluation_scenario"))

        registry = self.load_best_registry()
        prev_registry = (
            registry.get("champions_by_scenario", {}).get(scenario, {}).get(DEFAULT_CRITERION, {})
        )
        if not prev_registry and registry.get("active_scenario", scenario) == scenario:
            prev_registry = registry.get("best_by_model", {})

        benchmarking = forecast_data.get("models_benchmarking", {})
        ref_power = float(forecast_data.get("mean_test_power_w", 2000.0) or 2000.0)

        new_records: List[str] = []
        models_summary: Dict[str, Any] = {}

        for key in MODEL_KEYS:
            if key not in benchmarking:
                continue
            bench_entry = benchmarking[key]
            cfg = sanitize_model_config(key, configs_used.get(key))
            cfg["split"]["evaluation_scenario"] = scenario
            metrics = deepcopy(bench_entry.get("metrics", {}))
            train_metrics = deepcopy(bench_entry.get("train_metrics", {}))
            if "multi_criteria_score" not in metrics:
                metrics["multi_criteria_score"] = compute_multi_criteria_score(
                    metrics, train_metrics, mean_ref_power_w=ref_power
                )

            prev_rmse = self._prev_model_rmse(runs, key, scenario)
            curr_rmse = float(metrics.get("rmse", 0.0))
            delta_prev = round(curr_rmse - prev_rmse, 2) if prev_rmse is not None else None

            candidate_entry = {
                "metrics": metrics,
                "train_metrics": train_metrics,
                "learning_diagnosis": deepcopy(bench_entry.get("learning_diagnosis", {})),
                "error_diagnostics": deepcopy(bench_entry.get("error_diagnostics", {})),
                "delta_vs_prev_rmse_w": delta_prev,
                "config": cfg,
                "features_used": list(bench_entry.get("features_used", [])),
                "num_features": len(bench_entry.get("features_used", [])),
            }

            prev_best = prev_registry.get(key)
            is_record = prev_best is None or (
                criterion_rank_key(candidate_entry, DEFAULT_CRITERION)
                < criterion_rank_key(prev_best, DEFAULT_CRITERION)
            )
            if is_record:
                new_records.append(key)
            candidate_entry["new_record"] = is_record
            models_summary[key] = candidate_entry

        runs.append(
            {
                "run_id": run_id,
                "timestamp": timestamp,
                "evaluation_scenario": scenario,
                "total_hourly_samples": forecast_data.get("total_hourly_samples", 0),
                "best_model_key": forecast_data.get("best_model_key"),
                "models": models_summary,
            }
        )
        if len(runs) > MAX_HISTORY_RUNS:
            runs = runs[-MAX_HISTORY_RUNS:]

        champions_by_scenario = self._compute_all_scenario_champions(runs)
        best_by_model = self._save_registry(timestamp, scenario, champions_by_scenario)

        save_json(
            {"schema_version": SCHEMA_VERSION, "total_runs_recorded": total_recorded, "runs": runs},
            self.runs_history_path,
        )
        return {
            "run_id": run_id,
            "evaluation_scenario": scenario,
            "new_records": new_records,
            "best_by_model": best_by_model,
        }

    @staticmethod
    def _run_overall_rank(run: Dict[str, Any], criterion: str) -> Any:
        models_map = run.get("models", {})
        if not models_map:
            return (1, float("inf"), float("inf"))
        best_key = run.get("best_model_key")
        if best_key in models_map:
            return criterion_rank_key(models_map[best_key], criterion)
        return min(criterion_rank_key(entry, criterion) for entry in models_map.values())

    def compact_history_to_champion(self, criterion: str = DEFAULT_CRITERION) -> Dict[str, Any]:
        """Limpa o histórico deixando somente o Campeão geral renumerado para `run_0001`."""
        runs_payload = load_json(self.runs_history_path)
        runs: List[Dict[str, Any]] = list(runs_payload.get("runs", []))
        if not runs:
            return {"empty": True, "run_id": "-", "kept_original_run_id": None}

        winner_run = deepcopy(min(runs, key=lambda r: self._run_overall_rank(r, criterion)))
        original_run_id = str(winner_run.get("run_id", "run_0001"))
        scenario = _run_scenario(winner_run)

        winner_run["run_id"] = "run_0001"
        winner_run["evaluation_scenario"] = scenario
        champion_configs = get_default_all_configs()
        for key in MODEL_KEYS:
            if key in winner_run.get("models", {}):
                winner_run["models"][key]["delta_vs_prev_rmse_w"] = None
                winner_run["models"][key]["new_record"] = True
                cfg = winner_run["models"][key].get("config")
                if isinstance(cfg, dict):
                    sanitized = sanitize_model_config(key, deepcopy(cfg))
                    sanitized["split"]["evaluation_scenario"] = scenario
                    winner_run["models"][key]["config"] = sanitized
                    champion_configs[key] = sanitized

        save_json(
            {"schema_version": SCHEMA_VERSION, "total_runs_recorded": 1, "runs": [winner_run]},
            self.runs_history_path,
        )
        champions_by_scenario = self._compute_all_scenario_champions([winner_run])
        self._save_registry(_utc_now_iso(), scenario, champions_by_scenario)
        self.save_active_configs(champion_configs)

        snapshot_path = os.path.join(self.db_dir, "zenodo_forecast_results.json")
        if os.path.exists(snapshot_path):
            snap = load_json(snapshot_path)
            if isinstance(snap, dict):
                snap["active_run_id"] = "run_0001"
                save_json(snap, snapshot_path)

        return {
            "empty": False,
            "run_id": "run_0001",
            "kept_original_run_id": original_run_id,
            "evaluation_scenario": scenario,
            "configs": champion_configs,
        }
