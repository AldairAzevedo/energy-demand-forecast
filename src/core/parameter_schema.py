"""Esquema de domínio, taxonomia e validação de parâmetros dos modelos de previsão."""

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

from src.core.forecasting import DEFAULT_SCENARIO, sanitize_scenario

MODEL_KEYS: Tuple[str, ...] = (
    "Ridge_Linear",
    "Random_Forest",
    "Hist_Gradient_Boosting",
)

MODEL_DISPLAY_NAMES: Dict[str, str] = {
    "Ridge_Linear": "Ridge Linear (Baseline)",
    "Random_Forest": "Random Forest (Árvores)",
    "Hist_Gradient_Boosting": "HistGradientBoosting (Tabular)",
}

DEFAULT_HYPERPARAMETERS: Dict[str, Dict[str, Any]] = {
    "Ridge_Linear": {
        "alpha": 1.0,
    },
    "Random_Forest": {
        "n_estimators": 100,
        "max_depth": 16,
        "min_samples_leaf": 1,
    },
    "Hist_Gradient_Boosting": {
        "max_iter": 200,
        "learning_rate": 0.05,
        "max_depth": 0,
        "l2_regularization": 0.0,
    },
}

DEFAULT_FEATURE_PARAMS: Dict[str, Any] = {
    "power_lags": [1, 2, 3, 24, 48, 168],
    "rolling_mean_windows": [6, 24],
    "rolling_std_windows": [24],
    "use_cyclical_hour": True,
    "use_raw_hour": False,
    "use_temperature": True,
    "use_generation": True,
    "use_electrical_lags": True,
}

DEFAULT_SPLIT_PARAMS: Dict[str, Any] = {
    "evaluation_scenario": DEFAULT_SCENARIO,
    "train_ratio": 0.80,
    "random_state": 42,
    "context_hours": 72,
    "horizon_hours": 168,
}


def get_parameter_taxonomy() -> List[Dict[str, str]]:
    """Retorna a classificação científica entre Hiperparâmetros de ML e Covariáveis."""
    return [
        {
            "variavel": "power_lags (t-k horas)",
            "escopo": "Global de ML (Hiperparâmetro · Memória)",
            "mutabilidade": "Hiperparâmetro Configurável",
            "origem": "Derivada de power (W) passado",
            "descricao": "Memória autoregressiva (ex.: 1h, 24h, 168h atrás).",
        },
        {
            "variavel": "rolling_mean_windows",
            "escopo": "Global de ML (Hiperparâmetro · Memória)",
            "mutabilidade": "Hiperparâmetro Configurável",
            "origem": "Derivada de power (W) passado",
            "descricao": "Média móvel das últimas N horas para capturar patamar.",
        },
        {
            "variavel": "rolling_std_windows",
            "escopo": "Global de ML (Hiperparâmetro · Memória)",
            "mutabilidade": "Hiperparâmetro Configurável",
            "origem": "Derivada de power (W) passado",
            "descricao": "Desvio padrão móvel para medir volatilidade recente.",
        },
        {
            "variavel": "hour_sin / hour_cos",
            "escopo": "Global de ML (Hiperparâmetro · Eng. Cíclica)",
            "mutabilidade": "Hiperparâmetro (Ativar/Desativar)",
            "origem": "Derivada de time",
            "descricao": "Codifica a hora em círculo (23h vizinho de 0h).",
        },
        {
            "variavel": "hour_raw (0..23)",
            "escopo": "Global de ML (Hiperparâmetro · Eng. Temporal)",
            "mutabilidade": "Hiperparâmetro (Ativar/Desativar)",
            "origem": "Derivada de time",
            "descricao": "Hora numérica linear para comparar com sin/cos.",
        },
        {
            "variavel": "evaluation_scenario / train_ratio / cutoff",
            "escopo": "Global de ML (Protocolo de Validação)",
            "mutabilidade": "Hiperparâmetro do Experimento",
            "origem": "Configuração do corte",
            "descricao": "Cenário cross-dataset, proporção de treino e janela pré/pós-corte.",
        },
        {
            "variavel": "Hiperparâmetros do Algoritmo",
            "escopo": "Global de ML (Modelo Preditivo)",
            "mutabilidade": "Hiperparâmetro Configurável",
            "origem": "Algoritmo (Ridge, RF, HGB)",
            "descricao": "Regularização, nº de árvores, profundidade e taxa de aprendizado.",
        },
        {
            "variavel": "temp_c (temperature ºC)",
            "escopo": "Domínio (Covariável Exógena · Clima)",
            "mutabilidade": "Covariável Imutável (On/Off)",
            "origem": "Sensor meteorológico (.xlsx)",
            "descricao": "Temperatura externa medida; apenas inclui/exclui como entrada.",
        },
        {
            "variavel": "gen_w (generation w)",
            "escopo": "Domínio (Covariável Exógena · Solar FV)",
            "mutabilidade": "Covariável Imutável (On/Off)",
            "origem": "Medidor solar FV (.xlsx)",
            "descricao": "Geração Solar Fotovoltaica medida; indisponível na fase v4.",
        },
        {
            "variavel": "voltage_lag_1 / amperage_lag_1",
            "escopo": "Domínio (Covariável Elétrica · t-1)",
            "mutabilidade": "Covariável Imutável (On/Off)",
            "origem": "Medidor elétrico (.xlsx)",
            "descricao": "Tensão e corrente da hora anterior; indisponíveis na fase v4.",
        },
        {
            "variavel": "power (W)",
            "escopo": "Domínio (Variável Alvo)",
            "mutabilidade": "Alvo Imutável (y)",
            "origem": "Medidor principal (.xlsx)",
            "descricao": "Grandeza física prevista a cada 1h pelo modelo (Watts médios).",
        },
    ]


def normalize_int_list(
    values: Any,
    default: List[int],
    min_val: int = 1,
    max_val: int = 720,
) -> List[int]:
    """Normaliza uma lista de inteiros positivos ordenados e sem duplicatas."""
    if values is None:
        return list(default)
    if isinstance(values, str):
        tokens = [tok.strip() for tok in values.replace(";", ",").split(",") if tok.strip()]
        raw_items: List[Any] = tokens
    elif isinstance(values, (list, tuple, set)):
        raw_items = list(values)
    else:
        return list(default)

    cleaned: List[int] = []
    for item in raw_items:
        try:
            parsed = int(item)
        except (TypeError, ValueError):
            continue
        if min_val <= parsed <= max_val and parsed not in cleaned:
            cleaned.append(parsed)
    return sorted(cleaned)


def _clamp_float(val: Any, default: float, min_val: float, max_val: float) -> float:
    try:
        num = float(val)
    except (TypeError, ValueError):
        return default
    return max(min_val, min(max_val, num))


def _clamp_int(val: Any, default: int, min_val: int, max_val: int) -> int:
    try:
        num = int(val)
    except (TypeError, ValueError):
        return default
    return max(min_val, min(max_val, num))


def _sanitize_feature_params(raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    src = raw if isinstance(raw, dict) else {}
    feats = {
        "power_lags": normalize_int_list(
            src.get("power_lags"), DEFAULT_FEATURE_PARAMS["power_lags"], 1, 720
        ),
        "rolling_mean_windows": normalize_int_list(
            src.get("rolling_mean_windows"),
            DEFAULT_FEATURE_PARAMS["rolling_mean_windows"],
            2,
            720,
        ),
        "rolling_std_windows": normalize_int_list(
            src.get("rolling_std_windows"),
            DEFAULT_FEATURE_PARAMS["rolling_std_windows"],
            2,
            720,
        ),
        "use_cyclical_hour": bool(
            src.get("use_cyclical_hour", DEFAULT_FEATURE_PARAMS["use_cyclical_hour"])
        ),
        "use_raw_hour": bool(src.get("use_raw_hour", DEFAULT_FEATURE_PARAMS["use_raw_hour"])),
        "use_temperature": bool(
            src.get("use_temperature", DEFAULT_FEATURE_PARAMS["use_temperature"])
        ),
        "use_generation": bool(src.get("use_generation", DEFAULT_FEATURE_PARAMS["use_generation"])),
        "use_electrical_lags": bool(
            src.get("use_electrical_lags", DEFAULT_FEATURE_PARAMS["use_electrical_lags"])
        ),
    }

    has_any = any(
        [
            feats["power_lags"],
            feats["rolling_mean_windows"],
            feats["rolling_std_windows"],
            feats["use_cyclical_hour"],
            feats["use_raw_hour"],
            feats["use_temperature"],
            feats["use_generation"],
            feats["use_electrical_lags"],
        ]
    )
    if not has_any:
        feats["use_cyclical_hour"] = True
    return feats


def _sanitize_hyperparameters(model_key: str, raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    defaults = deepcopy(DEFAULT_HYPERPARAMETERS[model_key])
    src = raw if isinstance(raw, dict) else {}

    if model_key == "Ridge_Linear":
        return {"alpha": round(_clamp_float(src.get("alpha"), defaults["alpha"], 0.01, 1000.0), 4)}

    if model_key == "Random_Forest":
        return {
            "n_estimators": _clamp_int(src.get("n_estimators"), defaults["n_estimators"], 10, 500),
            "max_depth": _clamp_int(src.get("max_depth"), defaults["max_depth"], 2, 50),
            "min_samples_leaf": _clamp_int(
                src.get("min_samples_leaf"), defaults["min_samples_leaf"], 1, 50
            ),
        }

    return {
        "max_iter": _clamp_int(src.get("max_iter"), defaults["max_iter"], 20, 1000),
        "learning_rate": round(
            _clamp_float(src.get("learning_rate"), defaults["learning_rate"], 0.005, 0.5),
            4,
        ),
        "max_depth": _clamp_int(src.get("max_depth"), defaults["max_depth"], 0, 30),
        "l2_regularization": round(
            _clamp_float(src.get("l2_regularization"), defaults["l2_regularization"], 0.0, 50.0),
            4,
        ),
    }


def sanitize_model_config(model_key: str, raw_cfg: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Valida e normaliza a configuração completa de um modelo específico."""
    if model_key not in MODEL_KEYS:
        raise ValueError(f"Modelo desconhecido: {model_key}")

    src = raw_cfg if isinstance(raw_cfg, dict) else {}
    split_raw = src.get("split", {}) if isinstance(src.get("split"), dict) else {}

    return {
        "model_key": model_key,
        "display_name": MODEL_DISPLAY_NAMES[model_key],
        "features": _sanitize_feature_params(src.get("features")),
        "split": {
            "evaluation_scenario": sanitize_scenario(split_raw.get("evaluation_scenario")),
            "train_ratio": round(
                _clamp_float(
                    split_raw.get("train_ratio"),
                    DEFAULT_SPLIT_PARAMS["train_ratio"],
                    0.50,
                    0.95,
                ),
                2,
            ),
            "random_state": _clamp_int(
                split_raw.get("random_state"),
                DEFAULT_SPLIT_PARAMS["random_state"],
                0,
                99999,
            ),
            "context_hours": _clamp_int(
                split_raw.get("context_hours"),
                DEFAULT_SPLIT_PARAMS["context_hours"],
                24,
                168,
            ),
            "horizon_hours": _clamp_int(
                split_raw.get("horizon_hours"),
                DEFAULT_SPLIT_PARAMS["horizon_hours"],
                24,
                168,
            ),
        },
        "hyperparameters": _sanitize_hyperparameters(model_key, src.get("hyperparameters")),
    }


def get_default_model_config(model_key: str) -> Dict[str, Any]:
    """Retorna a configuração padrão (baseline) validada de um modelo."""
    return sanitize_model_config(model_key, None)


def get_default_all_configs() -> Dict[str, Dict[str, Any]]:
    """Retorna o dicionário completo com as configurações padrão de todos os modelos."""
    return {key: get_default_model_config(key) for key in MODEL_KEYS}
