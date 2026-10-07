# PRD WMFB: World Model for Business (Edisi Olist)

**Proyek Data Science end-to-end: memahami kondisi bisnis, memprediksi, menjelaskan, menguji skenario "bagaimana kalau" lewat model yang saling terhubung, lalu merekomendasikan tindakan dengan dampak yang diperkirakan dari data dan rancangan untuk mengukurnya secara nyata.**

| | |
| --- | --- |
| Versi | 1.0 |
| Tanggal | 7 Oktober 2026 |
| Peran | Data Scientist (bukan ML Engineer) |
| Metode | Hanya metode DS/ML standar: SQL, EDA, clustering, regresi, klasifikasi, NLP dasar, validasi, metrik |
| Engineering yang masuk | Lapisan data bertingkat, kode modular, tes otomatis, satu perintah rebuild, kartu model, catatan keputusan, aplikasi lokal read-only |
| Di luar scope (MLOps) | CI/CD, model registry, orkestrasi terjadwal, monitoring produksi, cloud, kontainer, autentikasi, API produksi |
| Durasi | ±15 minggu + 1 minggu cadangan |
| Data utama | Brazilian E-Commerce Public Dataset by Olist |

**Prinsip yang mengatur seluruh dokumen:** bukti lebih penting daripada kerumitan; validasi lebih penting daripada kebaruan; keputusan bisnis lebih penting daripada kecanggihan model; batasan yang jujur lebih penting daripada klaim besar.

---

## 1. Ringkasan dan Arsitektur

Pertanyaan utama proyek:

> **Di titik mana marketplace kehilangan paling banyak nilai (ulasan baik, pelanggan, pendapatan) akibat pengiriman terlambat dan masalah seller? Seberapa awal masalah itu bisa diprediksi? Apa yang terjadi di "dunia alternatif" jika kondisi diubah? Tindakan mana yang layak, dan seberapa yakin kita dengan perkiraan dampaknya?**

### 1.1 Arsitektur World Model (State, Transisi, Intervensi, Strategi)

| Lapisan | Isi | Sumber | Label |
| --- | --- | --- | --- |
| **State** (kondisi tiap minggu per kategori) | Unit terjual, harga rata-rata, persentase pesanan terlambat, rata-rata bintang, porsi ulasan buruk, porsi pelanggan baru, porsi pesanan dari seller berisiko | Olist | [Data] |
| **Faktor luar** (tidak bisa dikontrol) | Kalender, hari libur, lonjakan volume | Kalender dan data | [Data] |
| **Intervensi** (bisa dipilih manajemen) | Perbaikan ketepatan waktu seller, tambahan hari pada janji tiba, kebijakan menghubungi pelanggan lebih dini | Pilihan peneliti | [Skenario/Asumsi] |
| **Transisi** (cara kondisi berubah dari minggu ke minggu) | Empat blok model yang dipelajari dari data: permintaan, keterlambatan, ulasan buruk, pelanggan baru/kembali | Olist | [Prediksi] |
| **Identitas hitungan** | Pendapatan = unit × harga; jumlah ulasan buruk = jumlah pesanan × porsi ulasan buruk | Aritmetika | [Data] |
| **Ketidakpastian** | Kesalahan masa lalu tiap blok diundi ulang agar lintasan masa depan punya rentang | Data validasi | [Prediksi] |
| **Strategi** | Nilai bisnis tiap pilihan tindakan: plafon, titik impas, rentang untung bersih | Data + asumsi berlabel | [Estimasi] dan [Skenario/Asumsi] |

Rantai utama: **seller dan logistik → keterlambatan → ulasan → pelanggan kembali atau tidak**, dengan **permintaan per kategori** sebagai konteks perencanaan. Umpan balik terjadi karena keluaran satu blok menjadi masukan blok lain pada minggu berikutnya.

Yang sengaja **tidak** dimodelkan: stok, produksi, kapasitas, dan kegagalan supplier. Olist tidak memuat datanya, dan versi simulasi karangan mudah terbaca sebagai fakta.

### 1.2 Empat tesis yang diuji (hasil negatif sama sahnya dengan hasil positif)

1. Risiko keterlambatan dan ulasan buruk bisa diprediksi cukup awal untuk dipakai memilih pesanan atau seller yang perlu diintervensi.
2. Teks ulasan menambah kemampuan prediksi **di atas** informasi bintang saja.
3. Memodelkan variabel bisnis sebagai rantai terhubung memberi prediksi multi-minggu lebih baik daripada memprediksi tiap variabel sendiri-sendiri.
4. Dampak skenario dan strategi bisa diperkirakan dengan rentang yang jujur, dan hanya direkomendasikan jika untungnya bertahan di skenario pesimis.

### 1.3 Yang membuat proyek ini berbeda dari proyek Olist pada umumnya

| Umumnya | Di proyek ini |
| --- | --- |
| Prediksi keterlambatan dengan semua kolom, termasuk yang baru diketahui setelah barang tiba | Tiga titik prediksi (saat beli, saat diserahkan ke kurir, saat tiba) dengan tes kebocoran |
| Sentimen teks dianggap pasti membantu | Teks diuji terhadap pembanding "bintang saja" dan plasebo |
| Model berhenti di akurasi | Model dilanjutkan ke dunia alternatif, plafon dampak, titik impas, dan rancangan uji coba |
| Klaim "ulasan buruk turun X%" tanpa batas | Setiap skenario punya tingkat bukti A/B/C, batas domain, dan label asumsi |
| Notebook tunggal yang berantakan | Kode modular, tes otomatis, dan satu perintah untuk membangun ulang semuanya |

---

## 2. Pemilihan Dataset

### 2.1 Kandidat yang diperiksa

| Dataset | Isi (menurut sumbernya) | Cocok untuk | Kelemahan | Keputusan |
| --- | --- | --- | --- | --- |
| **Olist Brazilian E-Commerce** | Sekitar 100 ribu pesanan 2016–2018 di berbagai marketplace Brasil, dengan status pesanan, harga, pembayaran, performa ongkir, lokasi pelanggan, atribut produk, dan ulasan pelanggan. Terdiri dari 9 file CSV, termasuk tabel geolokasi, seller, dan ulasan. | Rantai lengkap seller → pengiriman → ulasan → pelanggan; forecasting; klasifikasi; NLP | Ulasan berbahasa Portugis. Sumber sekunder melaporkan hanya sekitar 3,4% pelanggan yang membeli ulang, jadi sinyal "pelanggan kembali" lemah. Tidak ada data stok. Variasi harga kemungkinan sempit (perkiraan saya, periksa di EDA). | **DATA UTAMA** |
| **M5 Walmart** | Penjualan unit 3.049 produk dalam 3 kategori besar dan 7 departemen, dengan harga per toko dan tanggal, kalender event, dan penanda SNAP; 42.840 deret waktu. | Menguji metode forecasting di data besar yang punya patokan publik | Tidak ada pelanggan, tidak ada teks | **BONUS A** |
| **Corporación Favorita** | Penjualan per toko dan keluarga produk, jumlah item yang sedang promosi, transaksi, harga minyak, hari libur | Forecasting dengan promosi | Tidak ada pelanggan atau teks | Cadangan bonus A |
| **Dunnhumby Complete Journey** | Transaksi 2.500 rumah tangga selama dua tahun; untuk sebagian rumah tangga ada demografi dan riwayat kontak pemasaran langsung | Segmentasi pelanggan, respons promosi, churn | Tidak ada teks; toko fisik | Alternatif jika fokus ke pelanggan |
| **Amazon Reviews 2023** | Lebih dari 570 juta ulasan dan 48 juta produk di 33 kategori, dengan metadata harga | NLP skala besar | Tidak ada angka penjualan; harga hanya potret saat data diambil; terlalu besar tanpa subset | Tidak dipakai |
| **PRDECT-ID (Tokopedia)** | Ulasan produk berbahasa Indonesia dari 29 kategori Tokopedia, dengan label emosi dan sentimen serta atribut seperti lokasi, harga, rating, dan jumlah terjual. Total 5.400 ulasan; di salah satu studi sentimennya 52,3% negatif dan 47,7% positif. | NLP bahasa Indonesia, konteks lokal | Kecil, satu potret waktu (tanpa deret waktu) | **BONUS B** |

### 2.2 Yang tidak ketemu dan perlu diakui

- **Dataset publik Indonesia yang punya penjualan bertanggal dan ulasan sekaligus tidak ketemu.** Yang ada kebanyakan hasil scraping skripsi atau potret satu waktu. Karena itu rantai utama memakai Olist, dan Indonesia masuk lewat bonus B.
- **Scraping Tokopedia sendiri tidak disarankan** untuk portofolio: ada risiko ketentuan layanan dan hukum, dan datanya tidak bisa direproduksi orang lain.
- **Lisensi Olist belum bisa diverifikasi dari hasil pencarian.** Cek halaman Kaggle-nya sebelum repositori dipublikasikan. README PRDECT-ID di Hugging Face menyebut lisensi CC BY 4.0, tetapi cek ulang di halaman Mendeley asalnya.
- Beberapa angka di sumber sekunder saling berbeda (misalnya jumlah rumah tangga Dunnhumby di studi lain). Angka final selalu dihitung ulang dari file asli di Langkah 1.

### 2.3 Keputusan

**Data utama: Olist.** Hanya dataset ini yang memuat seluruh rantai (seller, pengiriman, harga, ulasan teks, pelanggan) dalam satu bisnis nyata. **Bonus A (M5)** dan **bonus B (PRDECT-ID)** hanya dikerjakan jika Langkah 1 sampai 11 selesai.

---

## 3. Aturan Main (berlaku untuk semua langkah)

### 3.1 Validasi berbasis waktu

Selalu latih di masa lalu dan uji di masa depan. Pengacakan baris tidak boleh dipakai untuk data berurutan waktu.

- **Holdout terkunci:** kira-kira 8 minggu terakhir (atau 2 bulan terakhir untuk model tingkat pesanan) dipotong **sebelum EDA**, disimpan terpisah, dan dibuka **satu kali** di Langkah 12.
- **Validasi bergulir:** latih pada periode awal, uji pada periode berikutnya, geser maju, ulangi (sekitar 5 sampai 6 putaran).
- **Jeda pengaman:** beri jarak antara data latih dan data uji sepanjang jangkauan fitur masa lalu terpanjang.

### 3.2 Leakage (kebocoran informasi)

Leakage terjadi ketika model memakai informasi yang belum ada pada saat prediksi dibuat, sehingga hasil tampak bagus tetapi palsu.

**Contoh di Olist:** kita memprediksi apakah pesanan akan terlambat **saat pelanggan membeli**. Tanggal barang diterima pelanggan baru diketahui berhari-hari kemudian. Jika kolom itu (atau turunannya) masuk sebagai fitur, model tampak hampir sempurna padahal tidak berguna.

**Aturan sederhana:** setiap kolom diberi "tanggal ketersediaan", yaitu kapan nilainya baru diketahui. Fitur hanya boleh dipakai jika tanggal ketersediaannya sebelum waktu prediksi.

**Tes wajib sebelum model dievaluasi:**

1. **Audit tanggal:** daftar semua fitur beserta kapan nilainya diketahui.
2. **Tes kontrol positif:** sengaja masukkan satu fitur dari masa depan. Hasilnya harus melonjak tidak wajar, membuktikan pengecekan kita memang bisa menangkap kebocoran.
3. **Tes acak target:** acak label dalam blok waktu. Performa harus jatuh ke level asal-asalan.
4. **Statistik seller "as-of":** angka seperti "persentase terlambat seller 30 hari terakhir" hanya boleh dihitung dari pesanan yang **sudah selesai sebelum** waktu prediksi. Pesanan yang dibeli 10 Maret tidak boleh memakai hasil pengiriman 12 Maret.
5. **Semua pengubah data** (penskalaan, TF-IDF, clustering) dilatih hanya pada data latih tiap putaran validasi.

### 3.3 Aturan bahasa klaim

| Jenis klaim | Contoh kalimat yang boleh | Kalimat yang dilarang |
| --- | --- | --- |
| **[Data]** fakta | "Pada 2018, 8% pesanan tiba setelah tanggal janji." | Tafsir sebab tanpa bukti |
| **[Prediksi]** | "Model menangkap 50% pesanan terlambat dengan menandai 10% pesanan teratas pada data uji." | "Model tahu apa penyebabnya" |
| **[Asosiasi]** | "Pesanan terlambat berasosiasi dengan ulasan buruk, setelah memperhitungkan kategori dan harga." | "Keterlambatan menyebabkan ulasan buruk" |
| **[Estimasi]** hitungan dari data nyata dengan rentang | "Pelanggan dengan ulasan buruk membeli ulang sekitar 1,6 poin persen lebih jarang; nilainya diperkirakan R$ 1,5 sampai R$ 3 per ulasan." (angka contoh, bukan hasil) | Menyebutnya angka pasti |
| **[Skenario/Asumsi]** | "Jika 10% seller terburuk menurunkan keterlambatan separuhnya, model memperkirakan ulasan buruk turun sekitar X, dengan asumsi hubungan masa lalu tetap berlaku." | "Kalau diperbaiki, ulasan buruk **akan** turun X" |

Setiap tabel dan grafik di laporan diberi salah satu label di atas.

### 3.4 Kunci kriteria sebelum melihat hasil

Sebelum eksperimen, tulis satu halaman "rencana analisis": metrik utama, ambang lulus tiap gerbang, definisi "terlambat" dan "ulasan buruk", jendela data. Setelah dikunci, jangan diubah diam-diam setelah melihat hasil uji atau holdout. Jika harus diubah, catat alasannya di catatan keputusan (bagian 4.1).

### 3.5 Metrik dan cara membacanya

**Forecasting: WAPE** (total kesalahan dibagi total nilai sebenarnya). Contoh: tiga minggu, penjualan sebenarnya 100, 120, 80 (total 300); prediksi 110, 100, 90. Selisih mutlaknya 10, 20, 10 (total 40). WAPE = 40 / 300 = **13,3%**. Lebih stabil daripada persentase per titik ketika angka kecil.

**Klasifikasi tak seimbang (terlambat, ulasan buruk): jangan hanya pakai akurasi.** Contoh: dari 10.000 pesanan uji, 800 benar-benar terlambat (8%). Model menandai 1.000 pesanan paling berisiko, dan 400 di antaranya memang terlambat.
- Presisi = 400 / 1.000 = **40%**.
- Recall = 400 / 800 = **50%**.
- Lift = 40% / 8% = **5 kali** lebih baik daripada memilih acak.
- Model yang menebak "tidak ada yang terlambat" akurasinya 92%, tetapi tidak berguna. Karena itu metriknya presisi dan recall pada daftar teratas, serta PR-AUC.

**Rentang ketidakpastian:** pakai sebaran kesalahan model pada data validasi. Contoh: prediksi 200 unit; pada validasi, 80% kali nilai sebenarnya jatuh dalam ±25% dari prediksi, jadi rentang 80% adalah **150 sampai 250 unit**. Lalu periksa di data uji: dari 100 titik, berapa yang benar-benar masuk rentang? Idealnya sekitar 80. Jika hanya 65, laporkan apa adanya.

**Catatan ukuran sampel:** data mingguan per kategori kecil (8 kategori × ±87 minggu ≈ 700 baris; holdout 8 minggu ≈ 64 baris). Jangan menjadikan "tepat 80%" sebagai syarat lulus; laporkan hasil dengan catatan bahwa angkanya berisik.

---

## 4. Standar Engineering Data Science (tanpa MLOps)

Tujuannya agar hasil bisa diperiksa, diulang, dan dipercaya orang lain. Ini praktik seorang data scientist, bukan infrastruktur produksi.

### 4.1 Standar yang wajib

| Area | Standar | Bukti di repositori |
| --- | --- | --- |
| **Lapisan data bertingkat** | Tiga tingkat di MySQL: mentah (persis seperti file asal), bersih (tipe dan kunci dibereskan), mart (tabel analisis dan tampilan fitur). Skrip bernomor dan bisa dijalankan ulang tanpa merusak hasil. Jumlah baris direkonsiliasi antar tingkat. | Folder sql dengan skrip bernomor, laporan rekonsiliasi |
| **Kontrak data otomatis** | Cek otomatis tiap kali data dimuat: skema, kunci unik, pasangan antar tabel, urutan waktu, nilai mustahil. | Laporan kualitas data yang dibuat ulang tiap run |
| **Kode modular** | Notebook tipis (hanya memanggil, menampilkan tabel dan grafik, menulis interpretasi). Logika berada di modul terpisah: data, fitur as-of, NLP, model, evaluasi (pembagian waktu, metrik), world model, skenario, strategi, pelaporan. | Folder src dengan modul per fungsi |
| **Konfigurasi, bukan angka ajaib** | Jendela data, ambang gerbang, seed, ruang strategi, asumsi biaya berada di berkas konfigurasi. | Folder config |
| **Tes otomatis** | Satu perintah menjalankan semua tes (daftar di 4.2). | Folder tests, semua lulus |
| **Reproducibility** | Satu perintah membangun ulang dari data mentah sampai tabel hasil dan grafik. Seed terpisah untuk pembagian data, model, dan simulasi. Versi library dikunci. Hasil berat disimpan sementara (cache) supaya run ulang tidak berjam-jam. | README, berkas lingkungan |
| **Pencatatan** | Catatan percobaan (tanggal, fitur, model, metrik, hasil, termasuk yang gagal); catatan keputusan gerbang (tanggal, keputusan, alasan); **kartu model** satu halaman per model (tujuan, data, metrik, batasan, kapan tidak boleh dipakai). | Folder experiments dan reports |
| **Kualitas kode** | Format dan pemeriksaan gaya kode otomatis di komputer sendiri, nama yang jelas, fungsi kecil dengan keterangan singkat. | Konfigurasi format di repositori |
| **Aplikasi lokal read-only** | Aplikasi demo yang hanya membaca hasil tersimpan; tidak melatih ulang. Menampilkan rentang, label, dan batasan. | Folder app |

### 4.2 Delapan jenis tes otomatis

| # | Tes | Memeriksa |
| --- | --- | --- |
| 1 | Kontrak data | Skema, kunci unik, referensial, urutan waktu |
| 2 | Pembagian waktu | Tidak ada tumpang tindih waktu antara data latih, uji, dan holdout; jeda pengaman terpenuhi |
| 3 | Fitur as-of | Hasil perhitungan bertahap sama dengan hitungan manual yang lambat; tanggal informasi tiap fitur ≤ waktu prediksi |
| 4 | Kebocoran | Kontrol positif tertangkap; acak target menjatuhkan performa |
| 5 | Identitas hitungan | Pendapatan = unit × harga; jumlah pesanan konsisten antar tabel; tidak ada nilai negatif yang mustahil |
| 6 | Kewarasan skenario | Perubahan nol = hasil sama dengan dasar; efek lebih besar tidak lebih kecil; seed sama menghasilkan hasil sama |
| 7 | **Hasil beku** | Angka kunci di Tabel Bukti (misalnya WAPE model terpilih, presisi daftar teratas) direproduksi dari hasil tersimpan dalam toleransi yang ditetapkan. Yang dibandingkan adalah angka yang sudah dibekukan di Tabel Bukti dengan hasil yang direproduksi ulang. |
| 8 | Aplikasi | Aplikasi terbuka, menampilkan rentang di setiap angka prediksi, dan menampilkan label |

### 4.3 Yang sengaja tidak dikerjakan (batas dengan MLOps)

CI/CD otomatis (tes dijalankan manual dengan satu perintah), model registry (hasil disimpan sebagai berkas bernomor dan tercatat), pipeline terjadwal, monitoring produksi, cloud, kontainer, autentikasi, dan API produksi. API tipis hanya ada sebagai bonus D, dan tidak disarankan sebelum semua gerbang selesai.

---

## 5. Langkah demi Langkah

Setiap langkah punya format sama: **Tujuan, Dikerjakan, Output, Gerbang lulus.** Pekerjaan engineering (bagian 4) berjalan sejak minggu 1, bukan di akhir.

### Langkah 0: Kunci masalah dan aturan main (minggu 1)

- **Tujuan:** mulai dari keputusan bisnis, bukan dari model.
- **Dikerjakan:** tulis pernyataan masalah satu halaman; definisikan istilah ("terlambat" = barang tiba setelah tanggal estimasi yang dijanjikan; "ulasan buruk" = bintang 1 sampai 2); tentukan metrik tiap modul; susun rencana analisis (3.4); siapkan repositori, lingkungan, struktur folder, dan kerangka tes (tes kosong yang akan diisi).
- **Output:** rencana analisis, tabel definisi, repositori kosong yang bisa dijalankan dengan satu perintah.
- **Gerbang G0:** definisi dan ambang lulus tertulis sebelum menyentuh model.

| Pengambil keputusan | Keputusan yang didukung | Hasil yang dibutuhkan |
| --- | --- | --- |
| Manajer operasi marketplace | Seller, rute, atau wilayah mana yang diprioritaskan | Daftar berisiko + perkiraan dampak |
| Manajer kategori | Kesiapan pasokan per kategori 4 minggu ke depan | Prediksi permintaan + rentangnya |
| Tim layanan pelanggan | Pesanan mana yang dihubungi lebih awal | Daftar pesanan berisiko + cara kerjanya |

### Langkah 1: Lapisan data dan cek kualitas (minggu 1 sampai 2)

- **Tujuan:** memastikan data layak dan pipeline data bisa diulang.
- **Dikerjakan:** muat 9 tabel Olist ke tingkat mentah di MySQL; bangun tingkat bersih lalu mart (tabel pesanan lengkap: pesanan, item, pembayaran, ulasan, seller, produk, pelanggan); jalankan kontrak data; buat kamus data berisi kolom, arti, dan **tanggal ketersediaan**; tentukan jendela analisis setelah profiling (awal dan akhir periode Olist jarang atau tidak lengkap).
- **Cek kualitas:** kunci unik, pasangan antar tabel lengkap, urutan waktu masuk akal (beli ≤ kirim ≤ terima), nilai mustahil, selisih total pembayaran vs total item + ongkir, minggu kosong per kategori, minggu terakhir yang terpotong, proporsi ulasan yang punya teks, **angka pelanggan yang membeli ulang** (hitung sendiri; sumber sekunder bilang sekitar 3,4%).
- **Output:** laporan kualitas data (baris yang dibuang beserta alasan dan jumlahnya), laporan rekonsiliasi antar tingkat, kamus data, tes kontrak data (tes 1) yang lulus.
- **Gerbang G1:** semua cek punya hasil dan tindakan. Pelanggaran kecil (di bawah ±0,5% baris) dibersihkan dan dicatat; pelanggaran besar mengubah jendela atau definisi, dengan alasan tertulis.

### Langkah 2: Potong holdout, lalu EDA dan kondisi bisnis (minggu 2 sampai 3)

- **Tujuan:** memahami apa yang terjadi tanpa mengintip data uji akhir.
- **Dikerjakan:** **potong dan simpan holdout dulu**; baru EDA pada sisanya. Isi EDA: tren pesanan dan pendapatan, musiman (data kurang dari dua tahun penuh, jadi November hanya muncul satu kali), kategori terbesar, sebaran harga dan ongkir, waktu antar (janji vs kenyataan), sebaran bintang, peta lokasi seller dan pelanggan, keterlambatan menurut wilayah dan seller, episode khusus (lonjakan November, minggu dengan keterlambatan tinggi).
- **KPI dasar:** jumlah pesanan, pendapatan, nilai rata-rata per pesanan, persentase terlambat, rata-rata bintang, persentase ulasan buruk, persentase pelanggan kembali.
- **Output:** bab EDA berisi 8 sampai 10 grafik, masing-masing diakhiri satu kalimat "jadi apa"; tes pembagian waktu (tes 2) lulus.
- **Gerbang G2:** setiap grafik berujung pada pertanyaan atau keputusan; holdout belum pernah disentuh (checksum file dicatat).

### Langkah 3: Segmentasi seller dan pelanggan dengan clustering (minggu 3)

- **Tujuan:** menemukan kelompok perilaku yang bisa ditindaklanjuti.
- **Dikerjakan:** clustering seller (volume, harga rata-rata, persentase terlambat, rata-rata bintang, lama pengiriman) dan pelanggan (nilai belanja, kategori, lokasi, kepuasan); pilih jumlah kelompok dengan metode siku dan skor siluet; **uji kestabilan** dengan mengulang pada dua periode berbeda; beri nama kelompok yang bermakna bisnis (contoh: "seller besar, sering terlambat").
- **Output:** profil tiap kelompok dan satu rekomendasi per kelompok.
- **Gerbang G3:** kelompok stabil antar periode **dan** bisa dijelaskan dalam satu kalimat bisnis. Jika tidak, laporkan "segmentasi tidak stabil".

### Langkah 4: Tabel fitur "as-of" dan tes kebocoran (minggu 4)

- **Tujuan:** membuat tabel fitur yang aman dari kebocoran, dengan tiga titik waktu prediksi.

| Titik | Kapan | Fitur yang boleh dipakai | Yang diprediksi |
| --- | --- | --- | --- |
| **T0** | Saat pelanggan membeli | Harga, ongkir, kategori, berat dan dimensi produk, jarak seller ke pelanggan (dari koordinat kode pos), tanggal estimasi tiba, bulan dan hari, statistik seller **as-of** (keterlambatan dan bintang 30 dan 90 hari terakhir) | Akan terlambat? Akan berulasan buruk? |
| **T1** | Barang diserahkan ke kurir | Semua fitur T0 + lama seller memproses pesanan | Sama, dengan informasi lebih lengkap |
| **T2** | Barang tiba | Semua fitur T1 + keterlambatan sebenarnya | Akan berulasan buruk? |

Nilai tambah: **seberapa awal** masalah bisa dideteksi (T0, T1, atau T2), karena itu yang menentukan apakah intervensi masih sempat dilakukan.

- **Output:** tiga tabel fitur, tabel mingguan per kategori (untuk forecasting dan World Model), tes fitur as-of (tes 3) dan tes kebocoran (tes 4) yang lulus.
- **Gerbang G4:** semua tes kebocoran lulus, termasuk kontrol positif. Model **dilarang** dievaluasi sebelum gerbang ini lulus.

### Langkah 5: Forecast permintaan mingguan per kategori (minggu 5)

- **Tujuan:** memprediksi unit terjual 1 sampai 4 minggu ke depan untuk 6 sampai 8 kategori terbesar.
- **Anak tangga model (naik hanya jika terbukti lebih baik):**
  1. **Dasar:** nilai minggu lalu; rata-rata bergerak.
  2. **Regresi linier/Ridge** dengan fitur lag (nilai minggu-minggu sebelumnya), kalender, harga rata-rata.
  3. **Random Forest atau LightGBM** dengan fitur yang sama.
- **Aturan naik tangga (dikunci di G0):** model lebih rumit dipakai hanya jika (a) WAPE turun minimal ±3% relatif pada validasi bergulir, **dan** (b) membaik di mayoritas putaran (contoh: menang di 5 dari 6 putaran), **dan** (c) bertahan pada holdout. Jika seri, pakai yang lebih sederhana.
- **Contoh angka:** baseline WAPE 30%; syarat 3% relatif berarti model baru harus mencapai ≤ 29,1%. Jika perbaikannya lebih kecil dari fluktuasi antar putaran, anggap tidak terbukti.
- **Dilaporkan:** WAPE per horizon (1, 2, 3, 4 minggu), per kategori, bias (cenderung terlalu tinggi atau rendah), dan rentang 80%.
- **Output:** tabel perbandingan model, grafik prediksi vs kenyataan dengan pita rentang, daftar kategori yang tidak boleh diprediksi (volume terlalu kecil), kartu model.
- **Gerbang G5:** model terpilih mengalahkan dasar sesuai aturan, atau dilaporkan "tidak ada yang mengalahkan baseline".

### Langkah 6: Prediksi risiko keterlambatan pesanan (minggu 6)

- **Tujuan:** menandai pesanan yang berisiko terlambat pada T0 dan T1.
- **Dikerjakan:** logistic regression → Random Forest → LightGBM; atasi ketidakseimbangan kelas dengan bobot kelas; ukur **presisi dan recall pada daftar teratas** (misalnya 10% pesanan teratas), PR-AUC, dan lift; bandingkan T0 vs T1; analisis per wilayah dan kategori.
- **Output:** tabel kinerja T0 vs T1, kurva presisi-recall, fitur terpenting, jawaban "berapa besar daftar yang harus ditangani untuk menangkap separuh keterlambatan", kartu model.
- **Gerbang G6:** model mengalahkan aturan sederhana (misalnya "tandai pesanan berjarak jauh dengan seller yang riwayatnya buruk"). Jika tidak, aturan sederhana itulah rekomendasinya.

### Langkah 7: Prediksi ulasan buruk dan nilai tambah NLP (minggu 7 sampai 8)

- **Tujuan:** memprediksi ulasan bintang 1 sampai 2 dan menjawab tesis 2.
- **Bagian A: model terstruktur.** Fitur T0, T1, T2. Metrik sama dengan Langkah 6.
- **Bagian B: NLP dasar pada teks Portugis.** Teks **tidak diterjemahkan**. Praproses dengan stopword bahasa Portugis; sentimen dengan TF-IDF + logistic regression (label lemah: bintang 1 sampai 2 negatif, 3 netral, 4 sampai 5 positif); topik keluhan dengan NMF atau LDA, lalu **periksa topik secara manual** (contoh topik: barang tidak sampai, produk cacat, salah barang). Tulis keterbatasan label lemah.
- **Bagian C: tes nilai tambah teks.** Ulasan sebuah pesanan **tidak boleh** dipakai memprediksi ulasan pesanan itu sendiri (bocor). Teks dipakai di level seller dan masa lalu: "porsi keluhan topik X pada ulasan seller 30 hari terakhir".

| Versi | Fitur |
| --- | --- |
| A | Fitur terstruktur saja |
| B | A + **rata-rata bintang** seller 30 hari terakhir (tanpa teks) |
| C | B + porsi topik keluhan seller 30 hari terakhir (dari teks) |
| Plasebo | B + porsi topik yang **diacak antar seller** |

**Aturan keputusan:** NLP dianggap membantu hanya jika **C mengalahkan B** secara konsisten di mayoritas putaran validasi **dan** plasebo tidak ikut membaik. B dipakai sebagai pembanding karena label sentimen berasal dari bintang; tanpa B kita tidak tahu apakah manfaatnya dari teks atau sekadar bintang yang dibungkus ulang.
- **Output:** tabel A/B/C/plasebo, satu halaman "topik keluhan teratas dan contoh ulasannya" (bernilai bisnis walaupun NLP tidak menambah akurasi), kartu model.
- **Gerbang G7:** keputusan tertulis "NLP dipertahankan" atau "NLP dijadikan eksploratori; hasil nol dilaporkan".

### Langkah 8: Penjelasan model dan asosiasi (minggu 8)

- **Tujuan:** menjawab "kenapa", dengan bahasa klaim yang benar.
- **Dikerjakan:** SHAP atau pentingnya fitur untuk model terpilih; regresi sederhana (statsmodels) untuk hubungan keterlambatan, harga, dan ulasan buruk dengan interval kepercayaan; uji kestabilan di dua periode dan beberapa kategori besar.
- **Contoh pelaporan yang benar:** "Pesanan terlambat berasosiasi dengan peluang ulasan buruk yang jauh lebih tinggi (angka dan rentang dari data), setelah memperhitungkan kategori dan harga. Ini asosiasi, bukan bukti sebab-akibat."
- **Output:** tabel asosiasi berlabel [Asosiasi] dan daftar keterbatasannya (pembaur yang tidak teramati, tidak ada eksperimen). Hasil ini menjadi bahan untuk blok-blok World Model.
- **Gerbang G8:** tidak ada kalimat sebab-akibat tanpa dasar; tiap hubungan berlabel.

### Langkah 9: World Model, rantai blok yang terhubung (minggu 9 sampai 10)

- **Tujuan:** menghubungkan hasil Langkah 5 sampai 8 menjadi satu sistem yang bisa dijalankan maju beberapa minggu dengan ketidakpastian, sebagai dasar dunia alternatif.
- **Unit:** kategori × minggu (6 sampai 8 kategori). State minggu t hanya memakai informasi yang sudah diketahui sampai akhir minggu t.

**Blok transisi (semuanya dipelajari dari data nyata, dengan model dari anak tangga Langkah 5):**

| Blok | Memprediksi | Dari | Evaluasi |
| --- | --- | --- | --- |
| B1 Permintaan | Unit minggu depan | Unit minggu-minggu lalu, harga rata-rata, kalender, persentase terlambat dan bintang minggu lalu | WAPE |
| B2 Keterlambatan | Persentase terlambat minggu depan | Volume, porsi pesanan dari seller berisiko, musim, nilai minggu lalu | Rata-rata selisih mutlak |
| B3 Ulasan buruk | Porsi ulasan buruk minggu depan | Persentase terlambat pada minggu yang sama, kategori, harga, nilai minggu lalu | Rata-rata selisih mutlak |
| B4 Pelanggan baru dan kembali | Porsi pelanggan baru | Bintang minggu lalu | Dilaporkan apa adanya (kemungkinan lemah) |

**Identitas hitungan:** pendapatan = unit × harga rata-rata; jumlah ulasan buruk = jumlah pesanan × porsi ulasan buruk. **Harga dianggap masukan dari luar** (tidak diprediksi), dan karena variasi harga sempit, skenario harga ditandai tidak didukung kecuali EDA menunjukkan sebaliknya.

**Cara menjalankan maju (rollout):**
1. Mulai dari minggu terakhir yang diketahui.
2. Tiap blok memprediksi minggu berikutnya; hasilnya menjadi masukan blok lain (inilah umpan balik).
3. Pada setiap blok ditambahkan **kejutan acak** yang diambil dari kesalahan blok itu di data validasi. Contoh: blok permintaan memprediksi 200 unit; kesalahan masa lalu −30, −10, 0, +10, +40; undian +10 menghasilkan 210, undian −30 menghasilkan 170.
4. Ulangi 200 sampai 500 kali sehingga terbentuk rentang.
5. **Dunia alternatif** = rollout yang sama dengan satu intervensi. Dunia dasar dan dunia alternatif memakai **undian acak yang sama**, supaya selisihnya bersih dari kebetulan. Contoh: dasar 1.000 unit, alternatif 1.030, selisih 30. Jika undiannya berbeda, selisih bisa tampak −50 atau +100 hanya karena kebetulan.

**Tiga uji kejujuran (Gerbang G9):**

| Uji | Pertanyaan | Cara | Aturan |
| --- | --- | --- | --- |
| **U1 Rantai vs terpisah** | Apakah menghubungkan blok benar-benar membantu? | Bandingkan galat prediksi 1 sampai 8 minggu antara rantai terhubung dan model terpisah (tiap variabel diprediksi hanya dari riwayatnya sendiri) | Rantai dianggap berguna jika galat 4 minggu turun minimal ±3% relatif dan konsisten di mayoritas putaran. Jika tidak, pakai model terpisah dan turunkan sebutan "world model" menjadi "kumpulan prediksi" |
| **U2 Jawaban diketahui** | Apakah mesin skenario bisa menemukan efek yang sudah diketahui? | Buat data tiruan dengan hubungan yang kita tentukan (contoh: tiap kenaikan 1 poin persen keterlambatan menaikkan ulasan buruk 0,4 poin), jalankan seluruh pipeline, bandingkan efek hasil mesin dengan efek yang sebenarnya. Variasikan derau dan tambahkan pembaur (contoh: musim memengaruhi keterlambatan dan ulasan sekaligus) | Contoh angka: efek benar −0,8 poin, hasil mesin −0,7 poin, galat 12,5%. Lulus jika arah efek benar di minimal 95% dari 100 data tiruan dan galat relatif median ≤ 20% pada kondisi dasar. Laporkan di kondisi mana metode gagal |
| **U3 Replay kejadian nyata** | Apakah model masuk akal pada episode yang benar-benar terjadi? | Latih hanya dengan data sebelum episode (misalnya lonjakan November 2017 atau minggu keterlambatan tinggi), masukkan faktor luar aktual (volume), bandingkan lintasan model dengan kenyataan | Galat lebih kecil daripada baseline, dan nilai sebenarnya jatuh dalam rentang 80% pada sebagian besar minggu. Catatan: data sebelum November 2017 hanya sekitar 10 bulan, jadi hasilnya berisik |

- **Output:** rantai blok yang bisa dijalankan, grafik rollout dengan pita rentang, hasil U1, U2, U3, kartu model, tes identitas hitungan (tes 5).
- **Gerbang G9:** U1 dan U2 lulus (atau klaim diturunkan sesuai aturan); hasil U3 dilaporkan apa adanya.

### Langkah 10: Skenario "bagaimana kalau" dan validasinya (minggu 11)

- **Tujuan:** menjalankan dunia alternatif dan memberi tingkat bukti pada tiap hasil.

| Skenario | Intervensi | Cara | Label | Tingkat bukti maksimum |
| --- | --- | --- | --- | --- |
| **S1** Seller berisiko lebih tepat waktu | Persentase terlambat seller berisiko dikali 0,5 (contoh) | Rollout dunia alternatif lewat B2, B3 | [Skenario/Asumsi] | A jika lolos U2 dan U3 |
| **S2** Tambahan hari pada janji tiba | +3 hari untuk rute berisiko tinggi (contoh) | **Hitungan murni dari data nyata**: berapa pesanan yang tidak lagi "terlambat". Reaksi pelanggan terhadap janji lebih lama adalah asumsi terpisah | [Data] untuk hitungan, [Skenario/Asumsi] untuk reaksi | Tinggi untuk hitungannya |
| **S3** Lonjakan volume | Unit +20% pada faktor luar (contoh pekan seperti November) | Rollout lewat semua blok | [Asosiasi] | B jika lolos U1 dan U2 |
| **S4** Gabungan S1 + S2 | Dua intervensi sekaligus | Efek interaksi dilaporkan, **tidak dijumlahkan** | [Skenario/Asumsi] | Mengikuti yang terendah |

- **Tingkat bukti:** **A** = lolos jawaban-diketahui (U2), replay (U3), dan uji kewarasan; **B** = lolos U2 dan uji kewarasan tanpa replay yang relevan; **C** = hanya lolos uji kewarasan atau sangat bergantung asumsi. Skenario C wajib diberi tulisan "ilustratif, bukan dasar keputusan".
- **Contoh hitungan S1 (angka ilustrasi, bukan hasil data):** per 100.000 pesanan, 8% terlambat (8.000), peluang ulasan buruk pada pesanan terlambat 55% dan pada yang tepat waktu 10%. Ulasan buruk sekarang: 8.000 × 0,55 + 92.000 × 0,10 = 4.400 + 9.200 = **13.600**. Jika keterlambatan turun ke 6%: 6.000 × 0,55 + 94.000 × 0,10 = 3.300 + 9.400 = **12.700**. Selisih 900 ulasan buruk (turun sekitar 6,6%). Perhatikan: sekitar dua pertiga ulasan buruk (9.200 dari 13.600) datang dari pesanan yang **tidak** terlambat, jadi memperbaiki ketepatan waktu saja tidak menghabiskan masalah.
- **Cek terhadap kejadian nyata:** pilih seller dengan minimal 30 pesanan di tiap periode yang persentase terlambatnya turun minimal 10 poin antara dua periode 3 bulan berturut-turut. Bandingkan perubahan porsi ulasan buruk mereka dengan seller serupa yang keterlambatannya tidak berubah, lalu bandingkan dengan perkiraan model. Ini asosiasi, bukan bukti sebab-akibat, tetapi cocok-tidaknya perkiraan dengan kenyataan menaikkan atau menurunkan kepercayaan.
- **Uji kewarasan:** perubahan nol = hasil sama dengan dasar; perubahan lebih besar = efek searah dan tidak lebih kecil; perubahan kecil = efek kecil; hasil tidak keluar dari rentang yang pernah terlihat. Perubahan di luar jangkauan data (contoh: keterlambatan turun ke 0%) ditandai **EKSTRAPOLASI** dan tidak dilaporkan sebagai angka pasti.
- **Output:** tabel skenario dengan rentang, tingkat bukti, dan label; tes kewarasan skenario (tes 6) yang lulus.
- **Gerbang G10:** setiap skenario punya tingkat bukti dan label; skenario C ditandai ilustratif.

### Langkah 11: Nilai bisnis, strategi, dan rancangan uji coba (minggu 12 sampai 13)

- **Tujuan:** mengubah temuan menjadi keputusan dengan **asumsi sesedikit mungkin dan setransparan mungkin**, lalu merancang cara mengukur asumsi yang tersisa.
- **Prinsip jujur:** tanpa eksperimen, dampak intervensi **tidak bisa disebut terukur**. Hasil akhir proyek adalah dampak yang diperkirakan dengan rentang, ditambah rancangan untuk mengukurnya.

**A. Tiga lapis nilai (dari paling pasti ke paling berasumsi)**

| Lapis | Isi | Label | Contoh |
| --- | --- | --- | --- |
| **L1 Terukur** | Jumlah dan nilai pesanan bermasalah; **plafon dampak** (batas atas perbaikan jika masalah dihapus total) | [Data] | Dari contoh S1: jika keterlambatan jadi 0, ulasan buruk turun dari 13.600 ke 10.000 (selisih 3.600, sekitar 26%). Seberapa pun bagusnya intervensi, perbaikan ketepatan waktu tidak bisa melampaui sekitar 26% |
| **L2 Estimasi dari data** | **Nilai satu ulasan buruk**: selisih tingkat beli ulang pelanggan setelah ulasan buruk vs ulasan baik, dikali nilai belanja rata-rata; efek keterlambatan pada pembelian ulang; keduanya dengan rentang | [Estimasi] | Ilustrasi: 2,0% pelanggan dengan ulasan buruk membeli ulang vs 3,6% dengan ulasan baik; selisih 1,6 poin × nilai belanja rata-rata R$ 140 = **sekitar R$ 2,24 per ulasan buruk** |
| **L3 Asumsi tersisa** | Seberapa efektif intervensi menurunkan peluang ulasan buruk; efek reputasi (mulut ke mulut) yang tidak terlihat di data; biaya tindakan | [Skenario/Asumsi] | Diberi rentang pesimis, dasar, optimis dan titik impas |

Catatan penting: karena pembelian ulang di Olist sangat jarang, nilai satu ulasan buruk dari L2 kemungkinan **kecil**. Itu temuan yang sah dan bisa mengubah keputusan, dan lebih jujur daripada menebak R$ 30 atau lebih. Efek reputasi dilaporkan terpisah sebagai asumsi.

**B. Pilihan strategi yang dibandingkan**

| Strategi | Inti |
| --- | --- |
| A. Hubungi dini pelanggan pada pesanan berisiko | Memakai daftar teratas model T1 |
| B. Peringatan dan pembinaan seller berisiko | Memakai segmentasi dan skor seller |
| C. Perpanjang janji tiba pada rute berisiko | Hasil S2 |
| D. Status quo | Pembanding wajib |

**C. Contoh titik impas (angka ilustrasi; mata uang mengikuti data, R$)**

Strategi A menandai 1.000 pesanan. Presisi 40%, sehingga 400 benar-benar terlambat. Asumsi biaya: R$ 1 per pesanan yang dihubungi, total R$ 1.000. Misalkan menghubungi pelanggan menurunkan peluang ulasan buruk pada pesanan terlambat sebesar d poin, dan satu ulasan buruk bernilai v. Impas tercapai ketika 400 × d × v = R$ 1.000, yaitu d × v = 2,5.

| Nilai satu ulasan buruk (v) | Penurunan yang dibutuhkan agar impas (d) | Masuk akal? |
| --- | --- | --- |
| R$ 2 (kira-kira hasil L2) | 125 poin | Mustahil, karena peluang awal hanya 55 poin |
| R$ 10 | 25 poin | Sulit, perlu bukti kuat |
| R$ 30 | 8,3 poin | Mungkin, tetapi harus diukur lewat uji coba |

Pelajarannya: keputusan sangat bergantung pada v. Itulah kenapa v diestimasi dari data (L2), bukan ditebak.

**D. Aturan rekomendasi**

- Rekomendasi **tegas** hanya jika strategi untung bersih di skenario dasar **dan** pesimis, dengan tingkat bukti skenario minimal B.
- Jika tidak, tulis: "belum cukup bukti untuk mengubah strategi; ini yang dibutuhkan untuk memutuskan", lalu arahkan ke uji coba (bagian E).
- Semua hasil disajikan sebagai rentang untung bersih (pesimis, dasar, optimis) dan titik impas, bukan satu angka.

**E. Rancangan uji coba (deliverable dua halaman)**

Dokumen ini mengubah asumsi tersisa menjadi sesuatu yang bisa diukur:
- **Hipotesis:** menghubungi pelanggan dini menurunkan peluang ulasan buruk pada pesanan berisiko tinggi.
- **Populasi dan pembagian:** pesanan yang ditandai model; dibagi acak dua kelompok, satu diberi tindakan, satu tidak.
- **Hasil utama:** porsi ulasan buruk. **Hasil pendamping:** pembelian ulang dan jumlah keluhan.
- **Ukuran sampel (perkiraan kasar):** untuk mendeteksi penurunan 5 poin (55% ke 50%) dibutuhkan sekitar **1.560 pesanan terlambat per kelompok**. Karena hanya 40% pesanan yang ditandai benar-benar terlambat, itu setara sekitar **3.900 pesanan ditandai per kelompok**.
- **Aturan berhenti dan pengaman:** tindakan tidak boleh merugikan pelanggan; uji dihentikan jika ada keluhan meningkat.
- **Aturan keputusan setelah uji:** lanjutkan hanya jika penurunan yang terukur melampaui titik impas.

- **Output:** tabel nilai tiga lapis, tabel strategi dengan rentang dan titik impas, satu halaman rekomendasi (atau "belum cukup bukti"), dokumen rancangan uji coba.
- **Gerbang G11:** nilai satu ulasan buruk dilaporkan dengan rentang dan sumbernya; semua asumsi tersisa tercantum dengan rentang; rancangan uji coba selesai.

### Langkah 12: Buka holdout, analisis kegagalan, Tabel Bukti (minggu 14)

- **Tujuan:** menguji hasil akhir secara jujur dan mengakui di mana model gagal.
- **Dikerjakan:**
  1. **Buka holdout satu kali.** Jalankan model terpilih apa adanya. Catat tanggal pembukaan dan hasilnya. Jika kinerja turun jauh dari validasi, laporkan penurunannya dan turunkan klaim; jangan melatih ulang berdasarkan holdout.
  2. **Analisis kegagalan:** potong galat per kategori, wilayah, bulan (November), ukuran seller, ada atau tidaknya teks ulasan. Cari pola ("model sering salah pada seller baru yang riwayatnya sedikit").
  3. **Daftar kegagalan:** tabel berisi kondisi, gejala, dugaan penyebab, bukti, mitigasi.
  4. **Pernyataan penggunaan:** satu halaman "kapan model tidak boleh dipakai" (contoh: seller dengan kurang dari 20 pesanan, kategori volume kecil, perubahan di luar jangkauan data).
  5. **Tabel Bukti:** tiap klaim penting dengan bukti, label, tingkat bukti, batasan, dan hasil. Angka kunci dibekukan untuk tes hasil beku (tes 7).
- **Gerbang G12:** holdout dibuka tepat satu kali; semua klaim di laporan punya baris di Tabel Bukti.

### Langkah 13: Kemas dan finalisasi engineering (minggu 15)

- **Dikerjakan:** laporan 10 sampai 12 halaman; presentasi 10 slide untuk non-teknis (masalah, temuan, dunia alternatif, rekomendasi dengan rentang, rancangan uji coba, batasan); README; kartu model semua model; catatan keputusan semua gerbang; versi HTML atau PDF notebook; **aplikasi lokal read-only** (empat halaman); satu perintah rebuild diuji dari awal; semua tes lulus.
- **Halaman aplikasi:** (1) kondisi bisnis dan forecast dengan rentang; (2) risiko pesanan dan seller; (3) dunia alternatif dengan slider dibatasi domain, label, dan tingkat bukti; (4) strategi, titik impas, dan halaman batasan.
- **Aturan integritas aplikasi:** angka prediksi selalu disertai rentang; label selalu tampak; skenario C bertuliskan "ilustratif, bukan dasar keputusan"; di luar domain tervalidasi muncul peringatan **EKSTRAPOLASI**; halaman batasan bisa diakses dari mana saja.
- **Gerbang G13:** orang di luar proyek bisa membangun ulang dari README dengan satu perintah, semua tes lulus (termasuk tes aplikasi), dan memahami presentasi tanpa penjelasan lisan.

---

## 6. Ringkasan Gerbang

| Gerbang | Pertanyaan | Jika gagal |
| --- | --- | --- |
| G0 | Masalah, definisi, dan ambang dikunci? | Jangan mulai modeling |
| G1 | Data valid dan jendela analisis jelas? | Perbaiki, persempit jendela, atau gabung kategori |
| G2 | EDA berujung keputusan, holdout aman? | Ulangi EDA yang kosong |
| G3 | Segmen stabil dan bisa dijelaskan? | Laporkan "tidak stabil" |
| G4 | Semua tes kebocoran lulus? | Perbaiki fitur; model dilarang dievaluasi |
| G5 | Forecast mengalahkan baseline sesuai aturan? | Pakai baseline; laporkan hasil nol |
| G6 | Model risiko keterlambatan mengalahkan aturan sederhana? | Rekomendasikan aturan sederhana |
| G7 | NLP menambah di atas bintang saja dan lolos plasebo? | Jadikan eksploratori |
| G8 | Asosiasi berbahasa klaim yang benar? | Tulis ulang kalimat sebab-akibat |
| G9 | Rantai terhubung mengalahkan model terpisah dan lolos jawaban-diketahui? | Turunkan klaim "world model" |
| G10 | Skenario bertingkat bukti dan berlabel? | Beri tingkat C atau buang |
| G11 | Nilai bisnis diestimasi dari data, asumsi tercantum, rancangan uji coba ada? | "Belum cukup bukti" |
| G12 | Holdout dibuka sekali, Tabel Bukti lengkap? | Laporkan penurunan, turunkan klaim |
| G13 | Orang lain bisa membangun ulang, semua tes lulus? | Perbaiki dokumentasi atau tes |

Gerbang yang gagal **tidak dilewati diam-diam**: tindakan perbaikan atau dokumentasi kegagalan dicatat di catatan keputusan.

---

## 7. Bonus (hanya jika Langkah 1 sampai 11 sudah selesai)

| Bonus | Isi | Nilai tambah | Risiko |
| --- | --- | --- | --- |
| **A: Uji kewarasan forecasting di M5** | Jalankan tangga model Langkah 5 pada subset M5 (misalnya satu kategori, satu negara bagian) dan bandingkan dengan baseline yang sama | Menunjukkan metode bekerja di data besar yang punya acuan publik | Mudah melebar; batasi 1 minggu |
| **B: Transfer NLP ke bahasa Indonesia (PRDECT-ID)** | Jalankan pipeline sentimen dan topik pada 5.400 ulasan Tokopedia; bandingkan TF-IDF + logistic regression dengan model bahasa Indonesia seperti IndoBERT jika perlu | Relevansi lokal untuk perekrut di Indonesia | Tanpa dimensi waktu; hanya menguji NLP |
| **C: Pembanding pelanggan (Dunnhumby)** | Segmentasi dan respons promosi pada data grosir | Memperluas cerita ke pelanggan dan promosi | Proyek terpisah; jangan digabung |
| **D: API tipis lokal** | Pembungkus tipis di atas modul untuk menyajikan hasil | Menunjukkan kemampuan menyajikan model | Itu wilayah engineer; tidak disarankan sebelum semua gerbang selesai |

---

## 8. Deliverable dan Struktur Repositori

| Deliverable | Keterangan |
| --- | --- |
| 1. Notebook utama | Laporan teknis bertahap per langkah (1 sampai 12), tipis, tiap bab diakhiri ringkasan gerbang, bisa dijalankan dari awal sampai akhir dengan hasil sama |
| 2. Modul kode | Logika per fungsi (bagian 4.1) |
| 3. Skrip SQL bernomor | Tiga tingkat data, tampilan fitur |
| 4. Tes otomatis | Delapan jenis tes (4.2), semua lulus |
| 5. Laporan kualitas data, rekonsiliasi, kamus data | Dengan tanggal ketersediaan tiap kolom |
| 6. Rencana analisis, catatan percobaan, catatan keputusan, kartu model | Dokumentasi proses |
| 7. Laporan akhir 10 sampai 12 halaman | Temuan, dunia alternatif, rekomendasi dengan rentang, batasan |
| 8. Tabel Bukti, daftar kegagalan, pernyataan penggunaan | Bagian dari laporan |
| 9. Rancangan uji coba | Dua halaman (Langkah 11E) |
| 10. Presentasi 10 slide | Untuk non-teknis |
| 11. Aplikasi lokal read-only | Empat halaman |
| 12. README | Tujuan, cara membangun ulang dengan satu perintah, status gerbang, batasan |

**Struktur folder:**

| Folder | Isi |
| --- | --- |
| data | Mentah (tidak di-commit), olahan, kamus data |
| sql | Skrip bernomor: mentah, bersih, mart, tampilan fitur |
| src | Modul: data, fitur as-of, NLP, model, evaluasi, world model, skenario, strategi, pelaporan |
| tests | Delapan jenis tes |
| notebooks | Notebook utama |
| config | Rencana analisis, jendela data, ambang gerbang, ruang strategi, asumsi biaya |
| experiments | Catatan percobaan dan catatan keputusan |
| artifacts | Hasil tersimpan bernomor (model, tabel, hasil skenario) yang dibaca aplikasi |
| reports | Laporan, presentasi, kartu model, HTML notebook, rancangan uji coba |
| app | Aplikasi lokal read-only |

---

## 9. Teknologi

| Teknologi | Peran | Status |
| --- | --- | --- |
| Python (pandas, NumPy), matplotlib/seaborn/Plotly | Olah data dan visualisasi | Inti |
| MySQL | Tiga tingkat data, tampilan fitur | Inti |
| scikit-learn | Model dasar, clustering, TF-IDF, pipeline | Inti |
| LightGBM | Model non-linier | Inti |
| statsmodels | Regresi dan interval kepercayaan | Inti |
| SHAP | Penjelasan model | Inti |
| Jupyter | Laporan teknis | Inti |
| pytest | Delapan jenis tes otomatis | Inti |
| Format dan pemeriksaan gaya kode (misalnya black dan ruff) | Kualitas kode, dijalankan lokal | Inti |
| Git | Riwayat perubahan | Inti |
| NLTK atau spaCy (Portugis), NMF/LDA | Praproses teks dan topik | Inti |
| Streamlit | Aplikasi lokal read-only | Inti (ringan) |
| Model BERT bahasa Portugis atau Indonesia | NLP lanjutan | Bersyarat: hanya jika TF-IDF mentok **dan** terbukti menambah |
| LSTM, Optuna | Model sekuensial, tuning | Bonus: hanya jika lolos aturan naik tangga |

Prinsip: teknologi masuk hanya jika memberi nilai yang bisa dibuktikan.

---

## 10. Linimasa (±15 minggu + 1 cadangan)

| Minggu | Kegiatan | Gerbang |
| --- | --- | --- |
| 1 | Langkah 0; setup repositori, MySQL, kerangka tes; mulai Langkah 1 | G0 |
| 2 | Langkah 1 selesai; potong holdout; mulai EDA | G1 |
| 3 | EDA selesai; segmentasi | G2, G3 |
| 4 | Fitur as-of dan tes kebocoran | G4 |
| 5 | Forecast | G5 |
| 6 | Model risiko keterlambatan | G6 |
| 7 | Model ulasan buruk, NLP dasar | |
| 8 | Tes nilai tambah NLP; penjelasan dan asosiasi | G7, G8 |
| 9 | World Model: blok B1 sampai B4 dan rollout | |
| 10 | World Model: uji U1, U2, U3 | G9 |
| 11 | Skenario S1 sampai S4, validasi, cek kejadian nyata | G10 |
| 12 | Nilai bisnis tiga lapis, estimasi nilai ulasan buruk, plafon | |
| 13 | Strategi, titik impas, rancangan uji coba | G11 |
| 14 | Holdout, analisis kegagalan, Tabel Bukti | G12 |
| 15 | Laporan, presentasi, aplikasi, README, rebuild satu perintah | G13 |
| 16 | Cadangan | |

**Garis potong MVP (jika waktu mepet), urutan yang dikorbankan:** bonus A sampai D → aplikasi lokal (diganti tangkapan layar di laporan) → skenario S3 dan S4 → segmentasi disederhanakan → World Model versi minimal (hanya rantai B2 ke B3, yaitu keterlambatan ke ulasan buruk, tetap dengan uji U1 dan U2). **Tidak boleh dikorbankan:** kualitas data, tes kebocoran, validasi waktu, holdout, tes otomatis dasar, Tabel Bukti, rekomendasi dengan rentang, rancangan uji coba.

**Asumsi beban kerja:** ±15 sampai 20 jam per minggu (total sekitar 260 sampai 320 jam). Jika waktu lebih sedikit, perpanjang linimasa; jangan mengurangi gerbang.

---

## 11. Risiko

| Risiko | Dampak | Mitigasi |
| --- | --- | --- |
| Lingkup membesar (engineering + World Model) | Proyek tidak selesai | Garis potong MVP; bonus hanya setelah Langkah 11; engineering dikerjakan bertahap sejak minggu 1 |
| Data mingguan kecil | Blok World Model berisik, model rumit overfit | Mulai dari baseline; 6 sampai 8 kategori; laporkan rentang; ambang tipis bukan syarat mutlak |
| Rantai terhubung tidak mengalahkan model terpisah | Tesis 3 gagal | Hasil negatif dilaporkan; sebutan diturunkan sesuai aturan U1 |
| Pelanggan membeli ulang sangat sedikit | Nilai satu ulasan buruk kecil; mata rantai terakhir lemah | Dilaporkan sebagai temuan; efek reputasi dilaporkan terpisah sebagai asumsi |
| Efektivitas intervensi tidak bisa diukur dari data | Dampak bisnis tetap perkiraan | Titik impas dan rancangan uji coba; klaim dibatasi "diperkirakan dengan rentang" |
| NLP tidak menambah | Tesis 2 gagal | Hasil nol sah; pembanding bintang dan plasebo; topik keluhan tetap bernilai deskriptif |
| Ulasan berbahasa Portugis, label lemah | Sentimen berisik | Tidak diterjemahkan; keterbatasan ditulis; periksa topik manual |
| Kebocoran tak terdeteksi | Metrik menyesatkan | Audit tanggal, kontrol positif, tes acak target, holdout terkunci |
| Skenario dibaca sebagai ramalan | Overclaim | Tingkat bukti A/B/C, label wajib, batas domain |
| Data hanya 2016 sampai 2018 dan dari Brasil | Validitas eksternal terbatas | Tulis jelas di batasan; bonus B untuk konteks Indonesia |
| Lisensi data | Masalah saat publikasi | Cek lisensi Olist dan PRDECT-ID sebelum publikasi |

---

## 12. Definition of Done

- [ ] Rencana analisis tertulis dan dikunci sebelum modeling (G0)
- [ ] Tiga tingkat data, laporan kualitas, rekonsiliasi, dan kamus data (dengan tanggal ketersediaan) lengkap (G1)
- [ ] Holdout dipotong sebelum EDA, dibuka tepat satu kali, hasil dilaporkan apa adanya (G2, G12)
- [ ] Semua tes kebocoran lulus, termasuk kontrol positif dan acak target (G4)
- [ ] Forecast dibandingkan dengan baseline sesuai aturan naik tangga; ada rentang dan pengecekan cakupannya (G5)
- [ ] Model risiko keterlambatan dibandingkan dengan aturan sederhana; hasil T0 vs T1 dilaporkan (G6)
- [ ] Tes NLP A/B/C/plasebo selesai dengan keputusan tertulis (G7)
- [ ] Tidak ada kalimat sebab-akibat tanpa dasar; semua tabel dan grafik berlabel (G8)
- [ ] World Model: uji rantai vs terpisah (U1), jawaban-diketahui (U2), dan replay (U3) selesai dan dilaporkan (G9)
- [ ] Skenario berlabel dan bertingkat bukti A/B/C; cek terhadap kejadian nyata dilakukan (G10)
- [ ] Nilai satu ulasan buruk diestimasi dari data dengan rentang; plafon dampak dan titik impas dihitung; rancangan uji coba selesai (G11)
- [ ] Rekomendasi (atau "belum cukup bukti") dengan rentang pesimis, dasar, optimis
- [ ] Analisis kegagalan, daftar kegagalan, dan pernyataan penggunaan selesai
- [ ] Tabel Bukti terisi penuh dan angka kuncinya dibekukan
- [ ] Delapan jenis tes otomatis lulus dengan satu perintah
- [ ] Satu perintah membangun ulang dari data mentah sampai tabel hasil dan grafik
- [ ] Kartu model, catatan percobaan, dan catatan keputusan lengkap
- [ ] Aplikasi lokal memenuhi aturan integritas (rentang, label, peringatan ekstrapolasi, halaman batasan)
- [ ] README, laporan, dan presentasi dipahami orang di luar proyek (G13)
- [ ] Lisensi data dicek sebelum publikasi

---

## 13. Cara Menceritakan Proyek (CV dan Wawancara)

**Kerangka cerita (3 menit):**
1. Masalah bisnis dan keputusan yang ingin didukung.
2. Satu temuan yang paling mengejutkan (contoh: "sebagian besar ulasan buruk justru datang dari pesanan yang tepat waktu", **jika** hasil analisis memang menunjukkan itu).
3. Bagaimana memastikan hasil tidak palsu: validasi waktu, tes kebocoran, holdout satu kali, uji dengan jawaban yang sudah diketahui.
4. Dunia alternatif dan rekomendasi dengan rentang dan titik impas.
5. Apa yang tidak bisa disimpulkan, dan bagaimana uji coba akan menutup celahnya.

**Poin CV (isi angka hanya setelah hasil nyata ada; jangan menulis angka sebelum dihitung):**
- Membangun proyek DS end-to-end atas ±100 ribu pesanan marketplace: data bertingkat di SQL, tes otomatis kebocoran dan identitas data, kode modular yang bisa dibangun ulang dengan satu perintah.
- Model risiko keterlambatan menangkap **[X]%** pesanan terlambat dengan menandai **[Y]%** pesanan teratas (lift **[Z]** kali dibanding acak) pada titik **[T0/T1]**.
- Membangun rantai model terhubung (permintaan, keterlambatan, ulasan buruk) dan mengujinya terhadap model terpisah, data tiruan berjawaban diketahui, dan replay kejadian nyata; hasil: **[hasil]**.
- Mengestimasi nilai satu ulasan buruk dari data pembelian ulang (**[nilai dan rentang]**) dan menghitung titik impas intervensi; menyusun rancangan uji coba dengan perkiraan ukuran sampel.

**Pertanyaan wawancara yang akan siap dijawab:** kenapa tidak split acak; apa itu leakage dan buktinya di proyek ini; kenapa WAPE dan PR-AUC; kenapa NLP "tidak menang" (atau menang) dan bagaimana tahu; apa bedanya asosiasi dan sebab-akibat; mengapa dampak bisnis tidak diklaim terukur dan bagaimana mengukurnya; apa yang dilakukan jika rantai terhubung kalah dari model terpisah.

---

## 14. Hal yang Perlu Dipelajari Tambahan

Semuanya turunan dari materi bootcamp, dan bisa dipelajari tersebar selama proyek (±1 sampai 2 minggu total).

| Topik | Dipakai di |
| --- | --- |
| Fitur lag dan validasi time series | Langkah 4, 5, 9 |
| SQL lanjutan (CTE, window function, view) | Langkah 1, 4 |
| pytest dasar dan struktur modul Python | Bagian 4 |
| TF-IDF, NMF atau LDA | Langkah 7 |
| SHAP | Langkah 8 |
| Mengundi ulang kesalahan masa lalu (bootstrap sederhana) | Langkah 9 |
| Perkiraan ukuran sampel uji coba | Langkah 11 |

---

## Sumber Dataset

- Olist Brazilian E-Commerce Public Dataset: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- M5 Forecasting (Walmart): https://www.kaggle.com/c/m5-forecasting-accuracy
- Corporación Favorita (Store Sales Time Series Forecasting), Kaggle
- Dunnhumby, The Complete Journey: https://www.dunnhumby.com/source-files/
- Amazon Reviews 2023 (McAuley Lab): https://amazon-reviews-2023.github.io/
- PRDECT-ID (Tokopedia): https://data.mendeley.com/datasets/574v66hf2v dan https://www.kaggle.com/datasets/jocelyndumlao/prdect-id-indonesian-emotion-classification
