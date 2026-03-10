"""
tests/test_pipeline.py - pytest test suite for Stock Anomaly Detection Pipeline
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def make_ohlcv(n=100):
    """Create synthetic OHLCV DataFrame."""
    dates = pd.date_range('2020-01-01', periods=n, freq='B')
    close = 100 + np.cumsum(np.random.randn(n) * 2)
    df = pd.DataFrame({
        'open': close * 0.99,
        'high': close * 1.01,
        'low': close * 0.98,
        'close': close,
        'volume': np.random.randint(1_000_000, 5_000_000, n),
    }, index=dates)
    return df


def test_features_present():
    """Feature engineering must produce required columns."""
    from src.feature_engineering import FeatureEngineer
    df = make_ohlcv(100)
    engineer = FeatureEngineer()
    features = engineer.calculate_all_features(df)
    required = ['log_return', 'ma_20', 'volatility_20']
    for col in required:
        assert col in features.columns, f"Missing required feature: {col}"


def test_three_method_flags():
    """Anomaly detection must produce z_score_flag, isolation_forest_flag, lof_flag."""
    from src.feature_engineering import FeatureEngineer
    from src.anomaly_detection import AnomalyDetector
    df = make_ohlcv(200)
    engineer = FeatureEngineer()
    features = engineer.calculate_all_features(df)
    detector = AnomalyDetector()
    results = detector.detect_anomalies(features)
    for col in ['z_score_flag', 'isolation_forest_flag', 'lof_flag']:
        assert col in results.columns, f"Missing column: {col}"


def test_four_db_tables():
    """Database must initialize with 4 required tables."""
    import tempfile
    from src.database import DatabaseManager
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        tmp_path = f.name
    try:
        db = DatabaseManager(tmp_path)
        db.initialize_database()
        import sqlite3
        conn = sqlite3.connect(tmp_path)
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        conn.close()
        required_tables = {'stocks', 'price_data', 'news_articles', 'anomalies'}
        for t in required_tables:
            assert t in tables, f"Missing table: {t}"
    finally:
        os.unlink(tmp_path)


def test_fomc_dates_count():
    """FOMC dates list must have at least 60 entries (2015-2024)."""
    from src.fomc_events import get_fomc_dates
    fomc = get_fomc_dates()
    assert len(fomc) >= 60, f"Expected >= 60 FOMC dates, got {len(fomc)}"


def test_anomaly_type_values():
    """classify_anomaly_type must return one of the 4 valid type strings."""
    from src.anomaly_detection import AnomalyDetector
    from src.fomc_events import get_fomc_dates
    detector = AnomalyDetector()
    fomc = get_fomc_dates()
    valid_types = {'macroeconomic_event', 'earnings_surprise', 'sector_contagion', 'unexplained'}

    test_dates = [date(2022, 3, 16), date(2020, 3, 15), date(2019, 6, 1)]
    for d in test_dates:
        result = detector.classify_anomaly_type(d, fomc)
        assert result in valid_types, f"Invalid anomaly type: {result}"


def test_fomc_labeling():
    """label_fomc_anomalies must add fomc_related boolean column."""
    from src.fomc_events import label_fomc_anomalies
    df = pd.DataFrame({'anomaly_date': ['2022-03-16', '2022-03-17', '2022-01-01']})
    result = label_fomc_anomalies(df)
    assert 'fomc_related' in result.columns
    assert result.iloc[0]['fomc_related'] == True   # 2022-03-16 is FOMC day
    assert result.iloc[2]['fomc_related'] == False  # Jan 1 is not near FOMC


def test_contagion_detection():
    """detect_sector_contagion should find dates when multiple stocks have anomalies."""
    from src.contagion_analysis import detect_sector_contagion
    # 3 tickers all having anomalies on same day
    anomalies_dict = {
        'AAPL': pd.DataFrame({'anomaly_date': [date(2020, 3, 16), date(2020, 3, 20)]}),
        'MSFT': pd.DataFrame({'anomaly_date': [date(2020, 3, 16), date(2021, 5, 1)]}),
        'TSLA': pd.DataFrame({'anomaly_date': [date(2020, 3, 17), date(2021, 9, 1)]}),
    }
    contagion = detect_sector_contagion(anomalies_dict, min_stocks=3)
    assert len(contagion) > 0, "Should detect contagion on 2020-03-16"
