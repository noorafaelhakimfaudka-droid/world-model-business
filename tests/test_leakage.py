import pandas as pd
from pathlib import Path
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline

@pytest.fixture
def data_for_leakage():
    # Gunakan dev_orders utuh karena kita mau ngetes kontrol positif 
    # (sengaja membocorkan fitur dari masa depan)
    path = Path('data/processed/dev_orders.parquet')
    if not path.exists():
        pytest.skip("dev_orders.parquet tidak ditemukan")
    df = pd.read_parquet(path).head(2000) # Ambil sebagian kecil agar tes cepat
    return df

def test_positive_control_leakage(data_for_leakage):
    df = data_for_leakage.dropna(subset=['is_late', 'actual_delivery_days'])
    
    # 1. Model Jujur di T0 (Hanya pakai harga dan estimasi)
    X_honest = df[['total_items_value', 'estimated_delivery_days']]
    y = df['is_late']
    
    # Harus ada setidaknya 1 kelas positif dan 1 kelas negatif
    if y.nunique() < 2:
        pytest.skip("Tidak cukup variasi kelas untuk tes")
        
    model_honest = make_pipeline(SimpleImputer(), LogisticRegression())
    model_honest.fit(X_honest, y)
    preds_honest = model_honest.predict(X_honest)
    score_honest = precision_score(y, preds_honest, zero_division=0)
    
    # 2. Model Curang (Sengaja memasukkan 'actual_delivery_days' yang baru diketahui di T2)
    X_leak = df[['total_items_value', 'estimated_delivery_days', 'actual_delivery_days']]
    model_leak = make_pipeline(SimpleImputer(), LogisticRegression())
    model_leak.fit(X_leak, y)
    preds_leak = model_leak.predict(X_leak)
    score_leak = precision_score(y, preds_leak, zero_division=0)
    
    # Skoring model jujur pasti jelek karena fitur sedikit dan susah (mungkin 0%)
    # Tapi skoring model curang PASTI lonjak mendekati 100% karena algoritma bisa 
    # menebak bahwa actual > estimated = late
    assert score_leak > score_honest + 0.5, "Kontrol positif gagal: Model curang tidak melonjak!"
    assert score_leak > 0.9, "Kontrol positif gagal: Fitur bocor tidak membuat model sempurna!"
