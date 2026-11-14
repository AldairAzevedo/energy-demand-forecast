"""Carregadores e normalizadores horários dos datasets oficiais Zenodo (v1, v2 e v4)."""

import io
import os
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from src.utils.file_resilience import read_bytes_resilient


def find_col(columns: Sequence[str], keyword: str, exclude: str = "") -> Optional[str]:
    """Localiza coluna por palavra-chave case-insensitive (ex.: 'temp' trata ºC e ˚C)."""
    for col in columns:
        if keyword in col and (not exclude or exclude not in col):
            return col
    return None


def extract_hours(df: pd.DataFrame, time_col: Optional[str]) -> np.ndarray:
    """Extrai hora do dia (0..23) de colunas datetime.time, datetime.datetime ou strings."""
    fallback = np.arange(len(df), dtype=float) % 24.0
    if time_col is None or len(df) == 0:
        return fallback
    parsed = pd.to_datetime(df[time_col].astype(str), format="mixed", errors="coerce")
    if parsed.notna().all():
        return parsed.dt.hour.to_numpy(dtype=float)
    if parsed.notna().any():
        hours = parsed.dt.hour.to_numpy(dtype=float)
        missing = np.isnan(hours)
        hours[missing] = fallback[missing]
        return hours
    return fallback


def format_day_hour_labels(hours_of_day: Sequence[float], dataset_tag: str = "") -> List[str]:
    """Constrói rótulos cronológicos legíveis (ex.: 'v1 D001 00:00') para o eixo X."""
    prefix = f"{dataset_tag} " if dataset_tag else ""
    labels: List[str] = []
    for idx, hour_val in enumerate(hours_of_day):
        day_num = (idx // 24) + 1
        hour_int = int(hour_val) % 24
        labels.append(f"{prefix}D{day_num:03d} · {hour_int:02d}:00")
    return labels


def load_hourly_series(
    file_path: str,
    dataset_tag: str = "",
) -> Tuple[pd.DataFrame, Dict[str, Optional[str]], int]:
    """Lê séries de 5 minutos (v1.0 ou v2.0) e agrega em tabela horária."""
    raw_bytes = read_bytes_resilient(file_path)
    df = pd.read_excel(io.BytesIO(raw_bytes))
    df.columns = [str(c).strip().lower() for c in df.columns]
    cols = list(df.columns)

    col_map: Dict[str, Optional[str]] = {
        "power": find_col(cols, "power", exclude="gen"),
        "gen": find_col(cols, "gen"),
        "temp": find_col(cols, "temp"),
        "volt": find_col(cols, "volt"),
        "amp": find_col(cols, "amp"),
        "time": find_col(cols, "time"),
    }

    required = [c for c in (col_map["power"], col_map["temp"]) if c is not None]
    df_clean = df.dropna(subset=required).copy()
    total_5min_samples = len(df_clean)

    agg_map: Dict[str, str] = {}
    for key in ("power", "gen", "temp", "volt", "amp"):
        col_name = col_map[key]
        if col_name:
            agg_map[col_name] = "mean"

    df_clean["hour_bucket"] = np.arange(len(df_clean)) // 12
    df_clean["hour_of_day"] = extract_hours(df_clean, col_map["time"])
    agg_map["hour_of_day"] = "first"

    hourly = df_clean.groupby("hour_bucket").agg(agg_map).reset_index(drop=True)
    hourly["timestamp_label"] = format_day_hour_labels(
        hourly["hour_of_day"].to_numpy(dtype=float),
        dataset_tag=dataset_tag,
    )
    return hourly, col_map, total_5min_samples


def load_v4_days(
    data_dir: str,
    days: Tuple[int, ...] = (1, 2, 3),
) -> Tuple[pd.DataFrame, Dict[str, Optional[str]], int]:
    """Combina weather_forecast e real_consumption horários dos dias especificados de v4."""
    frames: List[pd.DataFrame] = []
    for day_idx in days:
        weather_path = os.path.join(
            data_dir, f"data_v4.{day_idx}.1_weather_forecast_day_{day_idx}.xlsx"
        )
        real_path = os.path.join(
            data_dir, f"data_v4.{day_idx}.2_real_consumption_day_{day_idx}.xlsx"
        )
        w_df = pd.read_excel(io.BytesIO(read_bytes_resilient(weather_path)))
        r_df = pd.read_excel(io.BytesIO(read_bytes_resilient(real_path)))

        w_df.columns = [str(c).strip().lower() for c in w_df.columns]
        r_df.columns = [str(c).strip().lower() for c in r_df.columns]

        temp_col = find_col(list(w_df.columns), "temp")
        power_col = find_col(list(r_df.columns), "power", exclude="gen")
        time_col = find_col(list(r_df.columns), "time") or find_col(list(w_df.columns), "time")
        if temp_col is None or power_col is None:
            raise ValueError(f"Colunas esperadas ausentes nos arquivos data_v4 dia {day_idx}.")

        hours = extract_hours(r_df, time_col)
        day_frame = pd.DataFrame(
            {
                "power (w)": pd.to_numeric(r_df[power_col], errors="coerce").astype(float),
                "temperature (ºc)": pd.to_numeric(w_df[temp_col], errors="coerce").astype(float),
                "hour_of_day": hours,
            }
        )
        day_frame["timestamp_label"] = [f"v4 Dia {day_idx} · {int(h) % 24:02d}:00" for h in hours]
        frames.append(day_frame)

    combined = pd.concat(frames, ignore_index=True)
    col_map: Dict[str, Optional[str]] = {
        "power": "power (w)",
        "gen": None,
        "temp": "temperature (ºc)",
        "volt": None,
        "amp": None,
        "time": None,
    }
    return combined, col_map, len(combined)
