# Janji: World Model for Business (Edisi Olist)

> **"Jangan perbaiki kurirnya dulu. Uji janjinya."**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests: Pytest Passing](https://img.shields.io/badge/tests-13%20passed-brightgreen.svg)](https://pytest.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistem Pendukung Keputusan (*Decision Support System* / DSS) komprehensif berbasis data 99.084 transaksi nyata e-commerce Olist (Brasil). Proyek ini memadukan **Machine Learning**, **Inferensi Kausal (Propensity Score Matching)**, dan **Simulasi Kontrafaktual Stokastik (World Model)** untuk memitigasi risiko keputusan operasional bernilai ratusan ribu Real sebelum modal fisik digelontorkan.

---

## 1. Latar Belakang dan Dilema Bisnis

### Siapa Olist dan Apa Dilemanya?
Olist adalah platform e-commerce terkemuka di Brasil yang menghubungkan ribuan pelaku UMKM (*sellers*) ke berbagai marketplace digital besar. Model bisnis Olist beroperasi sebagai platform perantara murni:
- **Olist tidak memiliki armada kurir sendiri dan tidak memiliki gudang fisik terpusat.**
- Seluruh pengiriman mengandalkan kurir pihak ketiga melintasi 27 negara bagian Brasil seluas 8,5 juta km² dengan ketimpangan infrastruktur ekstrem (pengiriman di São Paulo rata-rata 8 hari, sementara ke Roraima mencapai 29 hari).
- Keberhasilan transaksi sangat bergantung pada dua simpul: **kecepatan seller menyiapkan paket** dan **keandalan transit kurir pihak ketiga**.

### Fenomena Kritis: "Tebing Kepuasan" dan Retensi Pembeli Pertama
Dari analisis data empiris terhadap 86.283 pesanan historis, terungkap fakta bisnis yang mengkhawatirkan:
1. **Hanya 3,07% pembeli yang pernah berbelanja lebih dari satu kali (73,8% adalah pembeli satu kali transaksi).** Artinya, pesanan pertama adalah satu-satunya taruhan hidup-mati reputasi platform.
2. **Keterlambatan pengiriman mencapai 8,0% dari total pesanan.**
3. **Fenomena Tebing Kepuasan:** Begitu paket terlambat melewati estimasi janji tiba, rating kepuasan konsumen terjun bebas:
   - Paket Tepat Waktu: Rata-rata rating **4,3★** (ulasan buruk hanya 9,8%).
   - Paket Terlambat 1–3 Hari: Rata-rata rating langsung anjlok ke **2,4★** (ulasan buruk melonjak ke 21,4%).
   - Paket Terlambat >7 Hari: Rata-rata rating hancur ke **1,2★** (ulasan buruk mencapai 54,3%).

### Jebakan Refleks Manajemen
Refleks umum manajemen dalam menghadapi krisis keterlambatan biasanya adalah **"Nafsu Logistik Fisik"**: menggelontorkan anggaran ratusan ribu Real untuk menyewa jalur kilat armada kurir atau menjatuhkan sanksi denda pada seller. 

Namun benarkah kurirnya yang harus diperbaiki? Proyek ini membuktikan bahwa akar masalah terbesar sebenarnya terletak pada **ekspektasi janji tiba (SLA) yang tidak realistis**.

---

## 2. Pertanyaan Inti Proyek

Proyek ini dibangun untuk menjawab empat pertanyaan strategis dewan direksi:

1. **Di titik mana marketplace paling banyak kehilangan nilai (rating ulasan, retensi, pendapatan) akibat keterlambatan pengiriman?**
2. **Apakah keterlambatan benar-benar penyebab kausal anjloknya rating, atau sekadar korelasi palsu akibat rute jauh dan paket berat?**
3. **Seberapa awal risiko keterlambatan dapat dideteksi secara akurat tanpa membocorkan data masa depan (as-of prediction di T0 dan T1)?**
4. **Apa yang terjadi di "dunia alternatif" jika kita mengubah janji tiba dibandingkan menambah biaya kurir fisik? Tindakan mana yang paling menguntungkan secara finansial (P&L ROI)?**

---

## 3. Ringkasan Eksekutif dan Temuan Kunci

| Temuan Strategis | Metodologi | Dampak Bisnis Nyata |
|---|---|---|
| **1. Dampak Kausal Keterlambatan Pengiriman** | Propensity Score Matching (PSM) dengan Caliper 0,05 + Uji Plasebo | Keterlambatan terbukti secara kausal langsung memotong **1,71★** kepuasan konsumen (p < 0,001). Uji plasebo pada harga pesanan menghasilkan efek R$ 0,00, membuktikan model tidak bias. |
| **2. Efek Psikologis Janji (The Underpromise Effect)** | Simulasi Kebijakan Kontrafaktual (World Model Blok 1–3) | Menambahkan **+3 hari buffer SLA** pada estimasi tiba di website mencegah **~2.608 ulasan buruk** pada **Capex logistik R$ 0**, jauh lebih efektif daripada program percepatan kurir fisik. |
| **3. Deteksi Dini Risiko Keterlambatan** | Point-in-Time As-Of Random Forest pada titik T0 & T1 | Mendeteksi pesanan berisiko tinggi dengan **presisi 8,0%** di T0 (vs baseline heuristik 4,4% = **1,8x lift**), menjadi dasar pemantauan terarah tanpa memboroskan voucher kompensasi di awal. |
| **4. Valuasi Nilai Retensi dan Titik Impas** | Pemodelan Perilaku Belanja Ulang dan CLV | Setiap ulasan buruk yang dicegah mempertahankan nilai retensi **R$ 14,06** (konservatif) hingga **R$ 92,00** (CLV penuh). Kebijakan buffer SLA menghasilkan surplus bersih **+R$ 182.560**. |

---

## 4. Aplikasi Pendukung Keputusan (Streamlit DSS)

Aplikasi web interaktif disertakan sebagai kokpit pengambilan keputusan bagi pimpinan operasional dan dewan direksi:

```bash
# Menjalankan aplikasi web secara lokal
streamlit run streamlit_app.py
```

### 7 Babak Alur Keputusan:
1. **Babak 1: Dilema Logistik dan Reputasi**: Tebak rating, visualisasi tebing kepuasan, dan 4 metrik kondisi dasar Olist.
2. **Babak 2: Diagnosis Operasional dan Geografi**: Asimetri wilayah (São Paulo 8,3 hari vs Roraima 29,0 hari), dekomposisi waktu (seller 3,0 hari vs kurir 9,5 hari), Pareto 20 kategori (80% volume), dan peramalan mingguan (WAPE 13,6%).
3. **Babak 3: Matriks Penyelamatan Pelanggan dan Penjual**: Analisis RFM retensi pembeli pertama dan pendampingan 6% seller kritis penyumbang sepertiga keterlambatan.
4. **Babak 4: Sistem Peringatan Dini CS (T0 dan T1)**: Form evaluasi risiko real-time, meteran 3 zona aksi Plotly, dan batasan jujur presisi model.
5. **Babak 5: Laboratorium Bukti Kausalitas (PSM Lab)**: Love plot 6.740 pasang kembar identik, estimasi ATE −1,71★, dan kendali mutu uji plasebo.
6. **Babak 6: World Model Simulator (Operational Reality Lab)**: 
   - **Kokpit Makro**: Pilihan lingkup kebijakan (Blanket vs Rute Kritis >800 km vs 6% Seller Lelet), pergeseran gelombang SLA dinamis, neraca keuangan P&L kebijakan, dan uji stres toleransi pembatalan checkout.
   - **Inspektur Pesanan Nyata**: Mikrosimulasi 4 kasus transaksi riil dari database Olist.
7. **Babak 7: Kalkulator ROI Finansial & Protokol A/B Testing**: Titik impas voucher kompensasi CS dan rancangan eksperimen acak terkontrol (~1.560 pesanan per kelompok).

---

## 5. Kerangka Arsitektur Sistem

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

## 6. Pagar Pembatas Metodologi dan Integritas Rekayasa

- **Nol Kebocoran Masa Depan (Zero Future Leakage)**: Seluruh fitur dipartisi berdasarkan stempel waktu ketersediaan (*as-of timestamp*). Fitur di titik T0 tidak mengandung satu pun variabel pasca-checkout.
- **Pemisahan Berurutan Waktu (Chronological Split)**: Tidak menggunakan pengacakan data sembarangan (*random split*) pada data deret waktu. Latih di masa lalu, uji di masa depan dengan jeda pengaman (*buffer period*).
- **Segel Kriptografi Data Uji**: Sebanyak 12.801 pesanan dipisahkan dan disegel dengan hash kriptografi SHA-256 (`dfa121510c806f39cf24b894ae470a7e512af2a987c5ba7cf40dd871dd3ff84e`) dan tidak disentuh selama fase eksperimen.
- **Disiplin Angka Anti-Halusinasi**: Seluruh metrik berasal murni dari eksekusi kode nyata dengan verifikasi ganda (rekonsiliasi SQL dan pandas).

---

## 7. Peta Repositori dan Alur Analisis

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

## 8. Panduan Instalasi dan Pengujian Cepat

### 1. Prasyarat dan Penyiapan Lingkungan
```bash
# Klon repositori
git clone https://github.com/noorafaelhakimfaudka-droid/world-model-business.git
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

## 9. Peluang Pengembangan Lanjutan (Roadmap)

Proyek ini dirancang modular sehingga siap dikembangkan lebih jauh untuk kebutuhan produksi tingkat enterprise:

1. **Mesin Janji SLA Dinamis (Dynamic ML SLA Engine)**:
   Menggantikan penambahan buffer statis (+3 hari) dengan model regresi kuantil (*Quantile Regression* / LightGBM) yang memprediksi persentil ke-90 durasi pengiriman secara adaptif berdasarkan kombinasi rute spesifik, musim cuaca, dan kategori barang.
2. **Alokasi Eksperimen Cerdas (Multi-Armed Bandit)**:
   Meningkatkan protokol A/B testing statis menjadi algoritma adaptif (*Thompson Sampling* / *Bayesian Bandit*) untuk meminimalkan kerugian pembatalan checkout selama masa eksperimen berlangsung.
3. **Visualisasi Spasial Geografis Interaktif**:
   Integrasi peta koridor logistik Brasil menggunakan PyDeck/Folium untuk menganalisis simpul transit logistik kritis antar-negara bagian secara visual.
4. **Ekstraksi Topik Ulasan Berbasis LLM Lokal**:
   Pengelompokan otomatis keluhan tekstual 13.000 ulasan buruk menggunakan model bahasa terarah untuk mendiagnosis apakah komplain berakar pada kerusakan fisik barang, perilaku kurir, atau salah ekspektasi deskripsi produk.
5. **Replikasi Metodologi pada Ekosistem E-Commerce Indonesia**:
   Menerapkan kerangka kerja World Model & As-Of Features ini pada dataset transaksi e-commerce domestik untuk membuktikan adaptabilitas metodologi pada tantangan logistik kepulauan nusantara.

---

## 10. Lisensi dan Sumber Data

- **Dataset**: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) yang dipublikasikan secara terbuka di Kaggle.
- **Lisensi Kode**: Dirilis di bawah lisensi terbuka [MIT License](LICENSE).
