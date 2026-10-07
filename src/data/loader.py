"""
src/data/loader.py
Fungsi pembantu tipis untuk memuat data di dalam Jupyter Notebook
sesuai prinsip "Thin Notebook" (PRD §4.1).
"""

from pathlib import Path
import pandas as pd


def get_project_root() -> Path:
    """Mengembalikan path absolut direktori proyek."""
    return Path(__file__).resolve().parent.parent.parent


def load_dev_orders() -> pd.DataFrame:
    """
    Memuat data pengembangan (Development / EDA) yang sudah dipotong dari holdout.
    Rentang: 2017-01-01 s.d. 2018-06-30 (86.283 pesanan).
    AMAN DARI KEBOCORAN HOLDOUT.
    """
    root = get_project_root()
    dev_path = root / "data" / "processed" / "dev_orders.parquet"
    if not dev_path.exists():
        raise FileNotFoundError(
            f"Berkas {dev_path} belum tersedia. Jalankan src/data/split_holdout.py terlebih dahulu."
        )

    df = pd.read_parquet(dev_path)
    # Konversi kolom tanggal ke format datetime
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])

    return df


def verify_holdout_sealed() -> dict[str, str]:
    """Memeriksa bahwa holdout tetap terkunci dan checksum cocok."""
    root = get_project_root()
    checksum_file = root / "experiments" / "holdout_checksum.sha256"
    holdout_file = root / "data" / "processed" / "holdout_orders.parquet"

    if not checksum_file.exists() or not holdout_file.exists():
        return {"status": "BELUM TERKUNCI"}

    import hashlib
    sha256 = hashlib.sha256()
    with open(holdout_file, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    current_hash = sha256.hexdigest()
    sealed_hash = checksum_file.read_text(encoding="utf-8").split()[0].strip()

    is_intact = current_hash == sealed_hash
    return {
        "status": "TERKUNCI & AMAN" if is_intact else "SEGEL RUSAK",
        "sha256": current_hash,
    }
