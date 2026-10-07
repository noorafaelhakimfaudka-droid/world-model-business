# Catatan Belajar Data Science (WMFB Olist)

Buku saku istilah, konsep matematika, dan intuisi bisnis dalam bahasa sederhana dengan contoh angka kecil.

---

## 1. Konsep Dasar & Metodologi

### Pre-registration (Kunci Kriteria di Awal)
- **Bahasa Sederhana**: Menuliskan aturan penilaian dan batas kelulusan *sebelum* bermain atau melihat hasil.
- **Kenapa Penting**: Mencegah "menggeser gawang". Kalau model kita hasilnya biasa saja, kita tidak boleh mengganti rumus metrik seenaknya agar terlihat hebat.
- **Contoh**: Kita sepakati di awal bahwa pesanan disebut "terlambat" jika tiba setelah tanggal estimasi (lewat 1 menit pun terlambat). Kita tidak boleh mengubahnya jadi "toleransi 3 hari" setelah tahu model kita banyak salah.

### Data Leakage (Kebocoran Data)
- **Bahasa Sederhana**: Mencontek kunci jawaban dari masa depan saat ujian.
- **Kenapa Bahaya**: Model di komputer tampak akurasi 99%, tetapi saat dipakai di dunia nyata besok, model gagal total karena informasi masa depan itu belum ada.
- **Contoh**: Memprediksi "apakah pesanan ini akan terlambat saat pelanggan checkout (T0)" dengan memakai kolom "tanggal kurir mengantar barang". Jelas bocor, karena barang baru diantar seminggu setelah checkout!

### Holdout Set Terkunci
- **Bahasa Sederhana**: Berkas ujian akhir yang disimpan di dalam brankas terkunci dan hanya dibuka satu kali di akhir proyek.
- **Kenapa Penting**: Jika data uji sering kita lihat dan kita pakai untuk utak-atik parameter model berkali-kali, model kita secara tidak sadar "menghafal" data uji itu (*overfitting*).

---

## 2. Metrik & Pengukuran

### WAPE (Weighted Absolute Percentage Error)
- **Bahasa Sederhana**: Total jumlah kesalahan prediksi dibagi total volume penjualan sebenarnya.
- **Rumus**: `Sum(|Aktual - Prediksi|) / Sum(Aktual)`
- **Contoh Angka Kecil**:
  - Minggu 1: Asli = 100, Prediksi = 110 (Salah 10)
  - Minggu 2: Asli = 120, Prediksi = 100 (Salah 20)
  - Minggu 3: Asli = 80, Prediksi = 90 (Salah 10)
  - Total salah = 10 + 20 + 10 = 40. Total asli = 100 + 120 + 80 = 300.
  - WAPE = 40 / 300 = 13,3%.
- **Kenapa bukan MAPE biasa?**: Kalau ada minggu dengan penjualan 0 atau 1, MAPE biasa (persen per titik) bisa meledak jadi ratusan persen atau error pembagian nol. WAPE tetap stabil.

### Precision @ Top K vs Akurasi pada Kelas Tak Seimbang
- **Bahasa Sederhana**: Di e-commerce, keterlambatan pengiriman itu kasus langka (misal hanya 8 dari 100 pesanan yang terlambat).
- **Jebakan Akurasi**: Model pemalas yang menebak "semua pesanan tepat waktu" akan mendapat akurasi 92%! Kelihatan pintar, tapi tidak berguna bagi tim operasional.
- **Solusi (Precision & Recall Daftar Teratas)**:
  - Misal tim CS hanya sanggup menelepon 1.000 pelanggan (Top 1.000 pesanan paling berisiko menurut model).
  - Dari 1.000 yang ditelepon, berapa yang benar-benar terlambat? Jika ada 400 pesanan, maka **Presisi = 40%**.
  - Jika dari seluruh marketplace ada 800 pesanan terlambat, dan kita menangkap 400 di antaranya, maka **Recall = 400 / 800 = 50%**.
  - **Lift**: Memilih acak hanya dapat 8% (80 per 1.000). Dengan model dapat 40%. Artinya model **5 kali lebih baik (Lift 5x)** daripada tebak acak!
