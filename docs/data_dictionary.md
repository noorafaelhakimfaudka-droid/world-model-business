# Kamus Data (Data Dictionary) — Mart Orders
*Mengacu pada PRD §3.2, PRD §4.1, dan PRD §5 (Langkah 1 & 4)*

Tabel utama analisis: `mart_orders` di dalam database `data/processed/olist.db`.
Setiap baris merepresentasikan **satu pesanan unik** (*grain: order_id*).

---

## 1. Tabel Definisi Kolom & Tanggal Ketersediaan

| Nama Kolom | Tipe Data SQLite | Arti Bisnis | Tanggal Ketersediaan (Point-in-Time) | Boleh Dipakai di Titik Prediksi? |
|---|---|---|---|---|
| `order_id` | TEXT | ID unik transaksi pesanan | Saat Checkout (T0) | Identifier |
| `customer_id` | TEXT | ID unik sesi/akun pesanan pembeli | Saat Checkout (T0) | Identifier |
| `customer_unique_id` | TEXT | ID identitas asli pelanggan di seluruh riwayat transaksi | Saat Checkout (T0) | Lookup riwayat masa lalu (As-of) |
| `customer_zip_code_prefix` | INTEGER | 5 digit awal kode pos pembeli | Saat Checkout (T0) | T0, T1, T2 |
| `customer_city` | TEXT | Kota domisili pembeli | Saat Checkout (T0) | T0, T1, T2 |
| `customer_state` | TEXT | Kode negara bagian pembeli (misal: SP, RJ) | Saat Checkout (T0) | T0, T1, T2 |
| `order_status` | TEXT | Status akhir pesanan (delivered, shipped, canceled) | Berubah dinamis | Label / Filter |
| `order_purchase_timestamp` | TIMESTAMP | Waktu pelanggan menyelesaikan pembayaran/checkout | Saat Checkout (T0) | Anchor waktu prediksi |
| `order_approved_at` | TIMESTAMP | Waktu pembayaran disetujui sistem gateway | Pasca Checkout (T0+) | T1, T2 |
| `order_delivered_carrier_date`| TIMESTAMP | Waktu seller menyerahkan paket ke pihak logistik | Saat Penyerahan Kurir (T1) | T1, T2 |
| `order_delivered_customer_date`| TIMESTAMP | Waktu riil paket diterima oleh pembeli | Saat Barang Tiba (T2) | Target Keterlambatan / T2 saja |
| `order_estimated_delivery_date`| TIMESTAMP | Tanggal estimasi tiba yang dijanjikan ke pembeli | Saat Checkout (T0) | T0, T1, T2 |
| `actual_delivery_days` | REAL | Total hari riil pengiriman (tiba - beli) | Saat Barang Tiba (T2) | Target / Post-purchase (Dilarang di T0 & T1!) |
| `estimated_delivery_days` | REAL | Total hari estimasi pengiriman yang dijanjikan | Saat Checkout (T0) | T0, T1, T2 |
| `seller_handling_days` | REAL | Durasi seller memproses pesanan (serah kurir - beli) | Saat Penyerahan Kurir (T1) | T1, T2 (Dilarang di T0!) |
| `carrier_transit_days` | REAL | Durasi kurir mengantar paket (tiba - serah kurir) | Saat Barang Tiba (T2) | Target / Post-transit (Dilarang di T0 & T1!) |
| `is_late` | INTEGER | Flag pesanan terlambat (1 jika tiba > estimasi, 0 jika tepat waktu) | Saat Barang Tiba (T2) | **TARGET PREDIKSI LANGKAH 6** |
| `item_count` | INTEGER | Jumlah total barang fisik dalam 1 pesanan | Saat Checkout (T0) | T0, T1, T2 |
| `total_items_value` | REAL | Total nilai harga barang (BRL / R$) | Saat Checkout (T0) | T0, T1, T2 |
| `total_freight_value` | REAL | Total biaya ongkos kirim (BRL / R$) | Saat Checkout (T0) | T0, T1, T2 |
| `unique_sellers_count` | INTEGER | Jumlah seller berbeda yang terlibat dalam pesanan | Saat Checkout (T0) | T0, T1, T2 |
| `primary_seller_id` | TEXT | ID seller utama yang melayani pesanan | Saat Checkout (T0) | Fitur seller as-of |
| `seller_city` | TEXT | Kota asal seller | Saat Checkout (T0) | T0, T1, T2 |
| `seller_state` | TEXT | Negara bagian seller (SP, PR, RJ, dll.) | Saat Checkout (T0) | T0, T1, T2 |
| `primary_category` | TEXT | Kategori produk utama (bahasa Inggris) | Saat Checkout (T0) | T0, T1, T2 |
| `avg_product_weight_g` | REAL | Rata-rata berat produk dalam pesanan (gram) | Saat Checkout (T0) | T0, T1, T2 |
| `total_payment_value` | REAL | Total nilai nominal pembayaran pelanggan | Saat Checkout (T0) | T0, T1, T2 |
| `max_installments` | INTEGER | Jumlah cicilan pembayaran tertinggi | Saat Checkout (T0) | T0, T1, T2 |
| `primary_payment_type` | TEXT | Metode pembayaran utama (credit_card, boleto, voucher, debit_card) | Saat Checkout (T0) | T0, T1, T2 |
| `min_review_score` | INTEGER | Skor bintang review terendah yang diberikan (1–5) | Pasca Pengiriman (T2+) | **TARGET PREDIKSI LANGKAH 7** |
| `avg_review_score` | REAL | Rata-rata skor bintang review pelanggan | Pasca Pengiriman (T2+) | Evaluasi kepuasan |
| `is_bad_review` | INTEGER | Flag ulasan buruk (1 jika bintang 1–2, 0 jika 3–5) | Pasca Pengiriman (T2+) | **TARGET PREDIKSI LANGKAH 7** |
| `has_review_text` | INTEGER | Flag apakah ulasan menyertakan pesan teks (1/0) | Pasca Pengiriman (T2+) | Evaluasi NLP |
| `review_comment_message` | TEXT | Isi komentar teks ulasan dari pelanggan (Portugis) | Pasca Pengiriman (T2+) | Bahan NLP Langkah 7 |

---

## 2. Aturan Pencegahan Kebocoran (Leakage Rules)

1. **Prediksi Keterlambatan di T0 (Saat Checkout)**:
   - DILARANG menggunakan: `order_delivered_carrier_date`, `seller_handling_days`, `order_delivered_customer_date`, `actual_delivery_days`, `carrier_transit_days`, dan seluruh kolom ulasan (`review_*`).
2. **Prediksi Keterlambatan di T1 (Saat Barang Diserahkan Kurir)**:
   - BOLEH menggunakan: `order_delivered_carrier_date` dan `seller_handling_days`.
   - DILARANG menggunakan: `order_delivered_customer_date`, `actual_delivery_days`, `carrier_transit_days`, dan seluruh kolom ulasan.
3. **Prediksi Ulasan Buruk di T2 (Saat Barang Tiba)**:
   - BOLEH menggunakan seluruh informasi riwayat pengiriman aktual (`actual_delivery_days`, `is_late`).
   - DILARANG menggunakan: teks ulasan atau skor ulasan dari pesanan yang sedang diprediksi.
