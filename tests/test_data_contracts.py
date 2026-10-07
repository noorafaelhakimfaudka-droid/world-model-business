"""
tests/test_data_contracts.py
Tes Otomatis 1: Kontrak Data & Kualitas Data (PRD §4.2 #1)
Memeriksa skema, kunci unik, urutan waktu, konsistensi baris,
dan ketiadaan nilai negatif mustahil pada lapisan data bertingkat.
"""

from pathlib import Path
import sqlite3
import pytest


@pytest.fixture(scope="module")
def db_conn():
    """Menyediakan koneksi ke database SQLite olist.db."""
    repo_root = Path(__file__).resolve().parent.parent
    db_path = repo_root / "data" / "processed" / "olist.db"
    assert db_path.exists(), f"Database {db_path} harus ada sebelum menjalankan tes."
    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()


def test_required_tables_exist(db_conn):
    """Memastikan semua tabel bertingkat (raw, clean, mart) tersedia."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")
    existing_tables = {row[0] for row in cursor.fetchall()}

    expected_tables = {
        "raw_orders",
        "raw_order_items",
        "raw_order_payments",
        "raw_order_reviews",
        "raw_products",
        "raw_sellers",
        "raw_customers",
        "clean_orders",
        "clean_order_items",
        "clean_order_payments",
        "clean_order_reviews",
        "clean_products",
        "clean_sellers",
        "clean_customers",
        "mart_orders",
    }
    missing = expected_tables - existing_tables
    assert not missing, f"Tabel berikut belum dibuat di database: {missing}"


def test_mart_orders_primary_key_unique(db_conn):
    """Memastikan order_id pada tabel mart_orders bersifat unik 100% (tidak ada duplikasi)."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*), COUNT(DISTINCT order_id) FROM mart_orders")
    total_rows, unique_orders = cursor.fetchone()
    assert total_rows == unique_orders, f"Ada duplikasi order_id: {total_rows} baris vs {unique_orders} unik."


def test_mart_reconciliation_with_clean_orders(db_conn):
    """Memastikan jumlah pesanan di mart_orders sama persis dengan clean_orders (tidak ada yang hilang)."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clean_orders")
    clean_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM mart_orders")
    mart_count = cursor.fetchone()[0]
    assert mart_count == clean_count, f"Selisih baris antara clean ({clean_count}) dan mart ({mart_count})."


def test_temporal_consistency_no_traveling_backwards(db_conn):
    """Memastikan tidak ada pesanan di mana barang sampai sebelum tanggal pembelian."""
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM mart_orders 
        WHERE order_delivered_customer_date < order_purchase_timestamp
    """)
    anomalies = cursor.fetchone()[0]
    assert anomalies == 0, f"Ditemukan {anomalies} pesanan dengan tanggal tiba mendahului tanggal beli."


def test_no_impossible_negative_values(db_conn):
    """Memastikan tidak ada nilai harga, ongkir, kuantitas, atau pembayaran bernilai negatif."""
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM mart_orders 
        WHERE total_items_value < 0 
           OR total_freight_value < 0 
           OR total_payment_value < 0 
           OR item_count < 0
    """)
    negatives = cursor.fetchone()[0]
    assert negatives == 0, f"Ditemukan {negatives} pesanan dengan nilai negatif yang mustahil."


def test_review_score_domain(db_conn):
    """Memastikan skor review hanya berada dalam domain 1 sampai 5 (atau NULL jika belum direview)."""
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM mart_orders 
        WHERE min_review_score IS NOT NULL 
          AND (min_review_score < 1 OR min_review_score > 5)
    """)
    invalid_scores = cursor.fetchone()[0]
    assert invalid_scores == 0, f"Ditemukan {invalid_scores} skor review di luar rentang 1-5."


def test_is_late_flag_values(db_conn):
    """Memastikan flag is_late hanya bernilai 0, 1, atau NULL."""
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM mart_orders 
        WHERE is_late IS NOT NULL AND is_late NOT IN (0, 1)
    """)
    invalid_flags = cursor.fetchone()[0]
    assert invalid_flags == 0, f"Ditemukan {invalid_flags} nilai flag is_late yang tidak valid."
