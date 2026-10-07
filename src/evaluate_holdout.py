import pandas as pd
import numpy as np
import json
import sys
import datetime
from pathlib import Path
import argparse
import os

# Fix path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

# Untuk memuat pipeline yang sudah didefinisikan di modul
from src.models.classification import build_classification_pipeline, evaluate_top_k
from src.features.build_features import build_features

def prepare_real_holdout_features():
    print("Menyiapkan fitur holdout. Menggabungkan dev dan holdout untuk histori seller as-of...")
    df_dev = pd.read_parquet('data/processed/dev_orders.parquet')
    df_holdout = pd.read_parquet('data/processed/holdout_orders.parquet')
    df_combined = pd.concat([df_dev, df_holdout], ignore_index=True)
    
    tmp_path = Path('data/processed/temp_combined.parquet')
    df_combined.to_parquet(tmp_path, index=False)
    
    out_dir = Path('data/processed/holdout_feat')
    out_dir.mkdir(exist_ok=True)
    
    # Run build_features pipeline
    build_features(str(tmp_path), str(out_dir))
    
    # Hapus temp file
    if tmp_path.exists():
        tmp_path.unlink()
        
    return out_dir / 'features_t0.parquet'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--real', action='store_true', help="Jalankan di holdout sungguhan")
    args = parser.parse_args()

    holdout_flag = Path("experiments/holdout_opened.json")
    if holdout_flag.exists():
        print("[FATAL] Holdout sudah pernah dibuka sebelumnya! Menghentikan eksekusi demi menjaga Sumpah Data Scientist.")
        with open(holdout_flag, 'r') as f:
            print(f.read())
        return

    # Latih model selalu dari DEV T0 Asli
    print("Memuat data latih (dev)...")
    df_t0_dev = pd.read_parquet('data/processed/features_t0.parquet')
    # Train di semua data DEV yang tidak punya target bolong
    df_train = df_t0_dev.dropna(subset=['is_bad_review', 'is_late'])
    
    cat_cols = ['primary_category']
    num_cols = ['total_items_value', 'total_freight_value', 'estimated_delivery_days', 'avg_product_weight_g', 'seller_recent_late_rate_30d', 'seller_recent_avg_score_30d']
    
    X_train, y_train = df_train[cat_cols + num_cols], df_train['is_late']
    
    print("Melatih ulang model Random Forest (Beku G6) pada seluruh dev set...")
    model = build_classification_pipeline(cat_cols, num_cols, 'rf')
    model.fit(X_train, y_train)

    if not args.real:
        print("\n[DRY-RUN MODE] Validasi pada data test (Maret-Agustus 2018 di Dev Set)")
        df_test = df_t0_dev[df_t0_dev['order_purchase_timestamp'] >= '2018-04-01'].copy()
        df_test = df_test.dropna(subset=['is_bad_review', 'is_late'])
        X_test, y_test = df_test[cat_cols + num_cols], df_test['is_late']
        
        probs_ai = model.predict_proba(X_test)[:, 1]
        probs_aturan = (X_test['seller_recent_late_rate_30d'] * X_test['estimated_delivery_days']).fillna(0)
        
        p_ai, r_ai, auc_ai = evaluate_top_k(y_test, probs_ai, k_fraction=0.10)
        p_aturan, r_aturan, auc_aturan = evaluate_top_k(y_test, probs_aturan, k_fraction=0.10)
        
        print(f"Model AI         -> Top-10% Precision: {p_ai:.3f}, PR-AUC: {auc_ai:.3f}")
        print(f"Aturan Sederhana -> Top-10% Precision: {p_aturan:.3f}, PR-AUC: {auc_aturan:.3f}")
        print("\n[OK] DRY-RUN BERHASIL. Skrip siap. Gunakan --real saat diinstruksikan BUKA.")
        return

    # JIKA MODE REAL
    print("\n=============================================")
    print("!!! MENGHANCURKAN SEGEL SHA-256 HOLDOUT !!!")
    print("=============================================")
    
    feat_path = prepare_real_holdout_features()
    df_holdout_full = pd.read_parquet(feat_path)
    # Filter hanya data Juli - Agustus 2018
    df_holdout = df_holdout_full[df_holdout_full['order_purchase_timestamp'] >= '2018-07-01'].copy()
    df_holdout = df_holdout.dropna(subset=['is_bad_review', 'is_late'])
    
    X_holdout, y_holdout = df_holdout[cat_cols + num_cols], df_holdout['is_late']
    
    probs_ai = model.predict_proba(X_holdout)[:, 1]
    probs_aturan = (X_holdout['seller_recent_late_rate_30d'] * X_holdout['estimated_delivery_days']).fillna(0)
    
    p_ai, r_ai, auc_ai = evaluate_top_k(y_holdout, probs_ai, k_fraction=0.10)
    p_aturan, r_aturan, auc_aturan = evaluate_top_k(y_holdout, probs_aturan, k_fraction=0.10)
    
    print("\n--- HASIL HARI PENGHAKIMAN (HOLDOUT) ---")
    print(f"Model AI         -> Top-10% Precision: {p_ai:.3f}, PR-AUC: {auc_ai:.3f}")
    print(f"Aturan Sederhana -> Top-10% Precision: {p_aturan:.3f}, PR-AUC: {auc_aturan:.3f}")
    
    # Rekam hasil ke JSON agar tidak bisa dibuka lagi
    results = {
        "opened_at": datetime.datetime.now().isoformat(),
        "model_ai": {"top_10_precision": float(p_ai), "pr_auc": float(auc_ai)},
        "baseline_aturan": {"top_10_precision": float(p_aturan), "pr_auc": float(auc_aturan)},
        "pesan_sumpah": "Holdout telah dibuka satu kali. Angka ini mutlak dan final."
    }
    with open(holdout_flag, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[SELESAI] Hasil direkam secara permanen di {holdout_flag}")

if __name__ == "__main__":
    main()
