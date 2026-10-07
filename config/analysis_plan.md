# Rencana Analisis & Aturan Main Terkunci (Analysis Plan)
*Mengacu pada PRD §3.1 - §3.5, PRD §5 (Langkah 0), dan Gerbang G0*

Dokumen ini mengunci seluruh definisi, metrik, dan ambang kelulusan sebelum model dievaluasi. Perubahan pada dokumen ini hanya boleh dilakukan melalui pencatatan resmi di `experiments/decision_log.md` beserta alasan bisnis/teknis yang jelas.

---

## 1. Tabel Definisi Operasional Variabel

| Istilah | Definisi Operasional di Data | Alasan Bisnis |
|---|---|---|
| **Pesanan Terlambat (Late Order)** | `order_delivered_customer_date > order_estimated_delivery_date` (barang tiba melewati tanggal estimasi yang dijanjikan ke pelanggan). | Pelanggan mengevaluasi ketepatan waktu berdasarkan ekspektasi/janji yang diberikan saat checkout. |
| **Ulasan Buruk (Bad Review)** | `review_score IN (1, 2)` (rating bintang 1 atau 2). | Bintang 1 dan 2 mencerminkan ketidakpuasan serius yang berisiko merusak reputasi platform dan memicu churn. |
| **Ulasan Netral** | `review_score = 3`. | Pelanggan moderat; dipisahkan agar tidak mengaburkan sinyal ulasan negatif. |
| **Ulasan Baik** | `review_score IN (4, 5)`. | Pelanggan puas/sangat puas. |
| **Pelanggan Kembali (Repeat Customer)** | Pelanggan dengan `customer_unique_id` yang memiliki lebih dari 1 `order_id` dalam rentang data validasi. | Mengukur loyalitas riil pelanggan di marketplace. |
| **Titik Prediksi T0** | Momen saat pelanggan menyelesaikan pembelian (`order_purchase_timestamp`). | Hanya fitur yang diketahui saat checkout yang boleh digunakan (harga, jarak estimasi, kategori, reputasi masa lalu seller). |
| **Titik Prediksi T1** | Momen saat barang diserahkan ke kurir (`order_delivered_carrier_date`). | Fitur T0 ditambah durasi penanganan seller (*handling time*). |
| **Titik Prediksi T2** | Momen saat barang tiba di pelanggan (`order_delivered_customer_date`). | Mengetahui keterlambatan riil, sebelum ulasan diberikan pelanggan. |

---

## 2. Metrik Evaluasi & Aturan Naik Tangga (Model Ladder)

### A. Forecasting Permintaan Mingguan (Langkah 5 & Blok B1)
- **Metrik Utama**: **WAPE** (Weighted Absolute Percentage Error) = $\frac{\sum |y - \hat{y}|}{\sum y}$.
- **Baseline**: Nilai minggu lalu (Naive Lag-1) dan Rata-rata Bergerak 4 Minggu (Moving Average).
- **Aturan Naik Tangga**:
  1. Tingkat 1: Baseline Naive / MA.
  2. Tingkat 2: Regresi Linier / Ridge dengan lag, kalender, harga rata-rata.
  3. Tingkat 3: Random Forest / LightGBM.
- **Syarat Lulus Naik Tangga**: Model yang lebih rumit hanya dipilih jika:
  - WAPE turun minimal **3% relatif** dibandingkan model sebelumnya pada validasi bergulir (misal dari 30.0% menjadi $\le 29.1\%$).
  - Menang di mayoritas putaran validasi bergulir (minimal 4 dari 5 putaran).
  - Jika selisih < 3% relatif, pilih model yang lebih sederhana (Occam's Razor).

### B. Prediksi Risiko Keterlambatan & Ulasan Buruk (Langkah 6 & 7)
- **Metrik Utama**: **Precision @ Top 10%**, **Recall @ Top 10%**, **Lift**, dan **PR-AUC**.
- **Larangan**: Tidak boleh mengandalkan Akurasi mentah karena ketidakseimbangan kelas (*class imbalance*).
- **Aturan Keputusan**: Model prediktif harus mengalahkan aturan heuristik sederhana (misal: "tandai pesanan berjarak jauh dari seller dengan reputasi buruk").

### C. Pengujian Nilai Tambah NLP (Langkah 7)
- **Bandingkan 4 Varian**:
  - Model A: Fitur tabular/terstruktur saja.
  - Model B: Model A + rata-rata bintang seller 30 hari terakhir (tanpa teks).
  - Model C: Model B + porsi topik keluhan seller dari teks ulasan masa lalu.
  - Model Plasebo: Model B + porsi topik teks yang diacak antar seller.
- **Syarat NLP Dinyatakan Menambah Nilai**: Model C mengalahkan Model B secara konsisten, sementara Model Plasebo tidak menunjukkan peningkatan performa.

---

## 3. Pagar Metodologi Terkunci

1. **Holdout Terkunci (PRD §3.1)**:
   - Data 8 minggu terakhir dipotong sebelum eksplorasi (EDA), dihitung checksum SHA-256-nya, dan disimpan terpisah.
   - Holdout hanya dibuka tepat **satu kali** pada Langkah 12.
2. **Validasi Berbasis Waktu (PRD §3.1)**:
   - Tidak ada pengacakan baris (*no random k-fold*) pada data deret waktu.
   - Evaluasi menggunakan *Rolling Time-Series Validation* (5–6 putaran) dengan jeda pengaman (*gap/purge*) antar periode latih dan uji.
3. **Pencegahan Kebocoran (PRD §3.2)**:
   - Setiap fitur wajib mencantumkan tanggal ketersediaan $\le$ waktu prediksi.
   - Semua scaler, encoder, pengubah data, dan model NLP hanya di-fit pada data latih di masing-masing putaran.
4. **Bahasa Klaim Terstandarisasi (PRD §3.3)**:
   - Seluruh visualisasi dan tabel wajib memiliki label: `[Data]`, `[Prediksi]`, `[Asosiasi]`, `[Estimasi]`, atau `[Skenario/Asumsi]`.

---

## 4. Ambang Kelulusan Gerbang G0 – G13

| Gerbang | Syarat Kelulusan | Bukti yang Dibutuhkan |
|---|---|---|
| **G0** | Definisi, metrik, rencana analisis terkunci, dan kerangka repositori siap. | Berkas rencana analisis disepakati, struktur repositori terbentuk, tes awal lulus. |
| **G1** | Kontrak data lulus, rekonsiliasi baris selesai, kamus data memiliki tanggal ketersediaan. | Laporan kualitas data & rekonsiliasi; tes kontrak data lulus. |
| **G2** | EDA menjawab pertanyaan bisnis, holdout dipotong dengan checksum tercatat dan belum disentuh. | Grafik berlabel [Data] + kesimpulan bisnis; tes pembagian waktu lulus. |
| **G3** | Klaster seller & pelanggan stabil antar 2 periode dan bermakna bisnis (atau dilaporkan tidak stabil). | Skor siluet, perbandingan profil antar periode. |
| **G4** | Tes kebocoran lulus: kontrol positif tertangkap, target diacak performa jatuh ke acak. | Output tes kebocoran dan tes fitur as-of lulus. |
| **G5** | Forecast mengalahkan baseline sesuai aturan tangga (atau baseline dipertahankan). | Tabel WAPE bergulir + uji bias + rentang 80%. |
| **G6** | Model risiko keterlambatan mengalahkan aturan heuristik pada daftar teratas (Top 10%). | Kurva PR, tabel Precision/Recall/Lift pada T0 vs T1. |
| **G7** | Varian NLP C mengalahkan B dan plasebo tidak naik (atau hasil nihil dilaporkan transparan). | Tabel evaluasi Model A vs B vs C vs Plasebo. |
| **G8** | Seluruh temuan kausalitas diberi label [Asosiasi]; tidak ada klaim sebab-akibat tanpa eksperimen. | Tabel koefisien regresi dengan interval kepercayaan 95%. |
| **G9** | World Model terhubung lolos uji rantai (U1) dan uji jawaban diketahui (U2). | Selisih galat rantai vs terpisah; galat recovery efek sintetis $\le 20\%$. |
| **G10** | Skenario S1-S4 memiliki tingkat bukti (A/B/C), lolos uji kewarasan, dan batas domain jelas. | Tabel simulasi dunia alternatif dengan pita rentang undian sama. |
| **G11** | Nilai ulasan buruk dihitung dari data retensi (L2), titik impas dihitung, rancangan uji coba A/B selesai. | Tabel 3 lapis nilai, tabel titik impas, dokumen rancangan uji coba 2 halaman. |
| **G12** | Holdout dibuka 1 kali, penurunan performa dilaporkan apa adanya, Tabel Bukti lengkap. | Log eksekusi holdout, analisis irisan kegagalan, Tabel Bukti beku. |
| **G13** | Repositori dapat dibangun ulang dengan satu perintah oleh pihak luar, aplikasi lokal berjalan. | Panduan README lengkap, seluruh tes otomatis lulus. |
