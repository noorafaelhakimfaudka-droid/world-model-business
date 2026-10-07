# Laporan Kualitas Data & Rekonsiliasi Antar Tingkat
**Langkah 1: Lapisan Data dan Cek Kualitas**  
*Mengacu pada PRD §4.1 dan PRD §5 (Langkah 1) — Evaluasi Gerbang G1*

---

## 1. Rekonsiliasi Jumlah Baris Antar Tingkat (Row Reconciliation)

Berikut adalah rekonsiliasi jumlah baris aktual dari data mentah CSV, lapisan bersih (*clean*), hingga tabel analisis (*mart*):

| Entitas Data | Raw Layer (CSV Mentah) | Clean Layer (Data Bersih) | Mart Layer (`mart_orders`) | Selisih / Baris Dibuang | Keterangan & Tindakan |
|---|---|---|---|---|---|
| **Orders** | 99.441 baris | 99.433 baris | 99.433 baris | -8 baris (-0,008%) | 8 baris berstatus *delivered* tetapi `order_delivered_customer_date` bernilai NULL dibuang. Pelanggaran 0,008% (jauh di bawah batas toleransi 0,5%). |
| **Order Items** | 112.650 baris | 112.650 baris | Teragregasi ke 99.433 pesanan | 0 baris (0,0%) | 100% item terhubung dan teragregasi secara tepat. Rata-rata 1,13 item per pesanan. |
| **Order Payments** | 103.886 baris | 103.886 baris | Teragregasi ke 99.433 pesanan | 0 baris (0,0%) | 100% pembayaran terhubung. Mencakup pembayaran multi-metode/cicilan. |
| **Order Reviews** | 99.224 baris | 99.224 baris | Teragregasi ke 99.433 pesanan | 0 baris (0,0%) | 100% ulasan terhubung. Pesanan tanpa ulasan bernilai NULL secara wajar. |
| **Customers** | 99.441 baris | 99.441 baris | Terhubung via `customer_id` | 0 baris (0,0%) | 100% referensi pelanggan valid. |
| **Sellers** | 3.095 baris | 3.095 baris | Terhubung via `primary_seller_id` | 0 baris (0,0%) | 100% profil seller valid. |
| **Products** | 32.951 baris | 32.951 baris | Kategori diterjemahkan ke Inggris | 0 baris (0,0%) | Nama kolom typo diperbaiki (`lenght` -> `length`). |

---

## 2. Temuan Audit Kualitas Data

### A. Integritas Pembayaran vs Nilai Belanja (Items + Freight)
- **Total Pesanan Tercocokkan**: 98.665 pesanan (yang memiliki item dan pembayaran tercatat).
- **Kecocokan Persis (Selisih < R$ 0,01)**: 98.285 pesanan (**99,61%**).
- **Selisih Kecil (R$ 0,01 s.d. R$ 1,00)**: 131 pesanan (**0,13%**), disebabkan oleh pembulatan sen pada sistem cicilan/voucher.
- **Selisih Signifikan (> R$ 1,00)**: 249 pesanan (**0,25%**).
- **Kesimpulan**: Pelanggaran 0,25% berada jauh di bawah ambang batas toleransi PRD (0,5%). Data dipertahankan dengan nilai transaksi asli.

### B. Urutan Waktu Transaksi (Temporal Consistency)
- Cek anomali: `order_delivered_customer_date < order_purchase_timestamp` = **0 baris** (tidak ada paket yang sampai sebelum dibeli).
- Cek penyerahan kurir: `order_delivered_carrier_date < order_purchase_timestamp` = **0 baris**.
- Urutan waktu 100% masuk akal: Beli $\le$ Disetujui $\le$ Serah Kurir $\le$ Tiba di Pelanggan.

### C. Penetapan Jendela Waktu Analisis (Analysis Window)
- **Periode Awal (Sep–Des 2016)**: Hanya ada 329 pesanan, dan bulan November 2016 kosong total (0 pesanan).
- **Periode Akhir (Sep–Okt 2018)**: Data terpotong tiba-tiba (September 2018 = 16 pesanan, Oktober 2018 = 4 pesanan).
- **Keputusan Jendela Stabil**: Data yang digunakan untuk pemodelan deret waktu dan analisis utama dikunci pada rentang **1 Januari 2017 s.d. 31 Agustus 2018** (20 bulan penuh, 97.432 pesanan stabil).

### D. Angka Kunci Karakteristik Bisnis Aktual (Tabel Fakta Olist)
- **Tingkat Pembelian Ulang Riil**: **3,12%** (2.997 dari 96.096 pelanggan unik melakukan transaksi ulang). Asumsi PRD sebelumnya $\approx 3,4\%$.
- **Tingkat Keterlambatan Riil**: **8,11%** (7.826 dari 96.470 pesanan berstatus *delivered* yang memiliki tanggal terima).
- **Tingkat Ulasan Buruk (Bintang 1–2)**: **14,69%** (14.575 dari 99.224 ulasan).
- **Tingkat Ketersediaan Pesan Teks Ulasan**: **41,30%** (40.977 ulasan memiliki teks komentar).

---

## 3. Keputusan Gerbang G1

- **Status Gerbang G1**: **LULUS (PASS)**.
- **Tindakan**:
  1. 8 baris anomali dibuang pada lapisan `clean_orders` dan dicatat resmi.
  2. Jendela analisis deret waktu dikunci: Januari 2017 – Agustus 2018.
  3. Skrip SQL bertingkat (`sql/01_raw.sql`, `sql/02_clean.sql`, `sql/03_mart.sql`) berjalan otomatis melalui `src/data/build_database.py`.
