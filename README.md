# Janji: World Model for Business (Edisi Olist)

> **"Jangan perbaiki kurirnya dulu. Uji janjinya."**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests: Pytest Passing](https://img.shields.io/badge/tests-13%20passed-brightgreen.svg)](https://pytest.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistem Pendukung Keputusan (*Decision Support System* / DSS) komprehensif yang mengintegrasikan **Machine Learning**, **Inferensi Kausal (Propensity Score Matching)**, dan **Simulasi Kontrafaktual Stokastik (World Model)** pada 99.084 transaksi nyata e-commerce Olist (Brasil).

Alih-alih sekadar mengejar skor akurasi model di ruang hampa, proyek ini dibangun dari sudut pandang strategi kepemimpinan eksekutif: **Bagaimana data science dapat memitigasi risiko keputusan operasional bernilai ratusan ribu Real sebelum modal fisik digelontorkan?**

---

## 1. Ringkasan Eksekutif dan Temuan Kunci

| Temuan Strategis | Metodologi | Dampak Bisnis Nyata |
|---|---|---|
| **1. Dampak Kausal Keterlambatan Pengiriman** | Propensity Score Matching (PSM) dengan Caliper 0,05 + Uji Plasebo | Keterlambatan terbukti secara kausal langsung memotong **1,71★** kepuasan konsumen (p < 0,001). Ini bukan kebetulan akibat rute jauh atau barang berat. |
| **2. Efek Psikologis Janji (The Underpromise Effect)** | Simulasi Kebijakan Kontrafaktual (World Model Blok 1–3) | Menambahkan **+3 hari buffer SLA** pada estimasi tiba di website mencegah **~2.608 ulasan buruk** pada **Capex logistik R$ 0**, mengalahkan program percepatan kurir fisik. |
| **3. Deteksi Dini Risiko Keterlambatan** | Point-in-Time As-Of Random Forest pada titik T0 & T1 | Mendeteksi pesanan berisiko tinggi dengan **presisi 8,0%** di T0 (vs baseline heuristik 4,4% = **1,8x lift**), menjadi dasar pemantauan terarah tanpa memboroskan anggaran kompensasi. |
| **4. Valuasi Nilai Retensi dan ROI Bisnis** | Pemodelan Perilaku Belanja Ulang dan CLV | Mengingat hanya 3,07% pembeli yang berbelanja ulang di Olist, perlindungan pesanan pertama sangat krusial. Setiap ulasan buruk yang dicegah mempertahankan nilai retensi **R$ 14,06 hingga R$ 92,00**. |

---

## 2. Aplikasi Pendukung Keputusan (Streamlit DSS)

Aplikasi dasbor interaktif produksi siap pakai disertakan untuk presentasi eksekutif dan eksplorasi skenario langsung:

```bash
# Menjalankan aplikasi web secara lokal
streamlit run streamlit_app.py
```

### Fitur Utama Antarmuka:
1. **Dasbor KPI Eksekutif & 10 Temuan Bisnis**: Konsentrasi volume Pareto, ketimpangan geografis (São Paulo 8 hari vs Roraima 29 hari), dan fenomena tebing kepuasan (rating anjlok dari 4,3★ ke 2,4★ saat paket telat).
2. **Segmentasi Pelanggan (RFM) & Diagnosis Penjual**: Profil 73,8% pembeli satu kali transaksi dan diagnosis 6% penjual kritis penyumbang 34% keterlambatan.
3. **Peramalan Permintaan Operasional**: Prediksi deret waktu mingguan 4 pekan ke depan per kategori produk (WAPE = 13,6%).
4. **Sistem Peringatan Dini Keterlambatan**: Skoring risiko pesanan saat checkout (T0) dan saat diserahkan ke kurir (T1) dengan meteran 3 zona aksi.
5. **Laboratorium Kausalitas (PSM Lab)**: Visualisasi pasangan kembar identik (*matched twins*) pembuktian kausal ATE −1,71★ dan kontrol mutu plasebo R$ 0,00.
6. **World Model Simulator (Operational Reality Lab)**: Kokpit kebijakan makro dengan pergeseran gelombang SLA dinamis, neraca keuangan P&L kebijakan, uji stres toleransi pembatalan checkout, dan inspektur mikrosimulasi 4 kasus pesanan nyata.
7. **Kalkulator Titik Impas Voucher CS & Protokol A/B Testing**: Perhitungan sensitivitas kompensasi dan penentuan ukuran sampel uji coba lapangan (~1.560 pesanan per kelompok).

---

## 3. Kerangka Arsitektur Sistem

```
                          ┌──────────────────────────────────────────────┐
                          │         DATA MENTAH (9 TABEL CSV OLIST)      │
                          └──────────────────────┬───────────────────────┘
                                                 ▼
                          ┌──────────────────────────────────────────────┐
                          │         SQL DATA MART (SQLite OLAP)          │
                          │   01_raw.sql -> 02_clean.sql -> 03_mart.sql  │
                          └──────────────────────┬───────────────────────┘
                                                 ▼
             ┌───────────────────────────────────┴───────────────────────────────────┐
             ▼                                                                       ▼
┌─────────────────────────┐                                             ┌─────────────────────────┐
│    DATA PENGEMBANGAN    │                                             │   DATA UJI TERKUNCI     │
│ 86.283 Pesanan (Latih)  │                                             │ 12.801 Pesanan (Holdout)│
└────────────┬────────────┘                                             │ Segel SHA-256 Terverifikasi
             │                                                          └─────────────────────────┘
             ├───────────────────────────────────────────────────────────────────────┐
             ▼                                                                       ▼
┌─────────────────────────┐                                             ┌─────────────────────────┐
│  FITUR POINT-IN-TIME    │                                             │   INFERENSI KAUSALITAS  │
│  T0: Saat Checkout Saja │                                             │   Pencocokan Kembar PSM │
│  T1: Saat Serah Kurir   │                                             │   ATE = -1,71 Bintang   │
│  T2: Pasca Pengiriman   │                                             │   Uji Plasebo: R$ 0,00  │
└────────────┬────────────┘                                             └────────────┬────────────┘
             │                                                                       │
             ▼                                                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        SIMULATOR STOKASTIK WORLD MODEL                                 │
│   Intervensi Kebijakan -> Blok 1: Risiko Telat -> Blok 2: Risiko Rating -> Blok 3: CLV │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Pagar Pembatas Metodologi dan Integritas Rekayasa

- **Nol Kebocoran Masa Depan (Zero Future Leakage)**: Seluruh rekayasa fitur diisolasi secara ketat berdasarkan stempel waktu ketersediaan informasi (*as-of timestamp*). Fitur di titik T0 tidak mengandung satu pun kolom yang baru tercipta pasca-checkout.
- **Pemisahan Berurutan Waktu (Chronological Split)**: Tidak ada pengacakan data sembarangan (*random split*) pada data deret waktu. Data dilatih pada masa lalu dan diuji pada masa depan dengan jeda pengaman (*buffer window*).
- **Segel Kriptografi Data Uji**: Sebanyak 12.801 pesanan dipisahkan dan disegel dengan hash kriptografi SHA-256 (`dfa121510c806f39cf24b894ae470a7e512af2a987c5ba7cf40dd871dd3ff84e`) dan tidak pernah disentuh selama pelatihan model.
- **Disiplin Angka Anti-Halusinasi**: Setiap angka yang dilaporkan berasal murni dari eksekusi kode nyata dengan verifikasi ganda (rekonsiliasi SQL dan pandas).

---

## 5. Peta Repositori dan Alur Analisis

| Berkas Analisis | Fokus Bahasan | Metode dan Model Utama | Luaran Utama |
|---|---|---|---|
| [`notebooks/01_business_eda.ipynb`](notebooks/01_business_eda.ipynb) | Eksplorasi Data Bisnis | Statistik Deskriptif, Geocoding | 10 Wawasan Inti Bisnis Olist |
| [`notebooks/02_clustering.ipynb`](notebooks/02_clustering.ipynb) | Segmentasi Entitas | K-Means RFM, Pemetaan Seller | Profil Pembeli dan 6% Seller Kritis |
| [`notebooks/03_forecasting.ipynb`](notebooks/03_forecasting.ipynb) | Peramalan Permintaan | Moving Average, Ridge, Exponential Smoothing | WAPE = 13,6% (Skala Mingguan) |
| [`notebooks/04_predict_late.ipynb`](notebooks/04_predict_late.ipynb) | Deteksi Dini Keterlambatan | Random Forest, Top-K Precision Lift | Presisi T0 = 8,0% (1,8x Baseline) |
| [`notebooks/05_predict_reviews.ipynb`](notebooks/05_predict_reviews.ipynb) | Sentimen & Ulasan Pelanggan | TF-IDF, N-Grams, Logistic Regression | PR-AUC = 0,38, Akar Masalah Komplain |
| [`notebooks/06_causal_impact.ipynb`](notebooks/06_causal_impact.ipynb) | Inferensi Kausalitas | Propensity Score Matching (PSM) | ATE = −1,71★ (Bukti Sebab-Akibat) |
| [`notebooks/07_world_model.ipynb`](notebooks/07_world_model.ipynb) | Mesin Simulasi Sistem | Rantai Blok Probabilistik Terhubung | Lolos Uji Validasi U1–U3 |
| [`notebooks/08_scenarios.ipynb`](notebooks/08_scenarios.ipynb) | Analisis Skenario Kebijakan | Evaluasi Kebijakan S1, S2, S3 | Bukti Buffer SLA Kalahkan Capex Kurir |
| [`notebooks/09_business_value.ipynb`](notebooks/09_business_value.ipynb) | Valuasi ROI dan Eksperimen | Atribusi CLV, Analisis Power A/B | Desain A/B Testing (N=1.560/kelompok) |

---

## 6. Panduan Instalasi dan Pengujian Cepat

### 1. Prasyarat dan Penyiapan Lingkungan
```bash
# Klon repositori
git clone https://github.com/username-anda/world-model-business.git
cd world-model-business

# Buat dan aktifkan lingkungan virtual
python -m venv .venv
source .venv/bin/activate  # Pada Windows: .venv\Scripts\activate

# Pasang dependensi
pip install -r requirements.txt
```

### 2. Jalankan Pengujian Otomatis
```bash
python -m pytest tests/ -v
```
*(Seluruh 13 tes memvalidasi integritas skema database, konsistensi temporal, batasan as-of, kontrol positif anti-kebocoran, dan kecocokan segel SHA-256).*

### 3. Jalankan Aplikasi Web
```bash
streamlit run streamlit_app.py
```

---

## 7. Peluang Pengembangan Lanjutan (Roadmap)

Proyek ini dirancang modular sehingga siap dikembangkan lebih jauh untuk kebutuhan produksi tingkat enterprise:

1. **Mesin Janji SLA Dinamis (Dynamic ML SLA Engine)**:
   Menggantikan penambahan buffer statis (+3 hari) dengan model regresi kuantil (*Quantile Regression* / LightGBM) yang memprediksi persentil ke-90 durasi pengiriman secara adaptif berdasarkan kombinasi rute spesifik, musim cuaca, dan kategori barang.
2. **Alokasi Eksperimen Cerdas (Multi-Armed Bandit)**:
   Meningkatkan protokol A/B testing statis menjadi algoritma adaptif (*Thompson Sampling* / *Bayesian Bandit*) untuk meminimalkan kerugian pembatalan checkout selama masa eksperimen berlangsung.
3. **Visualisasi Spasial Geografis Interaktif**:
   Integrasi peta koridor logistik Brasil menggunakan PyDeck/Folium untuk menganalisis simpul transit logistik kritis antar-negara bagian secara visual.
4. **Ekstraksi Topik Ulasan Berbasis LLM Lokal**:
   Pengelompokan otomatis keluhan tekstual 13.000 ulasan buruk menggunakan model bahasa terarah untuk mendiagnosis apakah komplain berakar pada kerusakan fisik barang, perilaku kurir, atau salah ekspektasi deskripsi produk.

---

## 8. Lisensi dan Sumber Data

- **Dataset**: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) yang dipublikasikan secara terbuka di Kaggle.
- **Lisensi Kode**: Dirilis di bawah lisensi terbuka [MIT License](LICENSE).
