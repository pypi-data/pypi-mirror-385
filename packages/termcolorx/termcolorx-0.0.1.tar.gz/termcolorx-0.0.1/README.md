# 🎨 TermColorX — Advanced Terminal Color, Gradient, and Animation Library

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-%3E%3D3.13-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20MacOS-yellow)

> **TermColorX** adalah library Python modern yang dibuat **dari dasar** untuk memberikan pengalaman terminal yang penuh warna 🌈, interaktif ⚙️, dan dinamis 🎬.  
> Termasuk dukungan **ANSI**, **RGB**, **Gradien**, **Animasi Asinkron (asyncio)**, **Logger Berwarna**, dan **Deteksi Otomatis Platform**.

---

## 🚀 Fitur Utama

| Fitur | Deskripsi |
|-------|------------|
| 🎨 **Pewarnaan ANSI Lengkap** | Ubah warna teks, latar belakang, dan gaya (bold, italic, underline, dll). |
| 🌈 **Efek Gradien Dinamis** | Tampilkan teks dengan efek pelangi, gradien vertikal, horizontal, dan animasi RGB bergerak. |
| 🌀 **Animasi Terminal Lengkap** | Spinner, efek mengetik, progress bar, loading dots, animasi multi-baris, hingga versi asinkron (non-blocking). |
| 🧾 **Logger Berwarna & File Output** | Cetak pesan berwarna sesuai level (INFO, WARNING, ERROR, SUCCESS, dll) dan simpan ke file log. |
| ⚙️ **Integrasi `asyncio`** | Jalankan animasi tanpa menghalangi proses utama. |
| 💾 **Deteksi Dukungan Warna Platform** | Kompatibel di Windows, Linux, dan macOS dengan aktivasi ANSI otomatis. |

---

## 📦 Instalasi

Instal menggunakan pip:

```bash
pip install termcolorx
```

Atau instal langsung dari GitHub (versi terbaru):

```bash
pip install git+https://github.com/Athallah1234/termcolorx.git
```

---

## 🧠 Struktur Modul

```bash
termcolorx/
│
├── termcolorx/
│   ├── __init__.py
│   ├── color.py          # Pewarna teks & RGB
│   ├── logger.py         # Logger berwarna otomatis
│   ├── platform.py       # Deteksi sistem operasi & ANSI
│   ├── gradient.py       # Efek gradien pelangi
│   ├── animation.py      # Efek teks berjalan & spinner
│
├── examples/
│   └── demo.py           # Contoh penggunaan lengkap
│
├── setup.py
└── README.md
```

---

## 🧩 Import Dasar
```python
from termcolorx import TermColorX, Gradient, Animation, LoggerColor, PlatformSupport
```

---

## 🎨 Pewarnaan Dasar (color.py)
```python
from termcolorx import TermColorX

print(TermColorX.red("Ini teks merah"))
print(TermColorX.green("Sukses!"))
print(TermColorX.colorize("Bold & Underline", fg="blue", style="bold"))
print(TermColorX.rgb("RGB Warna!", 255, 100, 50))
print(TermColorX.color256("256 Color Mode!", 196))
```

## 🌟 Gaya dan Warna Lengkap:
- **Gaya**: ``bold``, ``italic``, ``underline``, ``dim``, ``blink``, ``reverse``, ``hidden``
- **Warna**: ``black``, ``red``, ``green``, ``yellow``, ``blue``, ``magenta``, ``cyan``, ``white``

---

## 🌈 Gradien & Efek Pelangi (gradient.py)

**Efek Pelangi**
```python
from termcolorx import Gradient

print(Gradient.rainbow("Hello TermColorX! 🌈"))
```

**Gradien Horizontal**
```python
text = "Gradient Horizontal Example"
print(Gradient.horizontal_gradient(text, (255, 0, 0), (0, 0, 255)))
```

**Gradien Vertikal**
```python
text = "Line 1\nLine 2\nLine 3"
print(Gradient.vertical_gradient(text, (0, 255, 0), (255, 0, 255)))
```

🔁 **Gradien Dinamis (Async)**
```python
import asyncio
from termcolorx import Gradient

asyncio.run(Gradient.rainbow_dynamic("Dynamic Rainbow ✨", delay=0.1))
```

---

## 🌀 Efek Animasi Terminal (animation.py)

**Efek Mengetik (Typing)**
```python
from termcolorx import Animation

Animation.typing("Memproses data...", delay=0.05, color="cyan")
```

**Spinner**
```python
Animation.spinner(duration=3, color="yellow")
```

**Progress Bar**
```python
Animation.progress_bar(total=40, duration=5, color="green")
```

**Animasi Gabungan (Typing + Spinner)**
```python
Animation.type_and_spinner("Loading Project...", typing_delay=0.05, spinner_duration=3)
```

**Loading dengan Pesan**
```python
Animation.loading_message("Mengunduh file", dots=5, dot_delay=0.4, color="magenta")
```

**Multi-line Typing**
```python
lines = ["Mempersiapkan...", "Menghubungkan server...", "Selesai!"]
Animation.multiline_typing(lines, delay=0.05, color="cyan")
```

🔁 **Versi Asinkron (asyncio)**
```python
import asyncio

async def main():
    await Animation.async_spinner("Sedang Memproses...", duration=3)
    await Animation.async_progress_with_message("Loading Data", total=20, duration=4)
    await Animation.async_multiline_typing(["Baris 1", "Baris 2", "Baris 3"])

asyncio.run(main())
```

---

## 🧾 Logger Berwarna (logger.py)

**Contoh Penggunaan**
```python
from termcolorx import LoggerColor

logger = LoggerColor(log_file="output.log")

logger.info("Sistem berjalan normal.")
logger.warning("Memori hampir penuh!")
logger.error("Gagal menghubungkan ke server.")
logger.success("Proses selesai dengan sukses!")
logger.debug("Variabel x = 42")
logger.critical("Kesalahan fatal terdeteksi!")
```

📁 **Output ke file:**
```less
2025-10-19 10:30:00 [INFO] Sistem berjalan normal.
2025-10-19 10:30:05 [ERROR] Gagal menghubungkan ke server.
```

---

## ⚙️ Deteksi Platform (platform.py)
```python
from termcolorx import PlatformSupport

PlatformSupport.enable_ansi()  # Aktifkan ANSI di Windows
print(PlatformSupport.info())
```

**Output Contoh:**
```python
{
    'os': 'Windows',
    'version': '10.0.22631',
    'ansi_supported': True
}
```

---

## 💫 Integrasi Async Lengkap
Semua metode async pada ``Animation`` dan ``Gradient`` dapat digabungkan agar animasi tidak menghalangi proses lain.

```python
import asyncio
from termcolorx import Animation, Gradient

async def show_effects():
    await asyncio.gather(
        Gradient.rainbow_dynamic("🌈 Warna Bergerak", delay=0.1),
        Animation.async_spinner("⌛ Memproses...", duration=5)
    )

asyncio.run(show_effects())
```

---

## 🧱 Contoh Proyek Mini

```python
from termcolorx import TermColorX, Animation, Gradient, LoggerColor

log = LoggerColor()

Animation.typing("Menjalankan sistem...", color="cyan")
print(Gradient.rainbow("TermColorX aktif! 🚀"))
log.success("Inisialisasi sukses.")
Animation.spinner(2)
Animation.progress_bar(total=20, duration=3)
log.info("Proses selesai tanpa error.")
```

---

## 📚 Dukungan & Dokumentasi

📖 Dokumentasi lengkap tersedia di:
👉 [https://github.com/Athallah1234/termcolorx](https://github.com/Athallah1234/termcolorx)

Jika kamu ingin berkontribusi:

1. Fork repositori.
2. Tambahkan fitur baru.
3. Kirim Pull Request ❤️

---

## 🧑‍💻 Author

👤 ATHALLAH RAJENDRA PUTRA JUNIARTO
📧 Email: athallahwork50@gmail.com
🌍 GitHub: [Athallah1234](https://github.com/Athallah1234)

## ⚖️ Lisensi

MIT License © 2025 — ATHALLAH RAJENDRA PUTRA JUNIARTO
> Bebas digunakan untuk proyek pribadi, komersial, atau open-source dengan menyertakan atribusi.

## ⭐ Dukung Proyek Ini

Jika kamu menyukai TermColorX:
- Beri ⭐ di [GitHub Repo](https://github.com/Athallah1234/termcolorx)
- Bagikan ke komunitas Python
- Gunakan di proyekmu!