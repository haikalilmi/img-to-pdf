# SRD (Software Requirements Specification) — IMG TO PDF

| Atribut | Isi |
|---|---|
| Nama perangkat lunak | IMG TO PDF |
| Versi dokumen | 1.0 |
| Tanggal | 11 September 2026 |
| Acuan | PRD IMG TO PDF v1.0 |
| Status | Disetujui untuk implementasi |

> Dokumen ini merinci kebutuhan perangkat lunak sebelum implementasi. Penomoran SRS-Fxx menelusuri ke PRD-Fxx.

## 1. Pendahuluan

### 1.1 Tujuan
Menetapkan kebutuhan fungsional, antarmuka, data, non-fungsional, dan pengujian aplikasi desktop konversi gambar ke PDF, sebagai kontrak kerja implementasi dan pengujian.

### 1.2 Lingkup
Satu aplikasi desktop Python + tkinter (`app.py`), satu skrip uji (`selfcheck.py`), satu file dependency (`requirements.txt`). Tidak ada server, database, atau layanan jaringan.

### 1.3 Definisi
- **Mode gabungan (`one`)**: n gambar → 1 file PDF, urutan halaman = urutan daftar.
- **Mode per-file (`each`)**: n gambar → n file PDF di satu folder.
- **Auto page**: ukuran halaman PDF mengikuti dimensi piksel gambar.
- **DPI**: dots per inch; menentukan ukuran fisik halaman PDF.

## 2. Deskripsi Umum

### 2.1 Konteks sistem
Aplikasi standalone. Input: berkas gambar lokal. Output: berkas PDF lokal. Semua pemrosesan di memori lokal via Pillow; tidak ada komponen eksternal saat runtime.

### 2.2 Karakteristik pengguna
Pengguna umum, terbiasa dengan dialog buka/simpan file. Tidak diperlukan akun, pelatihan, atau koneksi internet.

### 2.3 Batasan desain
1. Runtime hanya boleh bergantung padastdlib + `Pillow >= 10.0`.
2. GUI memakai `tkinter/ttk` bawaan Python (tanpa framework tambahan).
3. Ukuran jendela awal 820×640, minimum 700×560.
4. Konversi wajib di thread pekerja agar UI tidak freeze.

## 3. Kebutuhan Fungsional

### SRS-F01 — Tambah gambar (← PRD-F01)
- Input: dialog `askopenfilenames` dengan filter `*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff` + `*.*`.
- Proses: normalisasi ke absolute path; path yang sudah ada di daftar diabaikan.
- Output: daftar bertambah; status `"{total} gambar dalam daftar ({baru} baru)."`.
- Error: dialog dibatalkan → tidak ada perubahan.

### SRS-F02 — Kelola urutan dan isi daftar (← PRD-F02)
- Naik/Turun: menggeser item terpilih sebesar ±1; seleksi multi-item yang berdekatan bergerak sebagai blok; item di tepi atau bertabrakan dengan seleksi lain tidak bergerak.
- Hapus: menghapus semua item terpilih (dari indeks terbesar agar stabil).
- Bersihkan: mengosongkan seluruh daftar; status kembali `Belum ada gambar.`
- Tampilan daftar: `"{nomor}. {basename}"` dengan scrollbar vertikal.

### SRS-F03 — Mode output (← PRD-F03)
- `one`: output berupa path file `.pdf` (dialog `asksaveasfilename`, nama awal = basename gambar pertama + `.pdf`, default `hasil.pdf` bila daftar kosong).
- `each`: output berupa path folder (dialog `askdirectory`; folder dibuat bila belum ada via `makedirs exist_ok`).
- Ganti mode mengosongkan field output dan mengganti label (`File PDF:` vs `Folder output:`).

### SRS-F04 — Ukuran halaman (← PRD-F04)
- Pilihan: `Auto (ikut gambar)` → `None`; `A4` → (210.0, 297.0); `Letter` → (215.9, 279.4); `Legal` → (215.9, 355.6) mm.
- Mode Auto: halaman = dimensi gambar apa adanya.
- Mode tetap: `fit_to_page` — gambar di-scale dengan `ImageOps.contain` (LANCZOS, rasio dipertahankan) ke kotak cetak (halaman − 2×margin), lalu ditempel di tengah halaman putih.

### SRS-F05 — Orientasi (← PRD-F05)
- Pilihan: `Auto`, `Potret`, `Lanskap`.
- Auto pada halaman tetap: landscape bila `width > height`, selain itu potret (menukar lebar–tinggi ukuran kertas). Potret/Lanskap memaksa arah tersebut.
- Pada mode Auto page, orientasi tidak berpengaruh.

### SRS-F06 — Margin, DPI, kualitas (← PRD-F06, PRD-F07)
- Margin: float (mm), koma/titik desimal diterima, minimal 0.
- DPI: integer, rentang valid 30–1200. Konversi mm→px: `round(mm / 25.4 * dpi)`.
- Kualitas: integer 50–100 via slider.
- Validasi gagal → `messagebox.showwarning` dan proses dibatalkan (lihat §6).

### SRS-F07 — Koreksi gambar otomatis (← PRD-F08)
- `load_image(path)`: buka via Pillow → `exif_transpose` → bila mode `RGB` langsung pakai; bila ada kanal alpha → composite ke latar putih; selain itu konversi ke `RGB`.
- Jaminan: tidak ada latar hitam akibat alpha; foto EXIF tegak.

### SRS-F08 — Eksekusi background + progres (← PRD-F09)
- Klik Konversi → validasi → thread daemon `_worker` berjalan; tombol Tambah/Naik/Turun/Hapus/Bersihkan/Konversi/Pilih dinonaktifkan (`_set_busy`).
- Callback `on_progress(index, total, path)` dipanggil per halaman; event `progress/done/error/idle` dikirim via `queue.Queue` dan diproses UI tiap 100 ms (`_drain_events`).
- Progress bar maksimum = jumlah gambar; status `Mengonversi i/n...`; selesai → `Selesai.` + `showinfo`; gagal → `Gagal.` + `showerror`.

### SRS-F09 — Proteksi output (← PRD-F10)
- Mode `one`: bila target ada → `askyesno Timpa file?`; Tolak → batal.
- Mode `each`: nama file `unique_pdf_path(folder, stem)`; bila `stem.pdf` ada → `stem (2).pdf`, `(3)`, dst.
- Mode `each` menolak target yang merupakan file (bukan direktori) dengan `showerror`.

### SRS-F10 — Penyimpanan PDF (← PRD-F03)
- `save_pdf(pages, out, dpi, quality)`: `first.save(out, "PDF", save_all=True, append_images=rest, resolution=dpi, quality=quality)`.
- `convert_images(...)` mengembalikan jumlah halaman; melempar `ValueError` bila daftar kosong.

### SRS-F11 — Validasi dan pesan (← PRD-F11)
Urutan validasi pada `start()`: (1) daftar kosong → `Belum ada gambar`; (2) output kosong → `Output kosong`; (3) angka salah → `Input salah`; (4) margin < 0 atau DPI di luar rentang → `Input salah`; (5) target per-file bukan direktori → `Output salah`. Semua memakai `messagebox`, tanpa exception ke pengguna.

### SRS-F12 — Skrip verifikasi (← PRD-F12)
`selfcheck.py` (butuh tambahan `pypdf` hanya saat uji) wajib mencakup: (1) gabungan 3 gambar → 3 halaman + callback progres [(1,3),(2,3),(3,3)] + ukuran halaman halaman-1 = 1200×800 px pada 150 DPI; (2) A4 margin 10: landscape→landscape, potret→potret (±2 pt); (3) orientasi paksa Potret; (4) grayscale 1 halaman; (5) `unique_pdf_path` menghasilkan `hasil (2).pdf`; (6) konstanta A4 = (210.0, 297.0).

## 4. Kebutuhan Antarmuka

### 4.1 Antarmuka pengguna (spesifikasi layout)
Jendela `ImageToPdfApp` berisi vertikal: toolbar [Tambah Gambar][Naik][Turun][Hapus][Bersihkan] → Listbox + scrollbar → grup `Opsi` (Mode radio 2 pilihan; Ukuran halaman + Orientasi combobox readonly; Margin + DPI entry; Kualitas JPEG slider 50–100 + label nilai) → grup `Simpan` (label dinamis + entry + tombol Pilih...) → baris progress + tombol Konversi → label status.

### 4.2 Antarmuka berkas
- Input terbaca: PNG, JPEG, BMP, WEBP, TIFF (sesuai kemampuan Pillow).
- Output: PDF 1.3+ via Pillow, halaman RGB, kompresi JPEG sesuai parameter kualitas; resolusi metadata = DPI.

## 5. Kebutuhan Non-Fungsional

- SRS-N01 Kinerja (← PRD-N01): lihat kriteria PRD §8; polling event 100 ms.
- SRS-N02 Portabilitas (← PRD-N03): Python 3.10+, murni tkinter + Pillow; path memakai `os.path.abspath`.
- SRS-N03 Keandalan (← PRD-N04): exception di worker ditangkap (`Exception → error event`), UI tidak mati; `finally` selalu mengirim `idle` agar tombol aktif kembali.
- SRS-N04 Keamanan/privasi (← PRD-N05): tanpa socket, tanpa API key, tanpa tulis di luar target pengguna.
- SRS-N05 Keterbatasan terdokumentasi (← PRD-N06): render-ulang JPEG; saran kualitas 100 / DPI 300 untuk teks kecil.

## 6. Aturan Validasi (ringkasan)

| Field | Aturan | Pesan |
|---|---|---|
| Daftar gambar | ≥ 1 item | `Belum ada gambar` |
| Output | tidak kosong | `Output kosong` |
| Margin/DPI/kualitas | numerik | `Input salah` |
| Margin | ≥ 0 | `Input salah` |
| DPI | 30 ≤ dpi ≤ 1200 | `Input salah` |
| Target per-file | harus direktori | `Output salah` |

## 7. Arsitektur dan Modul

`app.py` — fungsi murni: `mm_to_px`, `load_image`, `page_pixel_size`, `fit_to_page`, `save_pdf`, `convert_images`, `unique_pdf_path`; kelas `ImageToPdfApp(tk.Tk)` untuk seluruh UI + orkestrasi thread (`start`, `_worker`, `_on_page`, `_drain_events`, `_set_busy`). Tidak ada modul lain. Dependensi: `requirements.txt` = `pillow>=10.0`.

## 8. Matriks Keterlacakan

| PRD | SRS | diverifikasi oleh |
|---|---|---|
| PRD-F01 | SRS-F01 | selfcheck §1 + uji manual tambah |
| PRD-F02 | SRS-F02 | uji manual Naik/Turun/Hapus/Bersihkan |
| PRD-F03 | SRS-F03, SRS-F10 | selfcheck §1 + uji manual dua mode |
| PRD-F04 | SRS-F04 | selfcheck §2 |
| PRD-F05 | SRS-F05 | selfcheck §2, §3 |
| PRD-F06 | SRS-F06 | selfcheck §2 + uji batas DPI/margin |
| PRD-F07 | SRS-F06 | uji slider 50–100 |
| PRD-F08 | SRS-F07 | selfcheck §1 (alpha), foto EXIF manual |
| PRD-F09 | SRS-F08 | uji manual progress + tombol nonaktif |
| PRD-F10 | SRS-F09 | selfcheck §5 + uji timpa |
| PRD-F11 | SRS-F11 | uji tiap pesan |
| PRD-F12 | SRS-F12 | `python selfcheck.py` → `SEMUA CEK LOLOS` |

## 9. Kriteria Penerimaan
Sama dengan PRD §8; pelulusan dinyatakan bila seluruh baris matriks §8 terpenuhi pada Python 3.10+ di minimal satu OS (Windows prioritas).
