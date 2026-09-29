"""
  BLOK 1 : Import & konstanta global
  BLOK 2 : Fungsi inti konversi (logika murni, tanpa GUI)
  BLOK 3 : Kelas GUI ImageToPdfApp (tampilan + interaksi + thread)
  BLOK 4 : Entry point program
"""

# ======================================================================
# BLOK 1: IMPORT & KONSTANTA GLOBAL — AWAL
# Tugas blok: menyiapkan semua kebutuhan dasar — library standar (os,
#   threading, queue), tkinter untuk GUI, Pillow untuk olah gambar,
#   serta konstanta format file, ukuran kertas, dan orientasi.
# ======================================================================

from __future__ import annotations

import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageOps

IMAGE_FILETYPES = [
    ("Gambar", "*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff"),
    ("Semua file", "*.*"),
]

# None = ukuran halaman mengikuti ukuran gambar
PAGE_SIZES_MM = {
    "Auto (ikut gambar)": None,
    "A4": (210.0, 297.0),
    "Letter": (215.9, 279.4),
    "Legal": (215.9, 355.6),
}

ORIENTATIONS = ("Auto", "Potret", "Lanskap")
MM_PER_INCH = 25.4

# ======================================================================
# BLOK 1: IMPORT & KONSTANTA GLOBAL — AKHIR
# ======================================================================


# ======================================================================
# BLOK 2: FUNGSI INTI KONVERSI — AWAL
# Tugas blok: logika murni tanpa GUI — memuat gambar, menghitung ukuran
#   halaman, menata gambar ke halaman, menyimpan PDF, dan membuat nama
#   file unik. Blok ini yang diuji otomatis oleh selfcheck.py.
# ======================================================================

# ----- Fungsi 2.1: mm_to_px — AWAL -----
# Tugas: mengubah milimeter ke piksel berdasarkan DPI.
def mm_to_px(mm: float, dpi: int) -> int:
    return max(0, round(mm / MM_PER_INCH * dpi))
# ----- Fungsi 2.1: mm_to_px — AKHIR -----


# ----- Fungsi 2.2: load_image — AWAL -----
# Tugas: membuka gambar, membetulkan orientasi EXIF, meratakan
#   transparansi (alpha) ke latar putih agar tidak jadi hitam di PDF.
def load_image(path: str) -> Image.Image:
    """Buka gambar, betulkan orientasi EXIF, ratakan alpha ke latar putih."""
    image = Image.open(path)
    image = ImageOps.exif_transpose(image)
    if image.mode == "RGB":
        return image
    if "A" in image.getbands():
        rgba = image.convert("RGBA")
        background = Image.new("RGB", rgba.size, "white")
        background.paste(rgba, mask=rgba.getchannel("A"))
        return background
    return image.convert("RGB")
# ----- Fungsi 2.2: load_image — AKHIR -----


# ----- Fungsi 2.3: page_pixel_size — AWAL -----
# Tugas: menghitung lebar-tinggi halaman dalam piksel dari ukuran
#   milimeter + DPI, dengan opsi tukar sisi untuk lanskap.
def page_pixel_size(size_mm: tuple[float, float], dpi: int, landscape: bool) -> tuple[int, int]:
    width_mm, height_mm = size_mm
    if landscape:
        width_mm, height_mm = height_mm, width_mm
    return mm_to_px(width_mm, dpi), mm_to_px(height_mm, dpi)
# ----- Fungsi 2.3: page_pixel_size — AKHIR -----


# ----- Fungsi 2.4: fit_to_page — AWAL -----
# Tugas: menempatkan gambar di tengah halaman berukuran tetap (mis. A4)
#   dengan rasio aspek tetap terjaga (contain + tempel tengah).
def fit_to_page(
    image: Image.Image,
    size_mm: tuple[float, float],
    margin_mm: float,
    dpi: int,
    orientation: str,
) -> Image.Image:
    """Tempatkan gambar di tengah halaman berukuran tetap, rasio tetap dijaga."""
    if orientation == "Potret":
        landscape = False
    elif orientation == "Lanskap":
        landscape = True
    else:
        landscape = image.width > image.height

    page_w, page_h = page_pixel_size(size_mm, dpi, landscape)
    pad = mm_to_px(margin_mm, dpi)
    box = (max(1, page_w - 2 * pad), max(1, page_h - 2 * pad))
    fitted = ImageOps.contain(image, box, Image.Resampling.LANCZOS)

    page = Image.new("RGB", (page_w, page_h), "white")
    page.paste(fitted, ((page_w - fitted.width) // 2, (page_h - fitted.height) // 2))
    return page
# ----- Fungsi 2.4: fit_to_page — AKHIR -----


# ----- Fungsi 2.5: save_pdf — AWAL -----
# Tugas: menyimpan daftar halaman (Pillow Image) menjadi satu file PDF.
def save_pdf(pages: list[Image.Image], out_path: str, dpi: int, quality: int) -> None:
    first, *rest = pages
    first.save(
        out_path,
        "PDF",
        save_all=True,
        append_images=rest,
        resolution=dpi,
        quality=quality,
    )
# ----- Fungsi 2.5: save_pdf — AKHIR -----


# ----- Fungsi 2.6: convert_images — AWAL -----
# Tugas: orkestrasi utama — memuat tiap gambar, (opsional) menatanya ke
#   halaman tetap, menyimpan PDF, melaporkan progres. Mengembalikan
#   jumlah halaman yang dihasilkan.
def convert_images(
    paths: list[str],
    out_path: str,
    page: str = "Auto (ikut gambar)",
    orientation: str = "Auto",
    margin_mm: float = 0.0,
    dpi: int = 150,
    quality: int = 90,
    on_progress=None,
) -> int:
    """Konversi daftar gambar menjadi satu PDF. Mengembalikan jumlah halaman."""
    if not paths:
        raise ValueError("Tidak ada gambar untuk dikonversi.")

    size_mm = PAGE_SIZES_MM[page]
    pages: list[Image.Image] = []
    for index, path in enumerate(paths, start=1):
        image = load_image(path)
        if size_mm is not None:
            image = fit_to_page(image, size_mm, margin_mm, dpi, orientation)
        pages.append(image)
        if on_progress is not None:
            on_progress(index, len(paths), path)

    save_pdf(pages, out_path, dpi, quality)
    return len(pages)
# ----- Fungsi 2.6: convert_images — AKHIR -----


# ----- Fungsi 2.7: unique_pdf_path — AWAL -----
# Tugas: membuat nama file PDF yang unik (hasil.pdf, hasil (2).pdf, ...)
#   agar file lama tidak tertimpa diam-diam.
def unique_pdf_path(folder: str, stem: str) -> str:
    """Nama file unik agar PDF dengan nama sama tidak saling menimpa."""
    candidate = os.path.join(folder, f"{stem}.pdf")
    number = 2
    while os.path.exists(candidate):
        candidate = os.path.join(folder, f"{stem} ({number}).pdf")
        number += 1
    return candidate
# ----- Fungsi 2.7: unique_pdf_path — AKHIR -----

# ======================================================================
# BLOK 2: FUNGSI INTI KONVERSI — AKHIR
# ======================================================================


# ======================================================================
# BLOK 3: KELAS GUI (ImageToPdfApp) — AWAL
# Tugas blok: seluruh tampilan dan interaksi — daftar gambar, panel opsi,
#   pemilihan output, tombol konversi — plus thread pekerja agar jendela
#   tidak membeku, dengan komunikasi thread lewat queue + event.
# ======================================================================

class ImageToPdfApp(tk.Tk):
    """Jendela utama aplikasi."""

    # ----- Sub-blok 3.1: Inisialisasi & state — AWAL -----
    # Tugas: judul/ukuran jendela, variabel opsi (mode, halaman, orientasi,
    #   margin, DPI, kualitas, output, status), daftar path, antrean event,
    #   dan penjadwalan pompa event tiap 100 ms.
    def __init__(self) -> None:
        super().__init__()
        self.title("IMG TO PDF")
        self.geometry("820x640")
        self.minsize(700, 560)

        self.paths: list[str] = []
        self.events: queue.Queue = queue.Queue()
        self.busy = False

        self.mode = tk.StringVar(value="one")
        self.page = tk.StringVar(value="Auto (ikut gambar)")
        self.orientation = tk.StringVar(value="Auto")
        self.margin = tk.StringVar(value="0")
        self.dpi = tk.StringVar(value="150")
        self.quality = tk.IntVar(value=90)
        self.output = tk.StringVar()
        self.status = tk.StringVar(value="Belum ada gambar.")

        self._build_widgets()
        self.after(100, self._drain_events)
    # ----- Sub-blok 3.1: Inisialisasi & state — AKHIR -----

    # ----- Sub-blok 3.2: Pembangunan tampilan — AWAL -----
    # Tugas: menyusun toolbar (Tambah/Naik/Turun/Hapus/Bersihkan),
    #   listbox + scrollbar, panel Opsi, panel Simpan, progress bar,
    #   tombol Konversi, dan label status.

    def _build_widgets(self) -> None:
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(root)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.add_button = ttk.Button(toolbar, text="Tambah Gambar", command=self.add_images)
        self.add_button.pack(side="left")
        self.up_button = ttk.Button(toolbar, text="Naik", command=lambda: self.move(-1))
        self.up_button.pack(side="left", padx=(6, 0))
        self.down_button = ttk.Button(toolbar, text="Turun", command=lambda: self.move(1))
        self.down_button.pack(side="left", padx=(6, 0))
        self.remove_button = ttk.Button(toolbar, text="Hapus", command=self.remove_selected)
        self.remove_button.pack(side="left", padx=(6, 0))
        self.clear_button = ttk.Button(toolbar, text="Bersihkan", command=self.clear_all)
        self.clear_button.pack(side="left", padx=(6, 0))

        list_frame = ttk.Frame(root)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.listbox = tk.Listbox(list_frame, selectmode="extended", activestyle="none")
        self.listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.listbox.configure(yscrollcommand=scrollbar.set)

        options = ttk.LabelFrame(root, text="Opsi", padding=10)
        options.grid(row=2, column=0, sticky="ew", pady=8)
        options.columnconfigure(1, weight=1)
        options.columnconfigure(3, weight=1)

        ttk.Label(options, text="Mode").grid(row=0, column=0, sticky="w", padx=(0, 6))
        mode_frame = ttk.Frame(options)
        mode_frame.grid(row=0, column=1, columnspan=3, sticky="w")
        ttk.Radiobutton(
            mode_frame, text="Semua gambar jadi satu PDF", value="one",
            variable=self.mode, command=self._mode_changed,
        ).pack(side="left", padx=(0, 12))
        ttk.Radiobutton(
            mode_frame, text="Satu PDF per gambar", value="each",
            variable=self.mode, command=self._mode_changed,
        ).pack(side="left")

        ttk.Label(options, text="Ukuran halaman").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Combobox(
            options, textvariable=self.page, values=list(PAGE_SIZES_MM), state="readonly",
        ).grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=4)

        ttk.Label(options, text="Orientasi").grid(row=1, column=2, sticky="w", pady=4)
        ttk.Combobox(
            options, textvariable=self.orientation, values=list(ORIENTATIONS), state="readonly",
        ).grid(row=1, column=3, sticky="ew", pady=4)

        ttk.Label(options, text="Margin (mm)").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(options, textvariable=self.margin, width=10).grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(options, text="DPI").grid(row=2, column=2, sticky="w", pady=4)
        ttk.Entry(options, textvariable=self.dpi, width=10).grid(row=2, column=3, sticky="w", pady=4)

        ttk.Label(options, text="Kualitas JPEG").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Scale(options, from_=50, to=100, variable=self.quality, orient="horizontal").grid(
            row=3, column=1, columnspan=2, sticky="ew", pady=4,
        )
        ttk.Label(options, textvariable=self.quality).grid(row=3, column=3, sticky="w")

        output_frame = ttk.LabelFrame(root, text="Simpan", padding=10)
        output_frame.grid(row=3, column=0, sticky="ew")
        output_frame.columnconfigure(0, weight=1)
        self.output_label = ttk.Label(output_frame, text="File PDF:")
        self.output_label.grid(row=0, column=0, sticky="w")
        output_row = ttk.Frame(output_frame)
        output_row.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        output_row.columnconfigure(0, weight=1)
        ttk.Entry(output_row, textvariable=self.output).grid(row=0, column=0, sticky="ew")
        self.browse_button = ttk.Button(output_row, text="Pilih...", command=self.choose_output)
        self.browse_button.grid(row=0, column=1, padx=(6, 0))

        action = ttk.Frame(root)
        action.grid(row=4, column=0, sticky="ew", pady=8)
        action.columnconfigure(0, weight=1)
        self.progress = ttk.Progressbar(action, mode="determinate")
        self.progress.grid(row=0, column=0, sticky="ew")
        self.run_button = ttk.Button(action, text="Konversi", command=self.start)
        self.run_button.grid(row=0, column=1, padx=(8, 0))

        ttk.Label(root, textvariable=self.status, anchor="w").grid(row=5, column=0, sticky="ew")

    # ----- Sub-blok 3.2: Pembangunan tampilan — AKHIR -----

    # ----- Sub-blok 3.3: Kelola daftar gambar — AWAL -----
    # Tugas: tambah (multi-pilih, cegah duplikat), geser urutan Naik/Turun
    #   (mendukung multi-seleksi), hapus pilihan, bersihkan semua, dan
    #   menggambar ulang isi listbox.

    def add_images(self) -> None:
        selected = filedialog.askopenfilenames(title="Pilih gambar", filetypes=IMAGE_FILETYPES)
        if not selected:
            return
        existing = set(self.paths)
        added = 0
        for path in selected:
            path = os.path.abspath(path)
            if path not in existing:
                self.paths.append(path)
                existing.add(path)
                added += 1
        self._refresh_list()
        self.status.set(f"{len(self.paths)} gambar dalam daftar ({added} baru).")

    def move(self, delta: int) -> None:
        selection = list(self.listbox.curselection())
        if not selection:
            return
        order = selection if delta < 0 else list(reversed(selection))
        landed: list[int] = []
        for index in order:
            target = index + delta
            if target < 0 or target >= len(self.paths) or target in selection:
                landed.append(index)
                continue
            self.paths[index], self.paths[target] = self.paths[target], self.paths[index]
            landed.append(target)
        self._refresh_list()
        for index in landed:
            self.listbox.selection_set(index)

    def remove_selected(self) -> None:
        selection = list(self.listbox.curselection())
        if not selection:
            return
        for index in reversed(selection):
            del self.paths[index]
        self._refresh_list()
        self.status.set(f"{len(self.paths)} gambar dalam daftar.")

    def clear_all(self) -> None:
        self.paths.clear()
        self._refresh_list()

    def _refresh_list(self) -> None:
        self.listbox.delete(0, "end")
        for index, path in enumerate(self.paths, start=1):
            self.listbox.insert("end", f"{index}. {os.path.basename(path)}")
        if not self.paths:
            self.status.set("Belum ada gambar.")

    # ----- Sub-blok 3.3: Kelola daftar gambar — AKHIR -----

    # ----- Sub-blok 3.4: Penentuan output — AWAL -----
    # Tugas: menyesuaikan label/field saat mode berubah, dan membuka
    #   dialog yang tepat — simpan file PDF (mode gabungan) atau pilih
    #   folder (mode per-file).

    def _mode_changed(self) -> None:
        per_file = self.mode.get() == "each"
        self.output_label.configure(text="Folder output:" if per_file else "File PDF:")
        self.output.set("")

    def choose_output(self) -> None:
        if self.mode.get() == "each":
            folder = filedialog.askdirectory(title="Pilih folder output")
            if folder:
                self.output.set(os.path.abspath(folder))
            return
        default = "hasil.pdf"
        if self.paths:
            default = os.path.splitext(os.path.basename(self.paths[0]))[0] + ".pdf"
        target = filedialog.asksaveasfilename(
            title="Simpan PDF",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=default,
        )
        if target:
            self.output.set(os.path.abspath(target))

    # ----- Sub-blok 3.4: Penentuan output — AKHIR -----

    # ----- Sub-blok 3.5: Validasi & thread konversi — AWAL -----
    # Tugas: memeriksa input (daftar, output, angka margin/DPI/kualitas),
    #   menyiapkan job, menjalankan _worker di thread daemon, dan
    #   mengirim hasil/progres lewat antrean event (tidak menyentuh
    #   widget langsung dari thread).

    def _read_options(self) -> tuple[float, int, int] | None:
        try:
            margin = float(self.margin.get().replace(",", ".") or 0)
            dpi = int(float(self.dpi.get() or 150))
            quality = int(self.quality.get())
        except ValueError:
            messagebox.showwarning("Input salah", "Margin, DPI, dan kualitas harus berupa angka.")
            return None
        if margin < 0 or not 30 <= dpi <= 1200:
            messagebox.showwarning("Input salah", "Margin minimal 0 mm dan DPI antara 30 sampai 1200.")
            return None
        return margin, dpi, quality

    def start(self) -> None:
        if self.busy:
            return
        if not self.paths:
            messagebox.showwarning("Belum ada gambar", "Tambahkan gambar dulu.")
            return
        target = self.output.get().strip()
        if not target:
            messagebox.showwarning("Output kosong", "Pilih file atau folder output dulu.")
            return
        options = self._read_options()
        if options is None:
            return
        margin, dpi, quality = options

        per_file = self.mode.get() == "each"
        if per_file:
            if os.path.exists(target) and not os.path.isdir(target):
                messagebox.showerror("Output salah", "Folder output tidak valid.")
                return
            os.makedirs(target, exist_ok=True)
        elif os.path.exists(target) and not messagebox.askyesno(
            "Timpa file?", f"{os.path.basename(target)} sudah ada. Timpa?"
        ):
            return

        job = {
            "paths": list(self.paths),
            "target": target,
            "per_file": per_file,
            "page": self.page.get(),
            "orientation": self.orientation.get(),
            "margin": margin,
            "dpi": dpi,
            "quality": quality,
        }
        self._set_busy(True)
        self.progress.configure(maximum=len(job["paths"]), value=0)
        self.status.set("Mengonversi...")
        threading.Thread(target=self._worker, args=(job,), daemon=True).start()

    def _worker(self, job: dict) -> None:
        common = {
            "page": job["page"],
            "orientation": job["orientation"],
            "margin_mm": job["margin"],
            "dpi": job["dpi"],
            "quality": job["quality"],
        }
        try:
            if job["per_file"]:
                for index, path in enumerate(job["paths"], start=1):
                    stem = os.path.splitext(os.path.basename(path))[0]
                    convert_images([path], unique_pdf_path(job["target"], stem), **common)
                    self.events.put(("progress", index, len(job["paths"])))
                message = f"{len(job['paths'])} PDF tersimpan di:\n{job['target']}"
            else:
                count = convert_images(job["paths"], job["target"], on_progress=self._on_page, **common)
                message = f"{count} halaman tersimpan ke:\n{job['target']}"
            self.events.put(("done", message))
        except Exception as exc:  # tampilkan ke pengguna, jangan matikan UI
            self.events.put(("error", f"{type(exc).__name__}: {exc}"))
        finally:
            self.events.put(("idle", None))

    def _on_page(self, index: int, total: int, path: str) -> None:
        self.events.put(("progress", index, total))

    # ----- Sub-blok 3.5: Validasi & thread konversi — AKHIR -----

    # ----- Sub-blok 3.6: Pompa event & status sibuk — AWAL -----
    # Tugas: _drain_events menguras antrean tiap 100 ms dan memutakhirkan
    #   progress/status/dialog dari thread utama; _set_busy mengunci/
    #   membuka tombol dan me-reset progress bar.

    def _drain_events(self) -> None:
        try:
            while True:
                kind, *payload = self.events.get_nowait()
                if kind == "progress":
                    index, total = payload
                    self.progress.configure(value=index)
                    self.status.set(f"Mengonversi {index}/{total}...")
                elif kind == "done":
                    self.status.set("Selesai.")
                    messagebox.showinfo("Selesai", payload[0])
                elif kind == "error":
                    self.status.set("Gagal.")
                    messagebox.showerror("Gagal", payload[0])
                elif kind == "idle":
                    self._set_busy(False)
        except queue.Empty:
            pass
        self.after(100, self._drain_events)

    def _set_busy(self, busy: bool) -> None:
        self.busy = busy
        state = "disabled" if busy else "normal"
        for button in (
            self.add_button, self.up_button, self.down_button, self.remove_button,
            self.clear_button, self.run_button, self.browse_button,
        ):
            button.configure(state=state)
        if not busy:
            self.progress.configure(value=0)

    # ----- Sub-blok 3.6: Pompa event & status sibuk — AKHIR -----

# ======================================================================
# BLOK 3: KELAS GUI (ImageToPdfApp) — AKHIR
# ======================================================================


# ======================================================================
# BLOK 4: ENTRY POINT — AWAL
# Tugas blok: titik masuk program — membuat jendela utama dan menjalankan
#   event loop tkinter. Blok ini yang dieksekusi saat `python app.py`.
# ======================================================================

def main() -> None:
    ImageToPdfApp().mainloop()


if __name__ == "__main__":
    main()

# ======================================================================
# BLOK 4: ENTRY POINT — AKHIR
# ======================================================================
