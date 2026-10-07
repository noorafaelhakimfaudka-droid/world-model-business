import pandas as pd
import numpy as np
from pathlib import Path
import sqlite3

def build_features(dev_orders_path='data/processed/dev_orders.parquet', output_dir='data/processed'):
    print("Memuat dev_orders...")
    df = pd.read_parquet(dev_orders_path)
    
    # Pastikan datetime
    for col in ['order_purchase_timestamp', 'order_delivered_customer_date']:
        df[col] = pd.to_datetime(df[col])
        
    df = df.sort_values('order_purchase_timestamp').reset_index(drop=True)
    
    print("Menghitung fitur as-of (seller history)... ini mungkin butuh waktu belasan detik.")
    # Untuk mempercepat, kita kumpulkan histori seller yang SUDAH SELESAI
    # Di Pandas, ini bisa dilakukan dengan window/rolling atau iterasi teroptimasi.
    
    # Kita butuh: untuk setiap pesanan, cari pesanan seller yang sama di masa lalu 
    # di mana order_delivered_customer_date < current order_purchase_timestamp
    # dan selisihnya <= 30 hari.
    
    # Cara efisien: Buat tabel terpisah dari kejadian selesai, lalu hitung rolling.
    # Namun karena waktu pengiriman bervariasi, order_purchase_timestamp bisa terjadi
    # SEBELUM order masa lalu selesai. Ini jebakan as-of klasik.
    # Kita pakai brute force sederhana pakai list comprehension atau apply jika lambat.
    
    # Buat dictionary histori untuk setiap seller: list of tuples (delivered_date, is_late, score)
    # yang diurutkan berdasar delivered_date
    seller_hist = {}
    for idx, row in df.dropna(subset=['order_delivered_customer_date']).iterrows():
        sid = row['primary_seller_id']
        if sid not in seller_hist:
            seller_hist[sid] = []
        seller_hist[sid].append((
            row['order_delivered_customer_date'], 
            row['is_late'], 
            row['min_review_score'] if pd.notna(row['min_review_score']) else 3.0
        ))
    
    # Urutkan histori tiap seller berdasarkan tanggal selesai
    for sid in seller_hist:
        seller_hist[sid].sort(key=lambda x: x[0])
        
    late_rate_30d = []
    avg_score_30d = []
    
    for idx, row in df.iterrows():
        sid = row['primary_seller_id']
        purch_date = row['order_purchase_timestamp']
        
        hist = seller_hist.get(sid, [])
        # Ambil yang sudah selesai SEBELUM purch_date, dan selesai dalam 30 hari terakhir
        cutoff = purch_date - pd.Timedelta(days=30)
        
        valid_past = [x for x in hist if x[0] < purch_date and x[0] >= cutoff]
        
        if len(valid_past) > 0:
            lates = [x[1] for x in valid_past]
            scores = [x[2] for x in valid_past]
            late_rate_30d.append(np.mean(lates))
            avg_score_30d.append(np.mean(scores))
        else:
            late_rate_30d.append(np.nan)  # Tidak ada histori
            avg_score_30d.append(np.nan)
            
    df['seller_recent_late_rate_30d'] = late_rate_30d
    df['seller_recent_avg_score_30d'] = avg_score_30d
    
    # Isi NaN dengan nilai rata-rata global jika seller baru
    df['seller_recent_late_rate_30d'].fillna(df['is_late'].mean(), inplace=True)
    df['seller_recent_avg_score_30d'].fillna(df['avg_review_score'].mean(), inplace=True)
    
    # Fitur Dasar T0
    df['purchase_month'] = df['order_purchase_timestamp'].dt.month
    df['purchase_dayofweek'] = df['order_purchase_timestamp'].dt.dayofweek
    
    t0_cols = [
        'order_id', 'order_purchase_timestamp', 'primary_category',
        'total_items_value', 'total_freight_value', 'estimated_delivery_days',
        'avg_product_weight_g', 'purchase_month', 'purchase_dayofweek',
        'seller_recent_late_rate_30d', 'seller_recent_avg_score_30d',
        'is_late', 'is_bad_review' # Targets
    ]
    
    t1_cols = t0_cols + ['seller_handling_days']
    t2_cols = t1_cols + ['actual_delivery_days', 'carrier_transit_days']
    
    df_t0 = df[t0_cols]
    df_t1 = df[t1_cols].dropna(subset=['seller_handling_days'])
    df_t2 = df[t2_cols].dropna(subset=['actual_delivery_days'])
    
    out_dir = Path(output_dir)
    out_dir.mkdir(exist_ok=True, parents=True)
    
    df_t0.to_parquet(out_dir / 'features_t0.parquet', index=False)
    df_t1.to_parquet(out_dir / 'features_t1.parquet', index=False)
    df_t2.to_parquet(out_dir / 'features_t2.parquet', index=False)
    print("Berhasil menyimpan features_t0.parquet, features_t1.parquet, features_t2.parquet")

if __name__ == "__main__":
    build_features()
