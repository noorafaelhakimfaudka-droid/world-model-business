"""
src/data/split_holdout.py
Memotong dan mengunci data holdout (2 bulan terakhir: 2018-07-01 s.d. 2018-08-31)
SEBELUM EDA dimulai, sesuai PRD §3.1, PRD §5 (Langkah 2), dan Pagar Proyek.
Menghasilkan:
1. data/processed/dev_orders.parquet (Data pengembangan & EDA, Jan 2017 - Jun 2018)
2. data/processed/holdout_orders.parquet (Data uji akhir TERKUNCI, Jul 2018 - Ags 2018)
3. experiments/holdout_checksum.sha256 (Segel integritas SHA-256)
"""

import hashlib
import sqlite3
from pathlib import Path
import pandas as pd


def split_and_lock_holdout(
    db_path: Path, output_dir: Path, exp_dir: Path
) -> dict[str, str]:
    db_path = Path(db_path)
    output_dir = Path(output_dir)
    exp_dir = Path(exp_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    exp_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        # Ambil data pesanan pada jendela stabil (2017-01-01 s.d. 2018-08-31)
        query = """
            SELECT * 
            FROM mart_orders 
            WHERE order_purchase_timestamp >= '2017-01-01 00:00:00'
              AND order_purchase_timestamp <= '2018-08-31 23:59:59'
            ORDER BY order_purchase_timestamp ASC
        """
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    df["purchase_ts"] = pd.to_datetime(df["order_purchase_timestamp"])

    # Titik pisah: 1 Juli 2018 pukul 00:00:00
    split_cutoff = pd.to_datetime("2018-07-01 00:00:00")

    dev_df = df[df["purchase_ts"] < split_cutoff].copy()
    holdout_df = df[df["purchase_ts"] >= split_cutoff].copy()

    # Drop kolom bantu purchase_ts agar skema identik dengan mart
    dev_df.drop(columns=["purchase_ts"], inplace=True)
    holdout_df.drop(columns=["purchase_ts"], inplace=True)

    dev_file = output_dir / "dev_orders.parquet"
    holdout_file = output_dir / "holdout_orders.parquet"

    # Simpan ke parquet
    dev_df.to_parquet(dev_file, index=False)
    holdout_df.to_parquet(holdout_file, index=False)

    # Hitung SHA-256 checksum berkas holdout sebagai segel integritas
    sha256 = hashlib.sha256()
    with open(holdout_file, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    checksum = sha256.hexdigest()

    checksum_file = exp_dir / "holdout_checksum.sha256"
    checksum_file.write_text(f"{checksum}  {holdout_file.name}\n", encoding="utf-8")

    return {
        "dev_rows": str(len(dev_df)),
        "dev_date_range": f"{df['order_purchase_timestamp'].min()} s.d. {dev_df['order_purchase_timestamp'].max()}",
        "holdout_rows": str(len(holdout_df)),
        "holdout_date_range": f"{holdout_df['order_purchase_timestamp'].min()} s.d. {holdout_df['order_purchase_timestamp'].max()}",
        "holdout_sha256": checksum,
    }


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent.parent
    db = base_dir / "data" / "processed" / "olist.db"
    out = base_dir / "data" / "processed"
    exp = base_dir / "experiments"

    print("=== MEMOTONG DAN MENGUNCI HOLDOUT (PRD §3.1) ===")
    results = split_and_lock_holdout(db, out, exp)
    print(f"Data Pengembangan (Dev/EDA) : {int(results['dev_rows']):,} baris ({results['dev_date_range']})")
    print(f"Data Holdout Terkunci       : {int(results['holdout_rows']):,} baris ({results['holdout_date_range']})")
    print(f"Segel SHA-256 Holdout       : {results['holdout_sha256']}")
