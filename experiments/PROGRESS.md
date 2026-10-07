# Progress Proyek: World Model for Business (Olist)

## Status Terkini
- **Langkah Aktif**: Langkah 0: Kunci Masalah dan Aturan Main (PRD §5 Langkah 0)
- **Status Gerbang**: 
  - G0: ✅ LULUS (Definisi, metrik, rencana analisis terkunci, tes repositori 3/3 lulus)
  - G1: ⏳ BERIKUTNYA (Lapisan data dan cek kualitas)
  - G2 s.d. G13: ⏸️ BELUM DIMULAI

## Yang Sudah Dipahami
- Peran data scientist pemula dan prinsip transparansi/kejujuran metodologi.
- Prinsip validasi berbasis waktu dan pagar holdout (tidak boleh diintip sebelum Langkah 12).
- Konsep pencegahan kebocoran data (leakage) dan titik prediksi waktu T0, T1, T2.
- Mengunci definisi istilah ("terlambat", "ulasan buruk") dan kriteria sukses sebelum memegang data atau model.
- Alur pengujian kontrak repositori dengan pytest.

## Yang Masih Goyah / Perlu Pendalaman
- Mekanisme teknis rollout World Model dan bootstrap undian acak (Langkah 9).
- Formula penentuan ukuran sampel uji coba intervensi bisnis (Langkah 11).

## Tugas Saat Ini & Berikutnya
- [x] Inisialisasi struktur repositori dan folder kerja (PRD §8).
- [x] Menyusun dokumen pernyataan masalah bisnis (docs/problem_statement.md).
- [x] Menyusun tabel definisi istilah dan aturan metrik (config/analysis_plan.md).
- [x] Menyusun rencana analisis dan ambang gerbang G0-G13 (config/analysis_plan.md).
- [x] Menyiapkan kerangka tes otomatis awal dan pengujian pytest (tests/test_initial_contracts.py).
- [x] Gerbang G0 Lulus.
- [ ] Menuju Langkah 1: Lapisan data dan cek kualitas.

## Pertanyaan Terbuka / Keputusan Pending
- Pilihan engine database untuk lapisan data bertingkat Langkah 1: MySQL (jika diinstal secara lokal) atau SQLite / DuckDB dengan interface SQL standar (perlu konfirmasi saat menuju Langkah 1).
