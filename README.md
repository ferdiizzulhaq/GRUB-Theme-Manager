# GRUB Theme Manager v5.0 🎨

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.x-green.svg)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Fedora%2043-red.svg)](https://getfedora.org/)
[![GitHub stars](https://img.shields.io/github/stars/username/grub-theme-manager.svg)](https://github.com/username/grub-theme-manager/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/username/grub-theme-manager.svg)](https://github.com/username/grub-theme-manager/issues)
[![GitHub forks](https://img.shields.io/github/forks/username/grub-theme-manager.svg)](https://github.com/username/grub-theme-manager/network)

Aplikasi GUI lengkap untuk mengelola tema dan konfigurasi GRUB dengan dukungan multi-bahasa.

## 📸 Screenshot

```
┌─────────────────────────────────────────────────────────────┐
│  GRUB Theme Manager v5.0 - Fedora 43         [UEFI] 🌐 EN  │
├─────────────────────────────────────────────────────────────┤
│  🎨 Tema  │  ⚙️ Settings  │  💾 Backup  │  🔧 Advanced    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Tema Aktif: Vimix                                           │
│                                                               │
│  Tema Terinstall:                                            │
│  ┌─────────────────────────────────────────────────┐        │
│  │ • Breeze                                         │        │
│  │ • Grub2-themes                                   │        │
│  │ • Vimix                                          │        │
│  └─────────────────────────────────────────────────┘        │
│  [✓ Terapkan] [🔍 Validasi] [👁 Preview] [🗑 Hapus]        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```
![Main Page](https://github.com/ferdiizzulhaq/GRUB-Theme-Manager/blob/main/screenshots/main-window.png)

## ✨ Fitur Utama

### 🌍 Multi-Language Support

- 🇮🇩 **Bahasa Indonesia** (Default)
- 🇬🇧 **English**
- 🇸🇦 **العربية (Arabic)**
- 🇨🇳 **中文 (Chinese/Mandarin)**

### 🎨 Manajemen Tema

- ✅ Install tema baru dari folder lokal
- ✅ Terapkan tema dengan backup otomatis
- ✅ Validasi struktur tema sebelum instalasi
- ✅ Preview tema menggunakan QEMU (grub2-theme-preview)
- ✅ Hapus tema yang tidak digunakan
- ✅ Deteksi dan list semua tema terinstall

### ⚙️ Konfigurasi GRUB

- ✅ Ubah resolusi GRUB (1920x1080, 1600x900, dll)
- ✅ Atur timeout menu boot
- ✅ Mode terminal (gfxterm/console)
- ✅ Edit parameter kernel (GRUB_CMDLINE_LINUX)
- ✅ Auto backup sebelum setiap perubahan

### 💾 Backup \& Restore

- ✅ Backup manual konfigurasi GRUB
- ✅ Restore dari backup sebelumnya
- ✅ Auto backup berkala (setiap 1 jam, opsional)
- ✅ Manajemen backup (hapus backup lama)
- ✅ Backup otomatis sebelum restore

### 🔧 Advanced Features

- ✅ Export/Import konfigurasi GRUB
- ✅ System information display
- ✅ Deteksi UEFI/BIOS otomatis
- ✅ Threading untuk update GRUB tanpa freeze UI
- ✅ Keyboard shortcuts
- ✅ Input validation
- ✅ Unsaved changes detection

### 🎮 Preview dengan Troubleshooting

- ✅ Dialog konfigurasi preview
- ✅ Opsi `--no-kvm` untuk kompatibilitas
- ✅ Custom resolution untuk preview
- ✅ Environment variables configuration
- ✅ Timeout configuration

## 📋 Persyaratan Sistem

### Sistem Operasi

- **Fedora 43** (direkomendasikan)
- Fedora 40-42 (kompatibel)
- Distro Linux lain dengan GRUB2 (mungkin perlu penyesuaian)

### Software Requirements

- **Python**: 3.6 atau lebih baru
- **PyQt5**: 5.x
- **GRUB2**: 2.x
- **polkit**: Untuk privilege escalation (pkexec)

### Optional (untuk fitur preview)

- **grub2-theme-preview**: Preview tema dengan QEMU
- **QEMU**: qemu-system-x86_64
- **OVMF**: UEFI firmware untuk QEMU
- **mtools \& xorriso**: Utilities untuk ISO creation

## 🚀 Instalasi

### 1. Install Dependencies

```bash
# Install PyQt5
sudo dnf install python3-pyqt5

# Install GRUB tools
sudo dnf install grub2-tools

# Install polkit (biasanya sudah ada)
sudo dnf install polkit
```

### 2. Install Optional Preview Tools

```bash
# Install grub2-theme-preview
pip3 install --user grub2-theme-preview

# Install QEMU dan dependencies
sudo dnf install qemu-system-x86 edk2-ovmf mtools xorriso
```

### 3. Download GRUB Theme Manager

```bash
# Clone repository (jika di GitHub)
git clone https://github.com/username/grub-theme-manager.git
cd grub-theme-manager

# Atau download langsung
wget https://path-to-file/grub-theme-manager-v05.py
chmod +x grub-theme-manager-v05.py
```

### 4. Jalankan Aplikasi

```bash
python3 grub-theme-manager-v05.py
```

## 📖 Cara Penggunaan

### Mengubah Bahasa Interface

1. Lihat dropdown **🌐 Bahasa** di kanan atas
2. Pilih bahasa yang diinginkan
3. Restart aplikasi untuk melihat perubahan

### Install Tema Baru

1. Download tema GRUB dari:
  - [GitHub - grub-themes](https://github.com/topics/grub-theme)
  - [Gnome-Look.org](https://www.gnome-look.org/browse/cat/109/)
  - [Grub2-Themes by vinceliuice](https://github.com/vinceliuice/grub2-themes)
2. Extract tema ke folder
3. Di aplikasi:
  - Buka tab **🎨 Tema**
  - Klik **📁 Browse**
  - Pilih folder tema
  - Klik **⬇ Install Tema**

### Menerapkan Tema

1. Pilih tema dari daftar
2. Klik **🔍 Validasi Tema** (opsional, untuk cek struktur)
3. Klik **👁 Preview** (opsional, jika grub2-theme-preview terinstall)
4. Klik **✓ Terapkan Tema**
5. Masukkan password sudo
6. Reboot untuk melihat perubahan

### Mengubah Resolusi GRUB

1. Buka tab **⚙️ Pengaturan**
2. Pilih resolusi dari dropdown **Resolusi GRUB**
3. Klik **💾 Simpan \& Terapkan Pengaturan**
4. Konfirmasi update GRUB
5. Reboot

### Backup \& Restore

**Membuat Backup:**

1. Buka tab **💾 Backup \& Restore**
2. Klik **💾 Buat Backup Sekarang** (atau Ctrl+B)
3. Backup tersimpan di `~/.grub-theme-manager/backups/`

**Restore Backup:**

1. Pilih backup dari daftar
2. Klik **↶ Restore Backup** atau double-click
3. Konfirmasi restore
4. Konfigurasi GRUB akan dikembalikan

### Auto Backup

1. Buka tab **🔧 Advanced**
2. Centang **Enable auto backup setiap jam**
3. Backup otomatis akan dibuat setiap 1 jam
4. Max 10 backup auto (yang lama dihapus otomatis)

### Export/Import Konfigurasi

**Export:**

1. Tab **🔧 Advanced** → **📤 Export Config**
2. Pilih lokasi penyimpanan
3. File `.conf` tersimpan

**Import:**

1. Tab **🔧 Advanced** → **📥 Import Config**
2. Pilih file `.conf`
3. Backup otomatis dibuat sebelum import

## ⌨️ Keyboard Shortcuts

| Shortcut | Fungsi |
| --- | --- |
| **F5** | Refresh semua data |
| **Ctrl+U** | Update GRUB Config |
| **Ctrl+B** | Buat Backup |
| **Ctrl+Q** | Keluar aplikasi |

## 🔧 Troubleshooting

### Preview Tidak Berfungsi

**Problem:** grub2-theme-preview tidak jalan atau error

**Solusi:**

1. Install grub2-theme-preview:

```bash
pip3 install --user grub2-theme-preview
```

2. Install dependencies:

```bash
sudo dnf install qemu-system-x86 edk2-ovmf mtools xorriso
```

3. Di aplikasi, klik **👁 Preview** → centang **Gunakan --no-kvm**
4. Set environment variables jika perlu:
  - `G2TP_GRUB_LIB`: `/usr/share/grub2` atau `/usr/lib/grub`
  - `G2TP_OVMF_IMAGE`: `/usr/share/edk2/ovmf/OVMF_CODE.fd`

### Update GRUB Gagal

**Problem:** Error saat update GRUB

**Solusi:**

1. Cek apakah `grub2-mkconfig` terinstall:

```bash
which grub2-mkconfig
```

2. Jalankan manual untuk lihat error:

```bash
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
```

3. Pastikan `pkexec` berfungsi:

```bash
pkexec echo "test"
```

### Tema Tidak Muncul di Boot

**Problem:** Tema sudah diterapkan tapi tidak muncul

**Solusi:**

1. Cek apakah GRUB_TERMINAL_OUTPUT di-comment:

```bash
grep GRUB_TERMINAL_OUTPUT /etc/default/grub
```

2. Pastikan tidak ada `GRUB_TERMINAL_OUTPUT="console"`
3. Harus `GRUB_TERMINAL_OUTPUT="gfxterm"`
4. Update GRUB lagi dengan Ctrl+U

### Permission Denied

**Problem:** Tidak bisa install/hapus tema

**Solusi:**

1. Pastikan polkit terinstall:

```bash
sudo dnf install polkit
```

2. User harus ada di grup wheel:

```bash
groups $USER
```

3. Jika belum, tambahkan:

```bash
sudo usermod -aG wheel $USER
```

## 📂 Struktur File

```
~/.grub-theme-manager/
└── backups/
    ├── grub_backup_20250117_120000.bak
    ├── grub_backup_20250117_130000.bak
    └── grub_auto_backup_20250117_140000.bak

/boot/grub2/
├── grub.cfg                    # Config yang di-generate
└── themes/                     # Folder tema
    ├── breeze/
    │   ├── theme.txt
    │   ├── background.png
    │   └── ...
    └── vimix/
        ├── theme.txt
        └── ...

/etc/default/grub              # Config GRUB utama
```

## 🌟 Contoh Tema GRUB

### Rekomendasi Tema Populer

1. **Vimix GRUB Theme**
  - GitHub: https://github.com/vinceliuice/grub2-themes
  - Modern, flat design
  - Multiple variants
2. **Cyberpunk GRUB Theme**
  - Futuristic cyberpunk style
  - Animated backgrounds
3. **Fallout GRUB Theme**
  - Pip-Boy inspired
  - Vintage terminal look
4. **Sekiro GRUB Theme**
  - Japanese aesthetic
  - Minimalist design

## 🤝 Contributing

Kontribusi sangat diterima! Silakan:

1. Fork repository
2. Buat branch fitur (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📝 TODO / Roadmap

- [ ] Tambahkan lebih banyak bahasa (Jepang, Korea, Jerman, dll)
- [ ] Built-in theme gallery dengan preview
- [ ] Theme creator/editor visual
- [ ] Export tema custom
- [ ] Auto-detect OS lain dan customize menu entries
- [ ] Dark/Light mode untuk aplikasi
- [ ] Plugins system
- [ ] Command-line interface (CLI) mode

## ⚠️ Disclaimer

- **Backup penting!** Selalu buat backup sebelum mengubah konfigurasi GRUB
- Aplikasi ini memodifikasi file sistem yang sensitif (`/etc/default/grub`)
- Kesalahan konfigurasi dapat membuat sistem tidak bisa boot
- Gunakan dengan hati-hati dan tanggung jawab sendiri
- Tested pada Fedora 43 UEFI/BIOS
- Distro lain mungkin memerlukan penyesuaian path

## 📄 License

MIT License - Lihat [LICENSE](LICENSE) untuk detail lengkap

## 👨‍💻 Author

**Ferdian Nasrudin**

- Email: ferdian.nasrudin@gmail.com

## 🙏 Acknowledgments

- PyQt5 team untuk GUI framework
- GRUB developers
- grub2-theme-preview contributors
- Semua pembuat tema GRUB yang luar biasa
- Komunitas Fedora

## 📞 Support

Jika ada masalah atau pertanyaan:

1. **GitHub Issues**: [Create an issue](https://github.com/username/grub-theme-manager/issues)
2. **Email**: ferdian.nasrudin@gmail.com
3. **Dokumentasi**: Lihat [Wiki](https://github.com/username/grub-theme-manager/wiki)

## 🔗 Links

- **GRUB Manual**: https://www.gnu.org/software/grub/manual/
- **Fedora GRUB Docs**: https://docs.fedoraproject.org/en-US/fedora/latest/system-administrators-guide/kernel-module-driver-configuration/Working_with_the_GRUB_2_Boot_Loader/
- **Theme Resources**:
  - https://github.com/topics/grub-theme
  - https://www.gnome-look.org/browse/cat/109/
  - https://www.pling.com/browse/cat/109/

---

**⭐ Jika aplikasi ini membantu, berikan star di GitHub!**
