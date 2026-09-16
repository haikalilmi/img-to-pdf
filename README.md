# IMG TO PDF

Aplikasi desktop Python + tkinter untuk mengubah gambar (PNG, JPG, BMP, WEBP, TIFF)
menjadi file PDF.

## Fitur

- Tambah banyak gambar sekaligus, atur urutannya (Naik / Turun / Hapus / Bersihkan).
- Dua mode output:
  - **Semua gambar jadi satu PDF** — urutan di daftar menentukan urutan halaman.
  - **Satu PDF per gambar** — simpan ke folder pilihan, nama file mengikuti nama gambar.
- Ukuran halaman: Auto (mengikuti ukuran gambar), A4, Letter, atau Legal.
- Orientasi halaman: Auto, Potret, atau Lanskap.
- Margin dalam milimeter dan nilai DPI untuk menentukan ukuran fisik halaman.
- Slider kualitas JPEG (50-100) untuk mengatur besar file vs mutu gambar.
- Orientasi foto diperbaiki otomatis dari data EXIF, dan transparansi (alpha)
  diratakan ke latar putih supaya tidak jadi hitam di PDF.
- Konversi berjalan di thread terpisah, jadi jendela tidak membeku dan ada progress bar.

## Cara pakai

```bash
pip install -r requirements.txt
python app.py
```

Langkah:

1. Klik **Tambah Gambar** dan pilih satu atau beberapa file gambar.
2. Pilih mode output, ukuran halaman, orientasi, margin, dan DPI.
3. Klik **Pilih...** untuk menentukan lokasi file atau folder hasil.
4. Klik **Konversi** dan tunggu sampai muncul notifikasi selesai.

## Cek cepat tanpa GUI

```bash
python selfcheck.py
```

Skrip ini membuat gambar contoh di folder sementara, mengonversinya, lalu memeriksa
jumlah halaman dan ukuran halaman hasil dengan `pypdf`. Skrip ini butuh `pypdf`
(hanya untuk pengecekan, aplikasi utama tidak membutuhkannya):

```bash
pip install pypdf
```

## Catatan

- Aplikasi hanya memakai Pillow, tanpa dependency tambahan.
- Pillow menyimpan halaman PDF sebagai kompresi JPEG, jadi gambar dirender ulang
  dan tidak di-embed lossless. Untuk gambar berisi teks kecil atau grafik garis,
  naikkan nilai kualitas ke 100 atau DPI ke 300 supaya lebih tajam.
- Kalau nanti ukuran file terasa kelewat besar, opsi berikutnya adalah mengganti
  mesin PDF ke `img2pdf`, yang menyematkan JPEG asli tanpa render ulang.
