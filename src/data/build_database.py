"""
src/data/build_database.py
Membangun lapisan data bertingkat di SQLite (data/processed/olist.db)
sesuai PRD §4.1 dan PRD §5 (Langkah 1).
Menjalankan:
1. Pemuatan Raw CSV -> tabel raw_*
2. Transformasi Clean (sql/02_clean.sql) -> tabel clean_*
3. Pembentukan Mart (sql/03_mart.sql) -> tabel mart_orders
"""

import sqlite3
from pathlib import Path
import pandas as pd


# Pemetaan nama berkas CSV ke nama tabel mentah
RAW_TABLE_MAP = {
    "olist_orders_dataset.csv": "raw_orders",
    "olist_order_items_dataset.csv": "raw_order_items",
    "olist_order_payments_dataset.csv": "raw_order_payments",
    "olist_order_reviews_dataset.csv": "raw_order_reviews",
    "olist_products_dataset.csv": "raw_products",
    "olist_sellers_dataset.csv": "raw_sellers",
    "olist_customers_dataset.csv": "raw_customers",
    "olist_geolocation_dataset.csv": "raw_geolocation",
    "product_category_name_translation.csv": "raw_category_translation",
}


def load_raw_tables(raw_dir: Path, db_path: Path) -> dict[str, int]:
    """
    Memuat 9 berkas CSV mentah ke dalam database SQLite sebagai tabel raw_*.
    Setiap baris dimuat apa adanya tanpa transformasi untuk menjaga audit trail.
    """
    raw_dir = Path(raw_dir)
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    counts = {}
    conn = sqlite3.connect(db_path)

    try:
        for csv_name, table_name in RAW_TABLE_MAP.items():
            csv_path = raw_dir / csv_name
            if not csv_path.exists():
                raise FileNotFoundError(f"Berkas CSV tidak ditemukan: {csv_path}")

            print(f"Memuat {csv_name} -> {table_name}...")
            # Chunksize untuk efisiensi memori (terutama geolocation >1 juta baris)
            chunks = pd.read_csv(csv_path, chunksize=50_000, low_memory=False)
            first_chunk = True
            for chunk in chunks:
                chunk.to_sql(
                    table_name,
                    conn,
                    if_exists="replace" if first_chunk else "append",
                    index=False,
                )
                first_chunk = False

            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            counts[table_name] = row_count
            print(f"  [OK] {table_name}: {row_count:,} baris.")

    finally:
        conn.close()

    return counts


def execute_sql_file(db_path: Path, sql_path: Path) -> None:
    """Mengeksekusi naskah SQL bertingkat pada database SQLite."""
    sql_path = Path(sql_path)
    db_path = Path(db_path)

    if not sql_path.exists():
        raise FileNotFoundError(f"Naskah SQL tidak ditemukan: {sql_path}")

    print(f"\nMengeksekusi skrip: {sql_path.name}...")
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()
        print(f"  [OK] Eksekusi {sql_path.name} selesai.")
    finally:
        conn.close()


def generate_reconciliation_report(db_path: Path) -> dict[str, int]:
    """Menghitung rekonsiliasi jumlah baris antar tingkat (raw, clean, mart)."""
    conn = sqlite3.connect(db_path)
    report = {}
    try:
        cursor = conn.cursor()
        queries = {
            "Raw Orders": "SELECT COUNT(*) FROM raw_orders",
            "Clean Orders": "SELECT COUNT(*) FROM clean_orders",
            "Mart Orders": "SELECT COUNT(*) FROM mart_orders",
            "Raw Order Items": "SELECT COUNT(*) FROM raw_order_items",
            "Clean Order Items": "SELECT COUNT(*) FROM clean_order_items",
            "Raw Order Reviews": "SELECT COUNT(*) FROM raw_order_reviews",
            "Clean Order Reviews": "SELECT COUNT(*) FROM clean_order_reviews",
            "Raw Customers": "SELECT COUNT(*) FROM raw_customers",
            "Clean Customers": "SELECT COUNT(*) FROM clean_customers",
            "Raw Sellers": "SELECT COUNT(*) FROM raw_sellers",
            "Clean Sellers": "SELECT COUNT(*) FROM clean_sellers",
        }
        for label, q in queries.items():
            cursor.execute(q)
            report[label] = cursor.fetchone()[0]
    finally:
        conn.close()
    return report


def build_full_pipeline(base_dir: Path) -> dict[str, int]:
    """Membangun seluruh lapisan data bertingkat dari raw sampai mart."""
    raw_dir = base_dir / "data" / "raw"
    db_file = base_dir / "data" / "processed" / "olist.db"
    sql_dir = base_dir / "sql"

    # 1. Raw
    print("=== TAHAP 1: MEMUAT DATA MENTAH (RAW) ===")
    load_raw_tables(raw_dir, db_file)

    # 2. Clean
    print("\n=== TAHAP 2: TRANSFORMASI DATA BERSIH (CLEAN) ===")
    execute_sql_file(db_file, sql_dir / "02_clean.sql")

    # 3. Mart
    print("\n=== TAHAP 3: MEMBANGUN MART TERINTEGRASI (MART) ===")
    execute_sql_file(db_file, sql_dir / "03_mart.sql")

    # 4. Rekonsiliasi
    print("\n=== LAPORAN REKONSILIASI ANTAR TINGKAT ===")
    recon = generate_reconciliation_report(db_file)
    for k, v in recon.items():
        print(f"  - {k:<25}: {v:>10,} baris")

    return recon


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent.parent
    build_full_pipeline(project_root)
