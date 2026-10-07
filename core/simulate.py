"""
core/simulate.py
Mesin simulasi World Model dengan pencarian cepat ke sim_grid.parquet (462 skenario)
"""

import streamlit as st
from core.load import load_agg

@st.cache_data(show_spinner=False)
def sim_lookup(b: int, s: int, k: int) -> dict:
    """
    Mengambil hasil simulasi pra-hitung dari sim_grid.parquet.
    b: buffer hari SLA (0 s/d 5)
    s: percepatan seller % (0 s/d 50, kelipatan 5)
    k: percepatan kurir % (0 s/d 30, kelipatan 5)
    """
    g = load_agg("sim_grid")
    if g.empty:
        # Fallback perhitungan instan jika file grid belum dimuat
        base_late = 0.080
        delta_late = min(0.068, b * 0.02007) + (s / 100.0) * 0.018 + (k / 100.0) * 0.032
        late_baru = max(0.008, base_late - delta_late)
        delta_bad = int(round((base_late - late_baru) * 0.502 * 86283))
        biaya = int(round((s / 100.0 * 2.5 + k / 100.0 * 25.0) * 86283))
        return {
            "buffer": b,
            "seller_pct": s,
            "kurir_pct": k,
            "late_rate": round(late_baru, 4),
            "bad_review_rate": round(0.148 - (delta_bad / 86283), 4),
            "bad_saved": delta_bad,
            "biaya": biaya,
            "val_saved_mid": delta_bad * 70,
            "val_saved_min": delta_bad * 48,
            "val_saved_max": delta_bad * 92,
            "cost_per_saved": round(biaya / delta_bad, 2) if delta_bad > 0 else 0
        }
        
    # Ambil baris terdekat jika nilai slider sedikit meleset
    sub = g[(g["buffer"] == b) & (g["seller_pct"] == s) & (g["kurir_pct"] == k)]
    if len(sub) > 0:
        row = sub.iloc[0].to_dict()
    else:
        # Cari yang paling mendekati
        dist = (g["buffer"] - b).abs() + (g["seller_pct"] - s).abs() + (g["kurir_pct"] - k).abs()
        row = g.iloc[dist.argmin()].to_dict()
        
    return row
