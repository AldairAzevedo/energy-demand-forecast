"""Módulo de pré-processamento, limpeza de sentinelas, interpolação e engenharia de features."""

from typing import Tuple

import numpy as np
import pandas as pd


class DataCleaner:
    """Responsável pela higienização de séries temporais físicas e sentinelas de sensores."""

    @staticmethod
    def replace_sentinel(
        values: np.ndarray,
        sentinel: float = -9999.0,
    ) -> np.ndarray:
        """Substitui valores sentinelas de erro de sensores meteorológicos por NaN."""
        arr = np.asarray(values, dtype=float).copy()
        # Tolerância numérica para sentinelas como -9999 ou -9999.0
        mask = np.isclose(arr, sentinel, atol=1e-3) | (arr <= -9000.0)
        arr[mask] = np.nan
        return arr

    @staticmethod
    def fill_missing_linear(values: np.ndarray) -> np.ndarray:
        """Preenche valores ausentes (NaN) via interpolação linear temporal."""
        arr = np.asarray(values, dtype=float).copy()
        series = pd.Series(arr)
        # Interpola linearmente e trata bordas com preenchimento para frente/trás
        interpolated = series.interpolate(method="linear").bfill().ffill()
        return interpolated.to_numpy()

    @staticmethod
    def deduplicate_timestamps(
        timestamps: np.ndarray,
        values: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Remove registros com timestamps duplicados mantendo a primeira ocorrência."""
        df = pd.DataFrame({"time": timestamps, "value": values})
        df_unique = df.drop_duplicates(subset=["time"], keep="first")
        return df_unique["time"].to_numpy(), df_unique["value"].to_numpy()


class TimeSeriesInterpolator:
    """Sincroniza séries temporais de taxas de amostragem assíncronas."""

    @staticmethod
    def interpolate_1d(
        source_times: np.ndarray,
        source_values: np.ndarray,
        target_times: np.ndarray,
    ) -> np.ndarray:
        """Interpola linearmente medições meteorológicas para os horários de demanda.

        Args:
            source_times: Vetor de timestamps originais (ex: horas decimais).
            source_values: Leituras físicas registradas.
            target_times: Vetor de timestamps uniformes desejados.

        Returns:
            Vetor interpolado correspondente exatamente aos target_times.
        """
        # Garante ordenação cronológica
        order = np.argsort(source_times)
        s_times = np.asarray(source_times)[order]
        s_vals = np.asarray(source_values)[order]
        return np.interp(target_times, s_times, s_vals)


class FeatureEngineer:
    """Engenharia de atributos multivariados e agregação de séries temporais elétricas."""

    @staticmethod
    def aggregate_daily_max(
        hourly_series: np.ndarray,
        hours_per_day: int = 24,
    ) -> np.ndarray:
        """Calcula o valor de pico (máximo) diário de uma série temporal contínua."""
        arr = np.asarray(hourly_series, dtype=float).ravel()
        n_days = len(arr) // hours_per_day
        trimmed = arr[: n_days * hours_per_day]
        matrix = trimmed.reshape((n_days, hours_per_day))
        return np.max(matrix, axis=1)

    @staticmethod
    def aggregate_daily_mean(
        hourly_series: np.ndarray,
        hours_per_day: int = 24,
    ) -> np.ndarray:
        """Calcula o valor médio diário de uma grandeza física (ex: umidade, vento)."""
        arr = np.asarray(hourly_series, dtype=float).ravel()
        n_days = len(arr) // hours_per_day
        trimmed = arr[: n_days * hours_per_day]
        matrix = trimmed.reshape((n_days, hours_per_day))
        return np.mean(matrix, axis=1)

    @staticmethod
    def standardize(matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Normalização Z-Score (média zero e desvio padrão unitário).

        Returns:
            Tupla (matriz_normalizada, medias, desvios_padrao).
        """
        arr = np.asarray(matrix, dtype=float)
        mean = np.mean(arr, axis=0)
        std = np.std(arr, axis=0)
        # Proteção contra divisão por zero em variáveis constantes
        std_safe = np.where(std < 1e-12, 1.0, std)
        normalized = (arr - mean) / std_safe
        return normalized, mean, std
