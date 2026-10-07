import pandas as pd
import numpy as np
from pathlib import Path
import pytest

@pytest.fixture
def t0_features():
    path = Path('data/processed/features_t0.parquet')
    if not path.exists():
        pytest.skip("File features_t0.parquet belum ada")
    return pd.read_parquet(path)

def test_t0_has_no_future_columns(t0_features):
    # Di T0 tidak boleh ada actual_delivery_days atau seller_handling_days
    forbidden = ['actual_delivery_days', 'seller_handling_days', 'carrier_transit_days', 'order_delivered_customer_date']
    for col in forbidden:
        assert col not in t0_features.columns, f"Bocor! Kolom {col} tidak boleh ada di T0."

def test_as_of_logic_sanity(t0_features):
    # Pastikan rata-rata late_rate seller masuk akal (antara 0 dan 1)
    assert t0_features['seller_recent_late_rate_30d'].min() >= 0.0
    assert t0_features['seller_recent_late_rate_30d'].max() <= 1.0
    
    # Pastikan rata-rata skor seller antara 1 dan 5
    assert t0_features['seller_recent_avg_score_30d'].min() >= 1.0
    assert t0_features['seller_recent_avg_score_30d'].max() <= 5.0
