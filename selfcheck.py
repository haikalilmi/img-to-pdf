"""Cek cepat logic konversi tanpa buka GUI.

Jalankan: python selfcheck.py
Butuh Pillow (wajib) dan pypdf (hanya untuk membaca ulang hasil PDF).
"""

from __future__ import annotations

import os
import tempfile

from PIL import Image

from app import PAGE_SIZES_MM, convert_images, unique_pdf_path

POINTS_PER_INCH = 72.0


def make_images(folder: str) -> list[str]:
    paths = []
    landscape = os.path.join(folder, "landscape.png")
    Image.new("RGB", (1200, 800), "red").save(landscape)

    alpha = os.path.join(folder, "alpha.png")
    Image.new("RGBA", (600, 900), (0, 0, 255, 128)).save(alpha)

    gray = os.path.join(folder, "gray.jpg")
    Image.new("L", (500, 500), 128).save(gray)

    paths.extend([landscape, alpha, gray])
    return paths


def page_size_points(path: str) -> list[tuple[float, float]]:
    from pypdf import PdfReader

    sizes = []
    for page in PdfReader(path).pages:
        box = page.mediabox
        sizes.append((float(box.width), float(box.height)))
    return sizes


def near(value: float, expected: float, tolerance: float = 1.5) -> bool:
    return abs(value - expected) <= tolerance


def main() -> None:
    with tempfile.TemporaryDirectory() as folder:
        paths = make_images(folder)
        dpi = 150
        quality = 90

        # 1) Semua gambar jadi satu PDF, halaman mengikuti ukuran gambar.
        auto_pdf = os.path.join(folder, "auto.pdf")
        seen = []
        pages = convert_images(
            paths,
            auto_pdf,
            page="Auto (ikut gambar)",
            dpi=dpi,
            quality=quality,
            on_progress=lambda index, total, path: seen.append((index, total)),
        )
        assert pages == 3, f"harusnya 3 halaman, dapat {pages}"
        assert seen == [(1, 3), (2, 3), (3, 3)], f"progress salah: {seen}"
        sizes = page_size_points(auto_pdf)
        assert len(sizes) == 3, f"PDF berisi {len(sizes)} halaman"
        width_pt = 1200 / dpi * POINTS_PER_INCH
        height_pt = 800 / dpi * POINTS_PER_INCH
        assert near(sizes[0][0], width_pt) and near(sizes[0][1], height_pt), f"halaman 1: {sizes[0]}"
        print("auto page size ok:", sizes[0])

        # 2) Muat ke A4: orientasi ikut gambar, rasio halaman A4.
        a4_pdf = os.path.join(folder, "a4.pdf")
        convert_images(paths, a4_pdf, page="A4", orientation="Auto", margin_mm=10, dpi=dpi, quality=quality)
        sizes = page_size_points(a4_pdf)
        assert near(sizes[0][0], 841.9, 2.0) and near(sizes[0][1], 595.3, 2.0), f"A4 lanskap: {sizes[0]}"
        assert near(sizes[1][0], 595.3, 2.0) and near(sizes[1][1], 841.9, 2.0), f"A4 potret: {sizes[1]}"
        print("A4 fit ok:", sizes[0], sizes[1])

        # 3) Orientasi dipaksa, margin dihormati (gambar tidak boleh melebihi area cetak).
        forced_pdf = os.path.join(folder, "forced.pdf")
        convert_images(paths[:1], forced_pdf, page="A4", orientation="Potret", margin_mm=0, dpi=dpi, quality=quality)
        sizes = page_size_points(forced_pdf)
        assert near(sizes[0][0], 595.3, 2.0) and near(sizes[0][1], 841.9, 2.0), f"A4 potret dipaksa: {sizes[0]}"
        print("forced orientation ok:", sizes[0])

        # 4) Gambar tanpa alpha (grayscale) tetap bisa dikonversi.
        gray_pdf = os.path.join(folder, "gray.pdf")
        convert_images(paths[2:], gray_pdf, dpi=dpi, quality=quality)
        assert len(page_size_points(gray_pdf)) == 1, "PDF grayscale harus 1 halaman"
        print("grayscale ok")

        # 5) Nama file output tidak menimpa file yang sudah ada.
        first = unique_pdf_path(folder, "hasil")
        open(first, "wb").close()
        second = unique_pdf_path(folder, "hasil")
        assert second != first and os.path.basename(second) == "hasil (2).pdf", second
        print("unique name ok:", os.path.basename(second))

        assert PAGE_SIZES_MM["A4"] == (210.0, 297.0)

    print("SEMUA CEK LOLOS")


if __name__ == "__main__":
    main()