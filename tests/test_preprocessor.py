"""Testes unitários para limpeza de dados, interpolação e engenharia de features."""

import numpy as np

from src.core.preprocessor import DataCleaner, FeatureEngineer, TimeSeriesInterpolator


def test_cleaner_replaces_sentinel_values():
    """Verifica que o valor sentinela -9999 é substituído por NaN e tratado."""
    raw_data = np.array([25.0, -9999.0, 28.0, 30.0, -9999.0])
    cleaned = DataCleaner.replace_sentinel(raw_data, sentinel=-9999.0)

    assert np.isnan(cleaned[1])
    assert np.isnan(cleaned[4])
    assert cleaned[0] == 25.0

    interpolated = DataCleaner.fill_missing_linear(cleaned)
    assert not np.any(np.isnan(interpolated))
    # Interpolação linear entre 25 e 28 -> 26.5
    assert np.isclose(interpolated[1], 26.5)


def test_time_series_interpolator_alignment():
    """Valida a interpolação temporal de dados assíncronos para horas cheias."""
    # Pontos meteorológicos registrados em minutos irregulares
    weather_times = np.array([0.0, 0.8, 1.4, 2.0])  # horas
    weather_temps = np.array([20.0, 24.0, 27.0, 30.0])  # °C

    target_hours = np.array([0.0, 1.0, 2.0])
    interpolated = TimeSeriesInterpolator.interpolate_1d(
        source_times=weather_times,
        source_values=weather_temps,
        target_times=target_hours,
    )

    assert len(interpolated) == 3
    assert interpolated[0] == 20.0
    assert interpolated[2] == 30.0
    # Na hora 1.0: interpolacao linear exata
    assert np.isclose(interpolated[1], 25.0)


def test_feature_engineer_daily_aggregation():
    """Testa a agregação diária de valores máximos de demanda e médias meteorológicas."""
    # 2 dias com 24 horas cada (48 horas)
    np.random.seed(42)
    demand = np.arange(48, dtype=float)

    daily_max_demand = FeatureEngineer.aggregate_daily_max(demand, hours_per_day=24)
    assert len(daily_max_demand) == 2
    assert daily_max_demand[0] == 23.0  # max do dia 1 (0 a 23)
    assert daily_max_demand[1] == 47.0  # max do dia 2 (24 a 47)
