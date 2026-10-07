# Pernyataan Masalah Bisnis (Problem Statement)
**Proyek: World Model for Business — Edisi Olist**  
*Mengacu pada PRD §1, PRD §2, dan PRD §5 (Langkah 0)*

---

## 1. Latar Belakang Bisnis

Olist adalah platform e-commerce di Brasil yang menghubungkan penjual kecil (sellers) ke berbagai marketplace besar. Sebagai platform marketplace perantara:
- Olist tidak memiliki armada kurir sendiri dan tidak memiliki inventaris/gudang sendiri secara langsung.
- Kepuasan pelanggan sangat bergantung pada dua hal: **performa pemrosesan pesanan oleh seller** dan **keandalan mitra logistik/pengiriman**.

Ketika pengiriman terlambat atau barang bermasalah, pelanggan melampiaskan kekecewaan lewat ulasan bintang rendah (1–2 bintang) dan enggan bertransaksi kembali. Hal ini merusak reputasi platform dan menghilangkan potensi nilai seumur hidup pelanggan (*customer lifetime value*).

---

## 2. Pertanyaan Inti Proyek

> **Di titik mana marketplace kehilangan paling banyak nilai (ulasan baik, pelanggan, pendapatan) akibat pengiriman terlambat dan masalah seller?**  
> **Seberapa awal masalah itu bisa diprediksi?**  
> **Apa yang terjadi di "dunia alternatif" jika kondisi diubah?**  
> **Tindakan mana yang layak, dan seberapa yakin kita dengan perkiraan dampaknya?**

---

## 3. Para Pengambil Keputusan & Tindakan Konkret

Proyek ini tidak berhenti di akurasi model, melainkan melayani 3 pemangku kepentingan bisnis nyata:

| Pengambil Keputusan | Keputusan yang Didukung | Output Data Science yang Dibutuhkan |
|---|---|---|
| **Manajer Operasi Marketplace** | Menentukan seller, rute antar-wilayah, atau mitra kurir mana yang harus diprioritaskan untuk pembinaan/peringatan/perpanjangan estimasi janji tiba. | Daftar seller & rute berisiko tinggi + estimasi dampak perbaikan terhadap penurunan ulasan buruk. |
| **Manajer Kategori (Commercial)** | Menilai kesiapan pasokan dan mengantisipasi lonjakan permintaan 1–4 minggu ke depan. | Prediksi volume permintaan mingguan per kategori + rentang ketidakpastian (80% confidence interval). |
| **Tim Layanan Pelanggan (Customer Support)** | Menentukan pesanan mana yang harus dihubungi secara proaktif sebelum barang tiba agar kekecewaan mereda. | Skor risiko keterlambatan pada titik T0 (checkout) dan T1 (saat diserahkan ke kurir) beserta titik impas biaya kontak. |

---

## 4. Rantai Nilai Bisnis (The Causal / Relational Chain)

Model dihubungkan mengikuti realitas bisnis e-commerce:

$$\text{Seller \& Logistik} \longrightarrow \text{Keterlambatan Pengiriman} \longrightarrow \text{Ulasan Buruk} \longrightarrow \text{Penurunan Retensi Pelanggan}$$

- **Umpan Balik (Feedback Loop)**: Ulasan buruk dan performa seller di masa lalu memengaruhi reputasi dan permintaan kategori di masa depan.
- **Batasan Jujur**: Data Olist tidak memiliki catatan stok barang, inventaris pabrik, atau kapasitas gudang. Kami secara sadar **TIDAK** memodelkan variabel fiktif tersebut agar tidak menyesatkan pengambil keputusan.
