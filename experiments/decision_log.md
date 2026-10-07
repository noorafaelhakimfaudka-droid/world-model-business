# Decision Log (Catatan Keputusan Proyek)

Dokumen ini mencatat setiap keputusan metodologi, perubahan rencana, atau penyesuaian kriteria yang disepakati selama proyek. Tidak ada perubahan yang dilakukan diam-diam.

| ID | Tanggal | Langkah / Gerbang | Keputusan | Alasan / Konteks | Dampak |
|---|---|---|---|---|---|
| DEC-001 | 2026-10-07 | Langkah 0 / G0 | Mengadopsi arsitektur proyek dan 13 langkah dari PRD v1.0 | Menyelaraskan roadmap DS end-to-end dengan fokus keputusan bisnis, anti-leakage, dan world model terhubung | Seluruh alur kerja mengikuti PRD_WMFB_Olist.md |
| DEC-002 | 2026-10-07 | Langkah 0 / G0 | Struktur repositori modular sesuai PRD §8 | Memisahkan data, modul logika (src), tes otomatis (tests), konfigurasi (config), dan pelaporan (reports) | Kode dapat direproduksi dan diaudit dengan jelas |
| DEC-003 | 2026-10-07 | Langkah 1 / G1 | Menggunakan SQLite lokal sebagai database engine 3 lapisan data (raw, clean, mart) | CLI MySQL tidak terpasang di host; SQLite bawaan Python stabil, portabel, mendukung penuh CTE, Window Function, View tanpa mengubah logika DS di PRD | Skrip SQL di folder sql/ menggunakan dialek SQLite |
