"""Carregadores e normalizadores horários dos datasets oficiais Zenodo (v1, v2 e v4)."""

import hashlib
import io
import json
import os
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from src.utils.file_resilience import read_bytes_resilient
from src.utils.json_io import load_json, save_json

_CACHE_DIR_NAME = "_hourly_cache"
_MEMORY_BUNDLE_CACHE: Dict[Tuple[Any, ...], Tuple[pd.DataFrame, Dict[str, Optional[str]], int]] = {}


def clear_dataset_caches() -> None:
    """Limpa o cache em memória de séries horárias."""
    _MEMORY_BUNDLE_CACHE.clear()


def _bytes_signature(raw_bytes: bytes) -> Dict[str, Any]:
    return {
        "size": len(raw_bytes),
        "sha256": hashlib.sha256(raw_bytes).hexdigest(),
    }


def _stat_signature(file_path: str) -> Tuple[int, int]:
    st_info = os.stat(file_path)
    return int(st_info.st_size), int(st_info.st_mtime_ns)


def _clone_bundle(
    bundle: Tuple[pd.DataFrame, Dict[str, Optional[str]], int],
) -> Tuple[pd.DataFrame, Dict[str, Optional[str]], int]:
    df, col_map, count = bundle
    return df.copy(), dict(col_map), int(count)


def _read_disk_cache(
    cache_dir: str,
    cache_stem: str,
    expected_sources: Dict[str, Dict[str, Any]],
) -> Optional[Tuple[pd.DataFrame, Dict[str, Optional[str]], int]]:
    csv_path = os.path.join(cache_dir, f"{cache_stem}.csv")
    meta_path = os.path.join(cache_dir, f"{cache_stem}.meta.json")
    if not (os.path.exists(csv_path) and os.path.exists(meta_path)):
        return None
    try:
        meta = load_json(meta_path)
        if meta.get("sources") != expected_sources:
            return None
        df = pd.read_csv(csv_path, float_precision="round_trip")
        if "timestamp_label" in df.columns:
            df["timestamp_label"] = df["timestamp_label"].astype(str)
        for col in df.columns:
            if col != "timestamp_label":
                df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)
        col_map = {str(k): (None if v is None else str(v)) for k, v in meta["col_map"].items()}
        total_samples = int(meta["total_samples"])
        return df, col_map, total_samples
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def _write_disk_cache(
    cache_dir: str,
    cache_stem: str,
    expected_sources: Dict[str, Dict[str, Any]],
    df: pd.DataFrame,
    col_map: Dict[str, Optional[str]],
    total_samples: int,
) -> None:
    try:
        os.makedirs(cache_dir, exist_ok=True)
        csv_path = os.path.join(cache_dir, f"{cache_stem}.csv")
        meta_path = os.path.join(cache_dir, f"{cache_stem}.meta.json")
        tmp_csv = f"{csv_path}.tmp"
        df.to_csv(tmp_csv, index=False)
        os.replace(tmp_csv, csv_path)
        save_json(
            {
                "sources": expected_sources,
                "col_map": col_map,
                "total_samples": int(total_samples),
            },
            meta_path,
        )
    except OSError:
        pass


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
    """Lê séries de 5 minutos (v1.0 ou v2.0) e agrega em tabela horária (com cache)."""
    abs_path = os.path.abspath(file_path)
    mem_key = ("hourly", abs_path, dataset_tag, *_stat_signature(file_path))
    cached_mem = _MEMORY_BUNDLE_CACHE.get(mem_key)
    if cached_mem is not None:
        return _clone_bundle(cached_mem)

    raw_bytes = read_bytes_resilient(file_path)
    src_name = os.path.basename(file_path)
    expected_sources = {src_name: _bytes_signature(raw_bytes)}
    cache_dir = os.path.join(os.path.dirname(abs_path), _CACHE_DIR_NAME)
    safe_tag = re.sub(r"[^a-zA-Z0-9_-]+", "_", dataset_tag or "default")
    stem = re.sub(r"[^a-zA-Z0-9_.-]+", "_", os.path.splitext(src_name)[0])
    cache_stem = f"{stem}__{safe_tag}"

    cached_disk = _read_disk_cache(cache_dir, cache_stem, expected_sources)
    if cached_disk is not None:
        _MEMORY_BUNDLE_CACHE[mem_key] = cached_disk
        return _clone_bundle(cached_disk)

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

    bundle = (hourly, col_map, total_5min_samples)
    _write_disk_cache(cache_dir, cache_stem, expected_sources, hourly, col_map, total_5min_samples)
    _MEMORY_BUNDLE_CACHE[mem_key] = bundle
    return _clone_bundle(bundle)


def load_v4_days(
    data_dir: str,
    days: Tuple[int, ...] = (1, 2, 3),
) -> Tuple[pd.DataFrame, Dict[str, Optional[str]], int]:
    """Combina weather_forecast e real_consumption horários dos dias especificados de v4."""
    abs_dir = os.path.abspath(data_dir)
    day_paths: List[Tuple[int, str, str]] = []
    mem_stats: List[Tuple[str, int, int]] = []
    for day_idx in days:
        w_path = os.path.join(data_dir, f"data_v4.{day_idx}.1_weather_forecast_day_{day_idx}.xlsx")
        r_path = os.path.join(data_dir, f"data_v4.{day_idx}.2_real_consumption_day_{day_idx}.xlsx")
        day_paths.append((day_idx, w_path, r_path))
        mem_stats.append((w_path, *_stat_signature(w_path)))
        mem_stats.append((r_path, *_stat_signature(r_path)))

    mem_key = ("v4", abs_dir, tuple(days), tuple(mem_stats))
    cached_mem = _MEMORY_BUNDLE_CACHE.get(mem_key)
    if cached_mem is not None:
        return _clone_bundle(cached_mem)

    raw_blobs: List[Tuple[int, str, bytes, str, bytes]] = []
    expected_sources: Dict[str, Dict[str, Any]] = {}
    for day_idx, w_path, r_path in day_paths:
        w_bytes = read_bytes_resilient(w_path)
        r_bytes = read_bytes_resilient(r_path)
        w_name = os.path.basename(w_path)
        r_name = os.path.basename(r_path)
        expected_sources[w_name] = _bytes_signature(w_bytes)
        expected_sources[r_name] = _bytes_signature(r_bytes)
        raw_blobs.append((day_idx, w_name, w_bytes, r_name, r_bytes))

    cache_dir = os.path.join(abs_dir, _CACHE_DIR_NAME)
    cache_stem = f"v4_days_{'_'.join(str(d) for d in days)}"
    cached_disk = _read_disk_cache(cache_dir, cache_stem, expected_sources)
    if cached_disk is not None:
        _MEMORY_BUNDLE_CACHE[mem_key] = cached_disk
        return _clone_bundle(cached_disk)

    frames: List[pd.DataFrame] = []
    for day_idx, _w_name, w_bytes, _r_name, r_bytes in raw_blobs:
        w_df = pd.read_excel(io.BytesIO(w_bytes))
        r_df = pd.read_excel(io.BytesIO(r_bytes))

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
    bundle = (combined, col_map, len(combined))
    _write_disk_cache(cache_dir, cache_stem, expected_sources, combined, col_map, len(combined))
    _MEMORY_BUNDLE_CACHE[mem_key] = bundle
    return _clone_bundle(bundle)
