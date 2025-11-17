# Contributing to GRUB Theme Manager

Terima kasih sudah tertarik berkontribusi! 🎉

## Cara Berkontribusi

1. Fork repository ini
2. Buat branch baru (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## Coding Standards

- Ikuti PEP 8 untuk Python code
- Gunakan meaningful variable names
- Tambahkan docstring untuk functions
- Test sebelum submit PR

## Menambahkan Bahasa Baru

Untuk menambahkan bahasa baru:
1. Edit class `Translations` di file utama
2. Tambahkan kode bahasa (e.g., 'fr', 'de', 'ja')
3. Translate semua keys
4. Update `get_available_languages()`
5. Test dengan memilih bahasa tersebut

## Melaporkan Bug

Gunakan GitHub Issues dengan template:
- **Deskripsi bug**
- **Cara reproduce**
- **Expected behavior**
- **Screenshots** (jika ada)
- **Environment** (OS, Python version, dll)

## Feature Requests

Silakan buat GitHub Issue dengan label `enhancement`
