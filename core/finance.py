"""
core/finance.py
Perhitungan finansial: Titik Impas Voucher Layanan Pelanggan (CS) dan Ukuran Sampel A/B Testing
"""

from math import ceil
from scipy.stats import norm

def calc_voucher_roi(voucher_cost: float, v_ret: float, r_pct: float, p_pct: float, n_tagged: int = 1000):
    """
    Menghitung laba/rugi dan titik impas pembagian voucher CS:
    v: voucher_cost (R$ 15)
    V_ret: nilai pelanggan yang terselamatkan (AOV R$ 137.75 atau rentang CLV)
    r_pct: persentase terselamatkan dari komplain/churn (misal 15%)
    p_pct: presisi penandaan AI (misal 8.0% di T0)
    """
    r = r_pct / 100.0
    p = p_pct / 100.0
    
    # 1. Per pelanggan yang benar-benar telat
    untung_per_telat = (r * v_ret) - voucher_cost
    impas_per_telat = (voucher_cost / v_ret) * 100.0 if v_ret > 0 else 0
    
    # 2. Per pesanan yang ditandai oleh AI (jika voucher diberikan ke semua pesanan top-K)
    untung_per_ditandai = (p * r * v_ret) - voucher_cost
    impas_per_ditandai = (voucher_cost / (p * v_ret)) * 100.0 if (p * v_ret) > 0 else 0
    
    total_net = untung_per_ditandai * n_tagged
    
    return {
        "untung_per_telat": round(untung_per_telat, 2),
        "impas_per_telat_pct": round(impas_per_telat, 1),
        "untung_per_ditandai": round(untung_per_ditandai, 2),
        "impas_per_ditandai_pct": round(impas_per_ditandai, 1),
        "total_net": round(total_net, 2)
    }

def calc_ab_sample(p1: float = 0.080, p2: float = 0.055, alpha: float = 0.05, power: float = 0.80, weekly_orders: int = 1200):
    """
    Menghitung ukuran sampel dua proporsi Z-test (dua sisi)
    Default: baseline 8.0% (p1), target 5.5% (p2) -> mereproduksi ~1.560 pesanan per kelompok
    """
    za = norm.ppf(1 - alpha / 2)
    zb = norm.ppf(power)
    
    diff = abs(p1 - p2)
    if diff == 0:
        return {"n_per_group": 0, "total_n": 0, "weeks": 0}
        
    n = (za + zb)**2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (diff**2)
    n_per_group = ceil(n)
    total_n = 2 * n_per_group
    weeks = ceil(total_n / weekly_orders) if weekly_orders > 0 else 0
    
    return {
        "n_per_group": n_per_group,
        "total_n": total_n,
        "weeks": weeks
    }
