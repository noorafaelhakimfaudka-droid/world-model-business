import pandas as pd
import numpy as np
import scipy.stats as stats

def calculate_bad_review_cost(df_orders):
    """
    Menghitung kerugian uang (dalam R$) akibat satu ulasan buruk.
    Metodologi: 
    1. Cari pelanggan yang belanja lebih dari 1 kali.
    2. Cek apakah ulasan buruk di pesanan pertama menurunkan peluang belanja lagi.
    3. Kalikan penurunan peluang dengan rata-rata nilai pesanan masa depan.
    """
    # Hanya melihat pelanggan dengan order pertama (simulasi sederhana)
    # Karena Olist repeat ratenya sangat kecil (~3%), angkanya mungkin bising.
    # Namun kita tetap laporkan secara jujur.
    
    # Kelompokkan berdasar customer_unique_id
    customer_stats = df_orders.groupby('customer_unique_id').agg(
        total_orders=('order_id', 'count'),
        first_order_score=('min_review_score', 'first'),
        first_order_value=('total_items_value', 'first')
    ).reset_index()
    
    customer_stats['is_repeat'] = (customer_stats['total_orders'] > 1).astype(int)
    customer_stats['is_first_bad'] = (customer_stats['first_order_score'] <= 2).astype(int)
    
    # Peluang kembali
    repeat_rate_good = customer_stats[customer_stats['is_first_bad'] == 0]['is_repeat'].mean()
    repeat_rate_bad = customer_stats[customer_stats['is_first_bad'] == 1]['is_repeat'].mean()
    
    drop_in_repeat_prob = repeat_rate_good - repeat_rate_bad
    
    # Jika drop negatif (orang marah malah balik lagi), set ke 0
    drop_in_repeat_prob = max(0, drop_in_repeat_prob)
    
    avg_future_value = customer_stats['first_order_value'].mean() # Asumsi belanja berikutnya sama
    
    cost_per_bad_review = drop_in_repeat_prob * avg_future_value
    
    return cost_per_bad_review, repeat_rate_good, repeat_rate_bad, avg_future_value


def calculate_sample_size(baseline_rate, target_rate, alpha=0.05, power=0.80):
    """
    Menghitung ukuran sampel minimum per kelompok untuk A/B testing
    menggunakan rumus Z-test proportions.
    """
    z_alpha = stats.norm.ppf(1 - alpha/2)
    z_beta = stats.norm.ppf(power)
    
    p1 = baseline_rate
    p2 = target_rate
    p = (p1 + p2) / 2
    
    # Rumus ukuran sampel untuk dua proporsi
    n = ((z_alpha * np.sqrt(2 * p * (1 - p)) + z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / ((p1 - p2) ** 2)
    
    return int(np.ceil(n))
