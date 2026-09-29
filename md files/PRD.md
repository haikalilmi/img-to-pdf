# PRD — IMG TO PDF

| Atribut | Isi |
|---|---|
| Nama produk | IMG TO PDF |
| Versi dokumen | 1.0 |
| Tanggal | 10 September 2026 |
| Status | Disetujui untuk pengembangan MVP |
| Penulis | Tim Pengembang |

> Dokumen ini disusun sebelum implementasi sebagai acuan pembangunan aplikasi.

## 1. Latar Belakang dan Masalah

Pengguna (mahasiswa, guru, staf administrasi) sering perlu menggabungkan foto/scan tugas, nota, atau dokumen menjadi satu file PDF untuk dikumpulkan atau diarsipkan. Aplikasi yang ada umumnya: (a) berbasis web sehingga mengharuskan upload dokumen sensitif, (b) berbayar/watermark, atau (c) tidak bisa mengatur urutan halaman dan ukuran kertas.

Dibutuhkan aplikasi desktop offline, gratis, dan sederhana untuk mengubah kumpulan gambar menjadi PDF dengan urutan dan ukuran halaman yang terkendali.

## 2. Tujuan Produk

1. Mengonversi satu atau banyak gambar menjadi file PDF secara offline.
2. Memberi kendali atas urutan halaman, ukuran kertas, orientasi, margin, DPI, dan kualitas kompresi.
3. Tetap responsif (UI tidak membeku) selama konversi dan memberi umpan balik progres.
4. Instalasi semudah mungkin: Python + satu dependency (`Pillow`).

## 3. Target Pengguna

| Persona | Kebutuhan |
|---|---|
| Mahasiswa / siswa | Scan tugas foto HP menjadi satu PDF rapi berurutan. |
| Guru / dosen | Arsip foto kegiatan/dokumen ke PDF. |
| Staf / umum | Konversi cepat tanpa upload ke internet. |

Karakteristik: pengguna umum, tidak diasumsikan paham teknis. Semua aksi harus bisa dilakukan lewat tombol dan dialog file standar.

## 4. Ruang Lingkup MVP

### Masuk lingkup (In Scope)

- PRD-F01: Tambah banyak gambar sekaligus (PNG, JPG/JPEG, BMP, WEBP, TIF/TIFF).
- PRD-F02: Kelola daftar: ubah urutan (Naik/Turun), Hapus pilihan, Bersihkan semua, cegah duplikat.
- PRD-F03: Mode output: (a) semua gambar jadi satu PDF, (b) satu PDF per gambar ke folder.
- PRD-F04: Ukuran halaman: Auto (ikut gambar), A4 (210 × 297 mm), Letter (215,9 × 279,4 mm), Legal (215,9 × 355,6 mm).
- PRD-F05: Orientasi: Auto (ikut bentuk gambar), Potret, Lanskap.
- PRD-F06: Margin (mm) dan DPI (30–1200) untuk ukuran fisik halaman.
- PRD-F07: Kualitas JPEG 50–100 (slider) untuk tradeoff ukuran file vs ketajaman.
- PRD-F08: Koreksi otomatis: orientasi EXIF dan flatten transparansi (alpha) ke latar putih.
- PRD-F09: Konversi di background thread + progress bar + status; tombol dinonaktifkan saat sibuk.
- PRD-F10: Proteksi output: konfirmasi timpa file; nama unik otomatis (`nama (2).pdf`) pada mode per-file.
- PRD-F11: Validasi input dengan pesan yang jelas (daftar kosong, output kosong, angka salah, folder salah).
- PRD-F12: Skrip cek otomatis tanpa GUI (`selfcheck.py`) untuk verifikasi logika konversi.

### Di luar lingkup (Out of Scope)

- Edit gambar (crop, rotate manual, filter), OCR, gabung/kompres PDF yang sudah ada.
- Drag-and-drop, pratinjau thumbnail, multi-bahasa.
- Installer biner (.exe) — cukup `python app.py`.

## 5. User Stories

1. Sebagai mahasiswa, saya ingin memilih banyak foto sekaligus agar tidak input satu per satu.
2. Sebagai mahasiswa, saya ingin mengatur urutan foto agar halaman PDF sesuai urutan tugas.
3. Sebagai pengguna, saya ingin memilih satu PDF gabungan atau satu PDF per gambar.
4. Sebagai pengguna, saya ingin memilih ukuran kertas A4 agar hasil cetak sesuai standar.
5. Sebagai pengguna, saya ingin tahu progres konversi agar tidak mengira aplikasi macet.
6. Sebagai pengguna, saya ingin file lama tidak tertimpa diam-diam.

## 6. Alur Pengguna (Happy Path)

1. Klik **Tambah Gambar** → dialog file (multi-select) → daftar terisi `1. nama.jpg`, dst.
2. (Opsional) Seleksi item → **Naik/Turun/Hapus**; atur Mode, Ukuran halaman, Orientasi, Margin, DPI, Kualitas.
3. Klik **Pilih...** → mode gabungan: dialog simpan `.pdf` (nama awal mengikuti gambar pertama); mode per-file: dialog pilih folder.
4. Klik **Konversi** → progress bar berjalan, status `Mengonversi i/n...`.
5. Dialog **Selesai** menampilkan lokasi hasil; dialog **Gagal** menampilkan jenis dan pesan error.

## 7. Kebutuhan Non-Fungsional

- PRD-N01 Kinerja: konversi 10 gambar 12 MP selesai < 60 detik di laptop standar; UI tetap responsif (refresh status ≤ 100 ms).
- PRD-N02 Kegunaan: pengguna baru menyelesaikan konversi pertama tanpa panduan dalam < 5 menit.
- PRD-N03 Kompatibilitas: Windows 10+, Linux, macOS; Python 3.10+; dependency runtime hanya `Pillow >= 10.0`.
- PRD-N04 Keandalan: satu gambar rusak menghentikan job dengan pesan jelas (tidak crash diam-diam); tidak ada file setengah jadi yang diklaim sukses.
- PRD-N05 Privasi: 100% offline; tidak ada jaringan/telemetri.
- PRD-N06 Keterbatasan yang diketahui: halaman PDF dirender ulang sebagai JPEG (bukan embed lossless); teks kecil disarankan kualitas 100 / DPI 300.

## 8. Kriteria Penerimaan (Acceptance Criteria)

1. 3 gambar contoh (landscape, RGBA, grayscale) → 1 PDF 3 halaman, ukuran halaman sesuai DPI.
2. Mode A4 + margin 10 mm: gambar landscape menghasilkan halaman landscape, potret menghasilkan potret, rasio A4 terjaga.
3. Orientasi dipaksa Potret selalu menghasilkan halaman potret.
4. Gambar RGBA tidak menghasilkan latar hitam di PDF.
5. File `hasil.pdf` yang sudah ada tidak tertimpa tanpa konfirmasi; mode per-file menghasilkan `hasil (2).pdf` bila bentrok.
6. DPI di luar 30–1200 atau margin negatif ditolak dengan peringatan.
7. Selama konversi tombol aksi nonaktif dan progress bar terisi 0 → n.
8. `python selfcheck.py` lolos semua cek (butuh tambahan `pypdf` hanya untuk pengujian).

## 9. Asumsi dan Risiko

| # | Asumsi / Risiko | Mitigasi |
|---|---|---|
| 1 | Pillow tersedia dan mendukung format yang dijanjikan | Kunci `pillow>=10.0` di `requirements.txt` |
| 2 | Foto HP membawa tag EXIF orientasi | Terapkan `exif_transpose` sebelum proses |
| 3 | PDF dari Pillow memakai kompresi JPEG (lossy) | Dokumentasikan di README + saran kualitas/DPI; opsi `img2pdf` sebagai pengembangan lanjutan |
| 4 | Pengguna memilih gambar sangat besar (OOM) | Proses sekuensial per halaman; dokumentasikan batas wajar |

## 10. Rencana Rilis

- v1.0 (MVP, dokumen ini): seluruh PRD-F01 s.d. PRD-F12.
- Berikutnya (bukan komitmen): drag-and-drop, pratinjau, mesin `img2pdf` opsional untuk file lebih kecil, build `.exe`.
