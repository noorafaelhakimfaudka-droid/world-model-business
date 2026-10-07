# Progress Proyek: World Model for Business (Olist)

## Status Terkini
- **Langkah Aktif**: Langkah 1 Selesai -> Menuju Langkah 2: Potong Holdout, lalu EDA (PRD §5 Langkah 2)
- **Status Gerbang**: 
  - G0: ✅ LULUS (Definisi, metrik, rencana analisis terkunci, tes repositori 3/3 lulus)
  - G1: ✅ LULUS (Lapisan data raw-clean-mart terintegrasi, 10/10 tes kontrak data lulus, rekonsiliasi baris tervalidasi)
  - G2: ⏳ BERIKUTNYA (Potong holdout terkunci & EDA kondisi bisnis)
  - G3 s.d. G13: ⏸️ BELUM DIMULAI

## Yang Sudah Dipahami
- Peran data scientist pemula dan prinsip transparansi/kejujuran metodologi.
- Prinsip validasi berbasis waktu dan pagar holdout (tidak boleh diintip sebelum Langkah 12).
- Konsep pencegahan kebocoran data (leakage) dan audit titik ketersediaan fitur (T0, T1, T2).
- Mengunci definisi istilah ("terlambat", "ulasan buruk") dan kriteria sukses sebelum memegang data atau model.
- Arsitektur data bertingkat (Raw -> Clean -> Mart) di SQLite dengan skrip SQL bernomor.
- Rekonsiliasi baris dan ambang toleransi anomali (8 baris anomali dibuang = 0,008% < 0,5%).
- Pengujian kontrak data otomatis dengan pytest (10 passed).

## Yang Masih Goyah / Perlu Pendalaman
- Pemotongan holdout 8 minggu terakhir dengan hashing SHA-256 sebelum EDA (Langkah 2).
- Mekanisme teknis rollout World Model dan bootstrap undian acak (Langkah 9).
- Formula penentuan ukuran sampel uji coba intervensi bisnis (Langkah 11).

## Tugas Saat Ini & Berikutnya
- [x] Inisialisasi struktur repositori dan folder kerja (PRD §8).
- [x] Menyusun dokumen pernyataan masalah bisnis (docs/problem_statement.md).
- [x] Menyusun tabel definisi istilah dan aturan metrik (config/analysis_plan.md).
- [x] Menyusun rencana analisis dan ambang gerbang G0-G13 (config/analysis_plan.md).
- [x] Menyiapkan kerangka tes otomatis awal dan pengujian pytest (tests/test_initial_contracts.py).
- [x] Gerbang G0 Lulus.
- [x] Menempatkan 9 berkas CSV Olist di data/raw/.
- [x] Membuat skrip SQL bernomor: 01_raw.sql, 02_clean.sql, 03_mart.sql.
- [x] Profiling data & verifikasi angka PRD (pembelian ulang, baris per tingkat, tanggal ketersediaan).
- [x] Membangun database SQLite bertingkat (data/processed/olist.db) via src/data/build_database.py.
- [x] Kamus data dengan tanggal ketersediaan (docs/data_dictionary.md).
- [x] Laporan kualitas data & rekonsiliasi baris (reports/data_quality_report.md).
- [x] Tes kontrak data otomatis (tests/test_data_contracts.py) — 10/10 lulus.
- [x] Gerbang G1 Lulus.
- [ ] Langkah 2: Potong holdout terkunci (8 minggu terakhir) dan catat checksum SHA-256 sebelum EDA.

## Pertanyaan Terbuka / Keputusan Pending
- Selesai (DEC-003: SQLite lokal untuk 3 lapis data).
