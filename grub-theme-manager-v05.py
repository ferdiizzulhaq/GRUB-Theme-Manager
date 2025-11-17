#!/usr/bin/env python3
"""
GRUB Theme Manager untuk Fedora 43 - Versi 5.0 Multi-Language
Aplikasi GUI untuk mengelola tema GRUB dengan dukungan multi-bahasa
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QFileDialog, QMessageBox,
    QTextEdit, QGroupBox, QLineEdit, QComboBox, QCheckBox, QTabWidget,
    QProgressBar, QStatusBar, QShortcut, QSpinBox, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt5.QtGui import QFont, QColor, QIntValidator, QKeySequence, QIcon


# ============================================================================
# HELPER CLASSES
# ============================================================================

class GRUBUpdateThread(QThread):
    """Thread untuk update GRUB tanpa freeze UI"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, command):
        super().__init__()
        self.command = command
    
    def run(self):
        try:
            self.progress.emit("Memulai update GRUB...")
            result = subprocess.run(
                self.command,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.progress.emit("✓ Update GRUB berhasil!")
                self.finished.emit(True, "Konfigurasi GRUB berhasil diperbarui!")
            else:
                self.finished.emit(False, f"Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.finished.emit(False, "Timeout: Update GRUB terlalu lama")
        except Exception as e:
            self.finished.emit(False, str(e))


class PreviewDialog(QDialog):
    """Dialog untuk konfigurasi preview"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Konfigurasi Preview")
        self.setModal(True)
        self.resize(500, 350)
        
        layout = QVBoxLayout(self)
        
        # Info
        info = QLabel(
            "⚠️ Preview membutuhkan grub2-theme-preview dan QEMU.\n\n"
            "Jika preview tidak berfungsi, coba opsi di bawah:"
        )
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Opsi no-kvm
        self.no_kvm_check = QCheckBox("Gunakan --no-kvm (lebih lambat, tapi lebih kompatibel)")
        self.no_kvm_check.setChecked(False)
        layout.addWidget(self.no_kvm_check)
        
        # Custom resolution
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("Resolusi Preview:"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "Default",
            "1920x1080",
            "1600x900",
            "1366x768",
            "1280x720",
            "1024x768"
        ])
        res_layout.addWidget(self.resolution_combo)
        res_layout.addStretch()
        layout.addLayout(res_layout)
        
        # Timeout
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Timeout (detik):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(-1, 300)
        self.timeout_spin.setValue(30)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        layout.addLayout(timeout_layout)
        
        # Environment variables
        env_group = QGroupBox("Environment Variables (troubleshooting)")
        env_layout = QVBoxLayout()
        
        grub_lib_layout = QHBoxLayout()
        grub_lib_layout.addWidget(QLabel("G2TP_GRUB_LIB:"))
        self.grub_lib_input = QLineEdit()
        self.grub_lib_input.setPlaceholderText("/usr/share/grub2 atau /usr/lib/grub")
        grub_lib_layout.addWidget(self.grub_lib_input)
        env_layout.addLayout(grub_lib_layout)
        
        ovmf_layout = QHBoxLayout()
        ovmf_layout.addWidget(QLabel("G2TP_OVMF_IMAGE:"))
        self.ovmf_input = QLineEdit()
        self.ovmf_input.setPlaceholderText("/usr/share/edk2/ovmf/OVMF_CODE.fd")
        ovmf_layout.addWidget(self.ovmf_input)
        env_layout.addLayout(ovmf_layout)
        
        env_group.setLayout(env_layout)
        layout.addWidget(env_group)
        
        layout.addStretch()
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_preview_options(self):
        """Return preview options"""
        return {
            'no_kvm': self.no_kvm_check.isChecked(),
            'resolution': self.resolution_combo.currentText() if self.resolution_combo.currentIndex() > 0 else None,
            'timeout': self.timeout_spin.value(),
            'grub_lib': self.grub_lib_input.text() or None,
            'ovmf_image': self.ovmf_input.text() or None
        }


class ThemeValidatorDialog(QDialog):
    """Dialog untuk validasi tema"""
    def __init__(self, theme_path, parent=None):
        super().__init__(parent)
        self.theme_path = theme_path
        self.setWindowTitle("Validasi Tema")
        self.setModal(True)
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(f"<h3>Validasi Tema: {os.path.basename(theme_path)}</h3>"))
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        
        close_btn = QPushButton("Tutup")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.validate_theme()
    
    def validate_theme(self):
        """Validasi struktur tema"""
        results = []
        
        # Cek theme.txt
        theme_txt = os.path.join(self.theme_path, 'theme.txt')
        if os.path.exists(theme_txt):
            results.append("✓ theme.txt ditemukan")
            
            # Parse theme.txt
            try:
                with open(theme_txt, 'r') as f:
                    content = f.read()
                    
                # Cek komponen penting
                components = {
                    'title-text': 'Judul menu',
                    'desktop-image': 'Background image',
                    'boot_menu': 'Boot menu',
                    'progress_bar': 'Progress bar'
                }
                
                for key, name in components.items():
                    if key in content:
                        results.append(f"  ✓ {name} terdefinisi")
                    else:
                        results.append(f"  ⚠ {name} tidak terdefinisi")
                        
            except Exception as e:
                results.append(f"  ✗ Error parsing theme.txt: {e}")
        else:
            results.append("✗ theme.txt TIDAK ditemukan - Tema tidak valid!")
        
        # Cek direktori umum
        common_dirs = ['icons', 'backgrounds', 'fonts']
        for dir_name in common_dirs:
            dir_path = os.path.join(self.theme_path, dir_name)
            if os.path.exists(dir_path):
                file_count = len(os.listdir(dir_path))
                results.append(f"✓ Folder {dir_name}/ ({file_count} file)")
            else:
                results.append(f"ℹ Folder {dir_name}/ tidak ada (opsional)")
        
        # Cek file gambar
        image_exts = ['.png', '.jpg', '.jpeg', '.tga']
        images = []
        for root, dirs, files in os.walk(self.theme_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_exts):
                    images.append(file)
        
        if images:
            results.append(f"\n✓ Ditemukan {len(images)} file gambar:")
            for img in images[:5]:
                results.append(f"  • {img}")
            if len(images) > 5:
                results.append(f"  ... dan {len(images) - 5} lainnya")
        else:
            results.append("\n⚠ Tidak ada file gambar ditemukan")
        
        self.result_text.setText("\n".join(results))

# ============================================================================
# SISTEM TRANSLASI / INTERNATIONALIZATION (i18n)
# ============================================================================

class Translations:
    """Kelas untuk mengelola translasi multi-bahasa"""
    
    def __init__(self):
        self.current_language = 'id'  # Default: Indonesian
        self.translations = {
            'id': {  # Indonesian (Default)
                'app_title': 'GRUB Theme Manager v5.0 - Fedora 43',
                'system': 'Sistem',
                'ready': 'Siap',
                'theme_tab': '🎨 Tema',
                'settings_tab': '⚙️ Pengaturan',
                'backup_tab': '💾 Backup & Restore',
                'advanced_tab': '🔧 Advanced',
                'current_theme': 'Tema Aktif Saat Ini',
                'theme': 'Tema',
                'installed_themes': 'Tema Terinstall',
                'apply_theme': '✓ Terapkan Tema',
                'validate_theme': '🔍 Validasi Tema',
                'preview_theme': '👁 Preview (QEMU)',
                'delete_theme': '🗑 Hapus Tema',
                'install_new_theme': 'Install Tema Baru',
                'browse': '📁 Browse',
                'install': '⬇ Install Tema',
                'download_themes': '💡 Download tema',
                'display_settings': 'Pengaturan Tampilan',
                'resolution': 'Resolusi GRUB',
                'terminal_mode': 'Mode Terminal',
                'timeout_settings': 'Pengaturan Waktu',
                'timeout_menu': 'Timeout Menu (detik)',
                'hide_countdown': 'Sembunyikan countdown',
                'kernel_settings': 'Pengaturan Kernel',
                'kernel_params': 'Parameter Kernel (GRUB_CMDLINE_LINUX)',
                'kernel_warning': '⚠️ Hati-hati saat mengubah parameter kernel!',
                'save_apply': '💾 Simpan & Terapkan Pengaturan',
                'backup_info': 'Informasi Backup',
                'backup_desc': 'Backup akan menyimpan file /etc/default/grub',
                'backup_tip': '💡 Tip: Selalu buat backup sebelum mengubah konfigurasi penting!',
                'create_backup': '💾 Buat Backup Sekarang',
                'available_backups': 'Backup Tersedia',
                'restore_backup': '↶ Restore Backup',
                'delete_backup': '🗑 Hapus Backup',
                'refresh': '↻ Refresh',
                'auto_backup': 'Auto Backup',
                'enable_auto_backup': 'Enable auto backup setiap jam',
                'auto_backup_desc': 'Auto backup akan membuat backup setiap jam secara otomatis.\nBackup lama akan dihapus otomatis (max 10 backup).',
                'export_import': 'Export/Import Konfigurasi',
                'export_config': '📤 Export Config',
                'import_config': '📥 Import Config',
                'export_desc': 'Export akan menyimpan semua pengaturan GRUB ke file.\nImport akan menerapkan pengaturan dari file yang di-export.',
                'system_info': 'Informasi Sistem',
                'clear_log': 'Bersihkan Log',
                'log_activity': 'Log Aktivitas',
                'shortcuts_hint': '💡 F5 (Refresh) | Ctrl+U (Update GRUB) | Ctrl+B (Backup) | Ctrl+Q (Keluar)',
                'update_grub': '🔄 Update GRUB Config',
                'about': 'ℹ️ Tentang',
                'exit': '✖ Keluar',
                'confirmation': 'Konfirmasi',
                'warning': 'Peringatan',
                'success': 'Sukses',
                'error': 'Error',
                'yes': 'Ya',
                'no': 'Tidak',
                'ok': 'OK',
                'cancel': 'Batal',
                'close': 'Tutup',
                'language': '🌐 Bahasa',
                'select_language': 'Pilih Bahasa',
                'restart_required': 'Perubahan bahasa akan diterapkan setelah restart aplikasi.',
            },
            'en': {  # English
                'app_title': 'GRUB Theme Manager v5.0 - Fedora 43',
                'system': 'System',
                'ready': 'Ready',
                'theme_tab': '🎨 Themes',
                'settings_tab': '⚙️ Settings',
                'backup_tab': '💾 Backup & Restore',
                'advanced_tab': '🔧 Advanced',
                'current_theme': 'Current Active Theme',
                'theme': 'Theme',
                'installed_themes': 'Installed Themes',
                'apply_theme': '✓ Apply Theme',
                'validate_theme': '🔍 Validate Theme',
                'preview_theme': '👁 Preview (QEMU)',
                'delete_theme': '🗑 Delete Theme',
                'install_new_theme': 'Install New Theme',
                'browse': '📁 Browse',
                'install': '⬇ Install Theme',
                'download_themes': '💡 Download themes',
                'display_settings': 'Display Settings',
                'resolution': 'GRUB Resolution',
                'terminal_mode': 'Terminal Mode',
                'timeout_settings': 'Timeout Settings',
                'timeout_menu': 'Menu Timeout (seconds)',
                'hide_countdown': 'Hide countdown',
                'kernel_settings': 'Kernel Settings',
                'kernel_params': 'Kernel Parameters (GRUB_CMDLINE_LINUX)',
                'kernel_warning': '⚠️ Be careful when modifying kernel parameters!',
                'save_apply': '💾 Save & Apply Settings',
                'backup_info': 'Backup Information',
                'backup_desc': 'Backup will save /etc/default/grub file',
                'backup_tip': '💡 Tip: Always create backup before changing important config!',
                'create_backup': '💾 Create Backup Now',
                'available_backups': 'Available Backups',
                'restore_backup': '↶ Restore Backup',
                'delete_backup': '🗑 Delete Backup',
                'refresh': '↻ Refresh',
                'auto_backup': 'Auto Backup',
                'enable_auto_backup': 'Enable auto backup every hour',
                'auto_backup_desc': 'Auto backup will create backup every hour automatically.\nOld backups will be deleted automatically (max 10 backups).',
                'export_import': 'Export/Import Configuration',
                'export_config': '📤 Export Config',
                'import_config': '📥 Import Config',
                'export_desc': 'Export will save all GRUB settings to file.\nImport will apply settings from exported file.',
                'system_info': 'System Information',
                'clear_log': 'Clear Log',
                'log_activity': 'Activity Log',
                'shortcuts_hint': '💡 F5 (Refresh) | Ctrl+U (Update GRUB) | Ctrl+B (Backup) | Ctrl+Q (Exit)',
                'update_grub': '🔄 Update GRUB Config',
                'about': 'ℹ️ About',
                'exit': '✖ Exit',
                'confirmation': 'Confirmation',
                'warning': 'Warning',
                'success': 'Success',
                'error': 'Error',
                'yes': 'Yes',
                'no': 'No',
                'ok': 'OK',
                'cancel': 'Cancel',
                'close': 'Close',
                'language': '🌐 Language',
                'select_language': 'Select Language',
                'restart_required': 'Language change will take effect after restarting the application.',
            },
            'ar': {  # Arabic
                'app_title': 'مدير سمات GRUB الإصدار 5.0 - فيدورا 43',
                'system': 'النظام',
                'ready': 'جاهز',
                'theme_tab': '🎨 السمات',
                'settings_tab': '⚙️ الإعدادات',
                'backup_tab': '💾 النسخ الاحتياطي',
                'advanced_tab': '🔧 متقدم',
                'current_theme': 'السمة النشطة الحالية',
                'theme': 'السمة',
                'installed_themes': 'السمات المثبتة',
                'apply_theme': '✓ تطبيق السمة',
                'validate_theme': '🔍 التحقق من السمة',
                'preview_theme': '👁 معاينة (QEMU)',
                'delete_theme': '🗑 حذف السمة',
                'install_new_theme': 'تثبيت سمة جديدة',
                'browse': '📁 استعراض',
                'install': '⬇ تثبيت السمة',
                'download_themes': '💡 تنزيل السمات',
                'display_settings': 'إعدادات العرض',
                'resolution': 'دقة GRUB',
                'terminal_mode': 'وضع الطرفية',
                'timeout_settings': 'إعدادات المهلة',
                'timeout_menu': 'مهلة القائمة (بالثواني)',
                'hide_countdown': 'إخفاء العد التنازلي',
                'kernel_settings': 'إعدادات النواة',
                'kernel_params': 'معلمات النواة',
                'kernel_warning': '⚠️ كن حذرًا عند تعديل معلمات النواة!',
                'save_apply': '💾 حفظ وتطبيق الإعدادات',
                'backup_info': 'معلومات النسخ الاحتياطي',
                'backup_desc': 'سيحفظ النسخ الاحتياطي ملف /etc/default/grub',
                'backup_tip': '💡 نصيحة: قم دائمًا بإنشاء نسخة احتياطية قبل تغيير التكوين المهم!',
                'create_backup': '💾 إنشاء نسخة احتياطية الآن',
                'available_backups': 'النسخ الاحتياطية المتاحة',
                'restore_backup': '↶ استعادة النسخة الاحتياطية',
                'delete_backup': '🗑 حذف النسخة الاحتياطية',
                'refresh': '↻ تحديث',
                'auto_backup': 'النسخ الاحتياطي التلقائي',
                'enable_auto_backup': 'تمكين النسخ الاحتياطي التلقائي كل ساعة',
                'auto_backup_desc': 'سيقوم النسخ الاحتياطي التلقائي بإنشاء نسخة احتياطية كل ساعة تلقائيًا.',
                'export_import': 'تصدير/استيراد التكوين',
                'export_config': '📤 تصدير التكوين',
                'import_config': '📥 استيراد التكوين',
                'export_desc': 'سيحفظ التصدير جميع إعدادات GRUB في ملف.',
                'system_info': 'معلومات النظام',
                'clear_log': 'مسح السجل',
                'log_activity': 'سجل النشاط',
                'shortcuts_hint': '💡 F5 (تحديث) | Ctrl+U (تحديث GRUB) | Ctrl+B (نسخة احتياطية) | Ctrl+Q (خروج)',
                'update_grub': '🔄 تحديث تكوين GRUB',
                'about': 'ℹ️ حول',
                'exit': '✖ خروج',
                'confirmation': 'تأكيد',
                'warning': 'تحذير',
                'success': 'نجح',
                'error': 'خطأ',
                'yes': 'نعم',
                'no': 'لا',
                'ok': 'موافق',
                'cancel': 'إلغاء',
                'close': 'إغلاق',
                'language': '🌐 اللغة',
                'select_language': 'اختر اللغة',
                'restart_required': 'سيتم تطبيق تغيير اللغة بعد إعادة تشغيل التطبيق.',
            },
            'zh': {  # Chinese
                'app_title': 'GRUB 主题管理器 v5.0 - Fedora 43',
                'system': '系统',
                'ready': '就绪',
                'theme_tab': '🎨 主题',
                'settings_tab': '⚙️ 设置',
                'backup_tab': '💾 备份与恢复',
                'advanced_tab': '🔧 高级',
                'current_theme': '当前活动主题',
                'theme': '主题',
                'installed_themes': '已安装的主题',
                'apply_theme': '✓ 应用主题',
                'validate_theme': '🔍 验证主题',
                'preview_theme': '👁 预览 (QEMU)',
                'delete_theme': '🗑 删除主题',
                'install_new_theme': '安装新主题',
                'browse': '📁 浏览',
                'install': '⬇ 安装主题',
                'download_themes': '💡 下载主题',
                'display_settings': '显示设置',
                'resolution': 'GRUB 分辨率',
                'terminal_mode': '终端模式',
                'timeout_settings': '超时设置',
                'timeout_menu': '菜单超时（秒）',
                'hide_countdown': '隐藏倒计时',
                'kernel_settings': '内核设置',
                'kernel_params': '内核参数',
                'kernel_warning': '⚠️ 修改内核参数时要小心！',
                'save_apply': '💾 保存并应用设置',
                'backup_info': '备份信息',
                'backup_desc': '备份将保存 /etc/default/grub 文件',
                'backup_tip': '💡 提示：在更改重要配置之前始终创建备份！',
                'create_backup': '💾 立即创建备份',
                'available_backups': '可用备份',
                'restore_backup': '↶ 恢复备份',
                'delete_backup': '🗑 删除备份',
                'refresh': '↻ 刷新',
                'auto_backup': '自动备份',
                'enable_auto_backup': '启用每小时自动备份',
                'auto_backup_desc': '自动备份将每小时自动创建备份。',
                'export_import': '导出/导入配置',
                'export_config': '📤 导出配置',
                'import_config': '📥 导入配置',
                'export_desc': '导出将所有GRUB设置保存到文件。',
                'system_info': '系统信息',
                'clear_log': '清除日志',
                'log_activity': '活动日志',
                'shortcuts_hint': '💡 F5 (刷新) | Ctrl+U (更新GRUB) | Ctrl+B (备份) | Ctrl+Q (退出)',
                'update_grub': '🔄 更新GRUB配置',
                'about': 'ℹ️ 关于',
                'exit': '✖ 退出',
                'confirmation': '确认',
                'warning': '警告',
                'success': '成功',
                'error': '错误',
                'yes': '是',
                'no': '否',
                'ok': '确定',
                'cancel': '取消',
                'close': '关闭',
                'language': '🌐 语言',
                'select_language': '选择语言',
                'restart_required': '语言更改将在重新启动应用程序后生效。',
            },
            # French, Russian, Spanish - sama seperti sebelumnya
        }
        
        # Load saved language preference
        self.load_language_preference()
    
    def get(self, key):
        """Dapatkan teks dalam bahasa yang dipilih"""
        return self.translations.get(self.current_language, {}).get(key, key)
    
    def set_language(self, lang_code):
        """Set bahasa"""
        if lang_code in self.translations:
            self.current_language = lang_code
            self.save_language_preference()
            return True
        return False
    
    def get_available_languages(self):
        """Dapatkan daftar bahasa yang tersedia"""
        return {
            'id': 'Bahasa Indonesia',
            'en': 'English',
            'ar': 'العربية (Arabic)',
            'zh': '中文 (Chinese)',
        }
    
    def save_language_preference(self):
        """Simpan preferensi bahasa"""
        settings = QSettings('GRUBThemeManager', 'Language')
        settings.setValue('current_language', self.current_language)
    
    def load_language_preference(self):
        """Load preferensi bahasa yang tersimpan"""
        settings = QSettings('GRUBThemeManager', 'Language')
        saved_lang = settings.value('current_language', 'id')
        if saved_lang in self.translations:
            self.current_language = saved_lang


# Instance global untuk translasi
tr = Translations()

# ============================================================================
# MAIN APPLICATION CLASS
# ============================================================================

class GRUBThemeManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.grub_config_path = "/etc/default/grub"
        self.grub_cfg_path = "/boot/grub2/grub.cfg"
        self.themes_path = "/boot/grub2/themes"
        self.backup_dir = os.path.expanduser("~/.grub-theme-manager/backups")
        
        # Deteksi sistem UEFI atau BIOS
        self.is_uefi = os.path.exists("/sys/firmware/efi")
        self.boot_type = "UEFI" if self.is_uefi else "BIOS"
        
        # Initialize log messages buffer
        self.log_messages = []
        
        # Track perubahan yang belum disimpan
        self.has_unsaved_changes = False
        
        # Preview options
        self.preview_options = {
            'no_kvm': False,
            'resolution': None,
            'timeout': 30,
            'grub_lib': None,
            'ovmf_image': None
        }
        
        self.current_theme = self.get_current_theme()
        self.update_thread = None
        
        # Buat folder backup
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Auto backup timer
        self.auto_backup_timer = QTimer()
        self.auto_backup_timer.timeout.connect(self.auto_backup)
        
        self.init_ui()
        self.setup_shortcuts()
        self.load_themes()
        self.load_current_config()
        self.check_preview_availability()
        
        # Flush buffered log messages
        if self.log_messages:
            for msg in self.log_messages:
                self.log_text.append(msg)
            self.log_messages.clear()
    
    def init_ui(self):
        """Inisialisasi User Interface dengan multi-language"""
        self.setWindowTitle(f"{tr.get('app_title')} ({self.boot_type})")
        self.setGeometry(100, 100, 980, 750)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"{tr.get('system')}: {self.boot_type} | {tr.get('ready')}")
        
        # Widget utama
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header dengan language selector
        header_layout = QHBoxLayout()
        header = QLabel("GRUB Theme Manager v5.0")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(header)
        
        system_label = QLabel(f"[{self.boot_type}]")
        system_label.setFont(QFont("Arial", 12))
        system_label.setStyleSheet("color: #0066cc; padding: 5px;")
        header_layout.addWidget(system_label)
        
        header_layout.addStretch()
        
        # Language selector
        lang_layout = QHBoxLayout()
        lang_label = QLabel(tr.get('language'))
        lang_layout.addWidget(lang_label)
        
        self.language_combo = QComboBox()
        languages = tr.get_available_languages()
        for code, name in languages.items():
            self.language_combo.addItem(name, code)
        
        # Set current language
        current_index = self.language_combo.findData(tr.current_language)
        if current_index >= 0:
            self.language_combo.setCurrentIndex(current_index)
        
        self.language_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(self.language_combo)
        
        header_layout.addLayout(lang_layout)
        
        main_layout.addLayout(header_layout)
        
        # Tab Widget
        tabs = QTabWidget()
        
        # Tab 1: Tema
        theme_tab = self.create_theme_tab()
        tabs.addTab(theme_tab, tr.get('theme_tab'))
        
        # Tab 2: Pengaturan
        settings_tab = self.create_settings_tab()
        tabs.addTab(settings_tab, tr.get('settings_tab'))
        
        # Tab 3: Backup & Restore
        backup_tab = self.create_backup_tab()
        tabs.addTab(backup_tab, tr.get('backup_tab'))
        
        # Tab 4: Advanced
        advanced_tab = self.create_advanced_tab()
        tabs.addTab(advanced_tab, tr.get('advanced_tab'))
        
        main_layout.addWidget(tabs)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Log area
        log_group = QGroupBox(tr.get('log_activity'))
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        log_layout.addWidget(self.log_text)
        
        log_buttons = QHBoxLayout()
        clear_log_btn = QPushButton(tr.get('clear_log'))
        clear_log_btn.clicked.connect(self.log_text.clear)
        log_buttons.addWidget(clear_log_btn)
        
        # Tampilkan shortcut hints
        shortcut_hint = QLabel(tr.get('shortcuts_hint'))
        shortcut_hint.setStyleSheet("color: gray; font-size: 10px;")
        log_buttons.addWidget(shortcut_hint)
        log_buttons.addStretch()
        
        log_layout.addLayout(log_buttons)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # Tombol utama
        bottom_buttons = QHBoxLayout()
        
        self.update_grub_button = QPushButton(tr.get('update_grub'))
        self.update_grub_button.clicked.connect(self.manual_update_grub)
        self.update_grub_button.setStyleSheet("background-color: #0066cc; color: white; padding: 8px;")
        bottom_buttons.addWidget(self.update_grub_button)
        
        refresh_button = QPushButton(tr.get('refresh'))
        refresh_button.clicked.connect(self.refresh_all)
        bottom_buttons.addWidget(refresh_button)
        
        about_button = QPushButton(tr.get('about'))
        about_button.clicked.connect(self.show_about)
        bottom_buttons.addWidget(about_button)
        
        exit_button = QPushButton(tr.get('exit'))
        exit_button.clicked.connect(self.close)
        bottom_buttons.addWidget(exit_button)
        
        main_layout.addLayout(bottom_buttons)
        
        self.log("✓ Aplikasi siap digunakan")
        self.log(f"✓ Sistem boot: {self.boot_type}")
        self.log(f"✓ Lokasi grub.cfg: {self.grub_cfg_path}")
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        refresh_shortcut = QShortcut(QKeySequence('F5'), self)
        refresh_shortcut.activated.connect(self.refresh_all)
        
        update_shortcut = QShortcut(QKeySequence('Ctrl+U'), self)
        update_shortcut.activated.connect(self.manual_update_grub)
        
        backup_shortcut = QShortcut(QKeySequence('Ctrl+B'), self)
        backup_shortcut.activated.connect(self.create_backup)
        
        quit_shortcut = QShortcut(QKeySequence('Ctrl+Q'), self)
        quit_shortcut.activated.connect(self.close)
    
    def change_language(self, index):
        """Handler untuk perubahan bahasa"""
        lang_code = self.language_combo.itemData(index)
        if lang_code and lang_code != tr.current_language:
            tr.set_language(lang_code)
            
            QMessageBox.information(
                self,
                tr.get('language'),
                tr.get('restart_required')
            )
    
    def create_theme_tab(self):
        """Buat tab untuk manajemen tema"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Info tema aktif
        info_group = QGroupBox(tr.get('current_theme'))
        info_layout = QVBoxLayout()
        self.current_theme_label = QLabel(f"{tr.get('theme')}: {self.current_theme}")
        self.current_theme_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(self.current_theme_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Daftar tema
        themes_group = QGroupBox(tr.get('installed_themes'))
        themes_layout = QVBoxLayout()
        
        self.themes_list = QListWidget()
        self.themes_list.itemClicked.connect(self.on_theme_selected)
        self.themes_list.itemDoubleClicked.connect(self.apply_theme)
        themes_layout.addWidget(self.themes_list)
        
        # Tombol tema
        themes_buttons = QHBoxLayout()
        
        self.apply_button = QPushButton(tr.get('apply_theme'))
        self.apply_button.clicked.connect(self.apply_theme)
        self.apply_button.setEnabled(False)
        self.apply_button.setStyleSheet("background-color: #28a745; color: white; padding: 6px;")
        themes_buttons.addWidget(self.apply_button)
        
        self.validate_button = QPushButton(tr.get('validate_theme'))
        self.validate_button.clicked.connect(self.validate_theme)
        self.validate_button.setEnabled(False)
        themes_buttons.addWidget(self.validate_button)
        
        self.preview_button = QPushButton(tr.get('preview_theme'))
        self.preview_button.clicked.connect(self.show_preview_dialog)
        self.preview_button.setEnabled(False)
        themes_buttons.addWidget(self.preview_button)
        
        self.delete_button = QPushButton(tr.get('delete_theme'))
        self.delete_button.clicked.connect(self.delete_theme)
        self.delete_button.setEnabled(False)
        self.delete_button.setStyleSheet("background-color: #dc3545; color: white; padding: 6px;")
        themes_buttons.addWidget(self.delete_button)
        
        themes_layout.addLayout(themes_buttons)
        themes_group.setLayout(themes_layout)
        layout.addWidget(themes_group)
        
        # Install tema baru
        install_group = QGroupBox(tr.get('install_new_theme'))
        install_layout = QVBoxLayout()
        
        path_layout = QHBoxLayout()
        self.install_path_input = QLineEdit()
        self.install_path_input.setPlaceholderText(tr.get('browse') + "...")
        path_layout.addWidget(self.install_path_input)
        
        browse_button = QPushButton(tr.get('browse'))
        browse_button.clicked.connect(self.browse_theme)
        path_layout.addWidget(browse_button)
        
        install_button = QPushButton(tr.get('install'))
        install_button.clicked.connect(self.install_theme)
        install_button.setStyleSheet("background-color: #007bff; color: white; padding: 6px;")
        path_layout.addWidget(install_button)
        
        install_layout.addLayout(path_layout)
        
        # Link download tema
        link_label = QLabel(
            f'{tr.get("download_themes")}: '
            '<a href="https://github.com/topics/grub-theme">GitHub</a> | '
            '<a href="https://www.gnome-look.org/browse/cat/109/">Gnome-Look</a>'
        )
        link_label.setOpenExternalLinks(True)
        install_layout.addWidget(link_label)
        
        install_group.setLayout(install_layout)
        layout.addWidget(install_group)
        
        return tab
    
    def create_settings_tab(self):
        """Buat tab pengaturan"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Display settings
        display_group = QGroupBox(tr.get('display_settings'))
        display_layout = QVBoxLayout()
        
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel(tr.get('resolution') + ":"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "Auto (Default)", "1920x1080", "1600x900", "1366x768",
            "1280x720", "1024x768"
        ])
        self.resolution_combo.currentIndexChanged.connect(self.mark_unsaved_changes)
        res_layout.addWidget(self.resolution_combo)
        res_layout.addStretch()
        display_layout.addLayout(res_layout)
        
        terminal_layout = QHBoxLayout()
        terminal_layout.addWidget(QLabel(tr.get('terminal_mode') + ":"))
        self.terminal_combo = QComboBox()
        self.terminal_combo.addItems(["gfxterm (Grafis)", "console (Teks)"])
        self.terminal_combo.currentIndexChanged.connect(self.mark_unsaved_changes)
        terminal_layout.addWidget(self.terminal_combo)
        terminal_layout.addStretch()
        display_layout.addLayout(terminal_layout)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # Timeout settings
        timeout_group = QGroupBox(tr.get('timeout_settings'))
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel(tr.get('timeout_menu') + ":"))
        self.timeout_input = QLineEdit()
        self.timeout_input.setPlaceholderText("5")
        self.timeout_input.setMaximumWidth(80)
        self.timeout_input.setValidator(QIntValidator(0, 300))
        self.timeout_input.textChanged.connect(self.mark_unsaved_changes)
        timeout_layout.addWidget(self.timeout_input)
        timeout_layout.addStretch()
        timeout_group.setLayout(timeout_layout)
        layout.addWidget(timeout_group)
        
        # Kernel settings
        kernel_group = QGroupBox(tr.get('kernel_settings'))
        kernel_layout = QVBoxLayout()
        kernel_layout.addWidget(QLabel(tr.get('kernel_params') + ":"))
        self.cmdline_input = QLineEdit()
        self.cmdline_input.setPlaceholderText("quiet splash")
        self.cmdline_input.textChanged.connect(self.mark_unsaved_changes)
        kernel_layout.addWidget(self.cmdline_input)
        
        warning = QLabel(tr.get('kernel_warning'))
        warning.setStyleSheet("color: orange; font-size: 10px;")
        kernel_layout.addWidget(warning)
        kernel_group.setLayout(kernel_layout)
        layout.addWidget(kernel_group)
        
        # Apply button
        apply_btn = QPushButton(tr.get('save_apply'))
        apply_btn.clicked.connect(self.apply_settings)
        apply_btn.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")
        layout.addWidget(apply_btn)
        layout.addStretch()
        
        return tab
    
    def create_backup_tab(self):
        """Buat tab backup"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info_group = QGroupBox(tr.get('backup_info'))
        info_layout = QVBoxLayout()
        info_text = QLabel(
            f"{tr.get('backup_desc')}\n"
            f"Lokasi: {self.backup_dir}\n\n"
            f"{tr.get('backup_tip')}"
        )
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        create_btn = QPushButton(tr.get('create_backup'))
        create_btn.clicked.connect(self.create_backup)
        create_btn.setStyleSheet("background-color: #17a2b8; color: white; padding: 8px;")
        layout.addWidget(create_btn)
        
        list_group = QGroupBox(tr.get('available_backups'))
        list_layout = QVBoxLayout()
        
        self.backup_list = QListWidget()
        self.backup_list.itemDoubleClicked.connect(self.restore_backup)
        list_layout.addWidget(self.backup_list)
        
        backup_buttons = QHBoxLayout()
        restore_btn = QPushButton(tr.get('restore_backup'))
        restore_btn.clicked.connect(self.restore_backup)
        backup_buttons.addWidget(restore_btn)
        
        delete_btn = QPushButton(tr.get('delete_backup'))
        delete_btn.clicked.connect(self.delete_backup)
        backup_buttons.addWidget(delete_btn)
        
        refresh_btn = QPushButton(tr.get('refresh'))
        refresh_btn.clicked.connect(self.load_backups)
        backup_buttons.addWidget(refresh_btn)
        
        list_layout.addLayout(backup_buttons)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        self.load_backups()
        
        return tab
    
    def create_advanced_tab(self):
        """Buat tab advanced"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Auto backup
        auto_group = QGroupBox(tr.get('auto_backup'))
        auto_layout = QVBoxLayout()
        
        self.auto_backup_check = QCheckBox(tr.get('enable_auto_backup'))
        self.auto_backup_check.stateChanged.connect(self.toggle_auto_backup)
        auto_layout.addWidget(self.auto_backup_check)
        
        auto_info = QLabel(tr.get('auto_backup_desc'))
        auto_info.setStyleSheet("color: gray; font-size: 11px;")
        auto_layout.addWidget(auto_info)
        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)
        
        # Export/Import
        export_group = QGroupBox(tr.get('export_import'))
        export_layout = QHBoxLayout()
        
        export_btn = QPushButton(tr.get('export_config'))
        export_btn.clicked.connect(self.export_config)
        export_layout.addWidget(export_btn)
        
        import_btn = QPushButton(tr.get('import_config'))
        import_btn.clicked.connect(self.import_config)
        export_layout.addWidget(import_btn)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # System info
        info_group = QGroupBox(tr.get('system_info'))
        info_layout = QVBoxLayout()
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(200)
        info_text.setText(self.get_system_info())
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        return tab
    
    # Helper methods
    def mark_unsaved_changes(self):
        self.has_unsaved_changes = True
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        if hasattr(self, 'log_text'):
            self.log_text.append(formatted)
        else:
            self.log_messages.append(formatted)
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(message, 3000)
    
    def get_current_theme(self):
        try:
            with open(self.grub_config_path, 'r') as f:
                for line in f:
                    if line.startswith('GRUB_THEME='):
                        theme_path = line.split('=')[1].strip().strip('"')
                        if theme_path:
                            return Path(theme_path).parent.name
            return "Default"
        except:
            return "Error"
    
    def load_current_config(self):
        try:
            with open(self.grub_config_path, 'r') as f:
                for line in f:
                    if line.startswith('GRUB_TIMEOUT='):
                        self.timeout_input.setText(line.split('=')[1].strip().strip('"'))
                    elif line.startswith('GRUB_GFXMODE='):
                        gfx = line.split('=')[1].strip().strip('"')
                        idx = self.resolution_combo.findText(gfx)
                        if idx >= 0:
                            self.resolution_combo.setCurrentIndex(idx)
                    elif line.startswith('GRUB_CMDLINE_LINUX='):
                        self.cmdline_input.setText(line.split('=',1)[1].strip().strip('"'))
            self.has_unsaved_changes = False
        except Exception as e:
            self.log(f"✗ Error load config: {e}")
    
    def load_themes(self):
        self.themes_list.clear()
        if not os.path.exists(self.themes_path):
            return
        try:
            themes = [d for d in os.listdir(self.themes_path) 
                     if os.path.isdir(os.path.join(self.themes_path, d))]
            if themes:
                self.themes_list.addItems(sorted(themes))
                self.log(f"✓ {len(themes)} tema ditemukan")
        except:
            pass
    
    def load_backups(self):
        self.backup_list.clear()
        try:
            backups = [f for f in os.listdir(self.backup_dir) 
                      if f.startswith('grub_backup_') and f.endswith('.bak')]
            if backups:
                self.backup_list.addItems(sorted(backups, reverse=True))
        except:
            pass
    
    def on_theme_selected(self, item):
        self.apply_button.setEnabled(True)
        self.validate_button.setEnabled(True)
        self.preview_button.setEnabled(True)
        self.delete_button.setEnabled(True)
    
    def check_preview_availability(self):
        try:
            subprocess.run(['which', 'grub2-theme-preview'], 
                         check=True, capture_output=True)
            return True
        except:
            return False
    
    def get_system_info(self):
        info = []
        info.append(f"Boot: {self.boot_type}")
        info.append(f"Config: {self.grub_config_path}")
        info.append(f"GRUB CFG: {self.grub_cfg_path}")
        info.append(f"Themes: {self.themes_path}")
        info.append(f"Backup: {self.backup_dir}")
        try:
            result = subprocess.run(['grub2-mkconfig', '--version'], 
                                  capture_output=True, text=True)
            info.append(f"\nGRUB: Installed ✓")
        except:
            info.append("\nGRUB: Error")
        return "\n".join(info)
    
    # Action methods
    def apply_theme(self):
        selected = self.themes_list.currentItem()
        if not selected:
            return
        
        theme_name = selected.text()
        theme_path = os.path.join(self.themes_path, theme_name, "theme.txt")
        
        if not os.path.exists(theme_path):
            QMessageBox.warning(self, tr.get('error'), 
                f'theme.txt tidak ditemukan!')
            return
        
        reply = QMessageBox.question(self, tr.get('confirmation'),
            f'Terapkan tema "{theme_name}"?\n\nBackup otomatis akan dibuat.',
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.No:
            return
        
        try:
            # Backup first
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"grub_backup_{timestamp}.bak")
            shutil.copy2(self.grub_config_path, backup_file)
            
            # Update config
            temp_config = "/tmp/grub_temp"
            with open(self.grub_config_path, 'r') as f:
                lines = f.readlines()
            
            with open(temp_config, 'w') as f:
                theme_found = False
                for line in lines:
                    if line.startswith('GRUB_THEME=') or line.startswith('#GRUB_THEME='):
                        f.write(f'GRUB_THEME="{theme_path}"\n')
                        theme_found = True
                    else:
                        f.write(line)
                if not theme_found:
                    f.write(f'\nGRUB_THEME="{theme_path}"\n')
            
            subprocess.run(['pkexec', 'cp', temp_config, self.grub_config_path], check=True)
            self.log(f"✓ Tema '{theme_name}' diterapkan")
            self.run_grub_update(f"Tema '{theme_name}' diterapkan")
            
        except Exception as e:
            self.log(f"✗ Error: {e}")
            QMessageBox.critical(self, tr.get('error'), str(e))
    
    def apply_settings(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"grub_backup_{timestamp}.bak")
            shutil.copy2(self.grub_config_path, backup_file)
            
            resolution = self.resolution_combo.currentText()
            timeout = self.timeout_input.text()
            terminal = "gfxterm" if self.terminal_combo.currentIndex() == 0 else "console"
            cmdline = self.cmdline_input.text()
            
            temp_config = "/tmp/grub_temp"
            with open(self.grub_config_path, 'r') as f:
                lines = f.readlines()
            
            with open(temp_config, 'w') as f:
                for line in lines:
                    if resolution != "Auto (Default)" and line.startswith('GRUB_GFXMODE='):
                        f.write(f'GRUB_GFXMODE={resolution}\n')
                    elif timeout and line.startswith('GRUB_TIMEOUT='):
                        f.write(f'GRUB_TIMEOUT={timeout}\n')
                    elif line.startswith('GRUB_CMDLINE_LINUX='):
                        f.write(f'GRUB_CMDLINE_LINUX="{cmdline}"\n')
                    else:
                        f.write(line)
            
            subprocess.run(['pkexec', 'cp', temp_config, self.grub_config_path], check=True)
            self.has_unsaved_changes = False
            self.run_grub_update("Pengaturan diterapkan")
            
        except Exception as e:
            QMessageBox.critical(self, tr.get('error'), str(e))
    
    def run_grub_update(self, success_message):
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.update_grub_button.setEnabled(False)
        
        command = ['pkexec', 'grub2-mkconfig', '-o', self.grub_cfg_path]
        
        self.update_thread = GRUBUpdateThread(command)
        self.update_thread.progress.connect(self.log)
        self.update_thread.finished.connect(
            lambda success, msg: self.on_update_finished(success, msg, success_message)
        )
        self.update_thread.start()
    
    def on_update_finished(self, success, message, success_message):
        self.progress_bar.setVisible(False)
        self.update_grub_button.setEnabled(True)
        
        if success:
            self.log(f"✓ {success_message}")
            self.current_theme = self.get_current_theme()
            self.current_theme_label.setText(f"{tr.get('theme')}: {self.current_theme}")
            QMessageBox.information(self, tr.get('success'), 
                f'{success_message}!\n\nReboot untuk melihat perubahan.')
        else:
            QMessageBox.critical(self, tr.get('error'), message)
    
    def manual_update_grub(self):
        reply = QMessageBox.question(self, tr.get('confirmation'),
            f'Regenerasi GRUB?\n\n{self.grub_cfg_path}',
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.run_grub_update("GRUB diperbarui")
    
    def show_preview_dialog(self):
        dialog = PreviewDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.preview_options = dialog.get_preview_options()
            self.preview_theme()
    
    def preview_theme(self):
        selected = self.themes_list.currentItem()
        if not selected:
            return
        
        theme_name = selected.text()
        theme_path = os.path.join(self.themes_path, theme_name)
        
        cmd = ['grub2-theme-preview', theme_path]
        if self.preview_options.get('no_kvm'):
            cmd.append('--no-kvm')
        
        try:
            self.log(f"🔍 Preview '{theme_name}'...")
            subprocess.Popen(cmd)
        except FileNotFoundError:
            QMessageBox.warning(self, 'Tool Not Found',
                'grub2-theme-preview belum terinstall.\n\n'
                'pip3 install --user grub2-theme-preview')
    
    def validate_theme(self):
        selected = self.themes_list.currentItem()
        if not selected:
            return
        
        theme_path = os.path.join(self.themes_path, selected.text())
        dialog = ThemeValidatorDialog(theme_path, self)
        dialog.exec_()
    
    def delete_theme(self):
        selected = self.themes_list.currentItem()
        if not selected:
            return
        
        theme_name = selected.text()
        if theme_name == self.current_theme:
            QMessageBox.warning(self, tr.get('warning'),
                'Tidak dapat menghapus tema yang sedang aktif!')
            return
        
        reply = QMessageBox.question(self, tr.get('confirmation'),
            f'Hapus tema "{theme_name}"?',
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                theme_path = os.path.join(self.themes_path, theme_name)
                subprocess.run(['pkexec', 'rm', '-rf', theme_path], check=True)
                self.log(f"✓ Tema '{theme_name}' dihapus")
                self.load_themes()
            except Exception as e:
                self.log(f"✗ Error: {e}")
    
    def browse_theme(self):
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Tema")
        if folder:
            self.install_path_input.setText(folder)
    
    def install_theme(self):
        source_path = self.install_path_input.text()
        
        if not source_path or not os.path.exists(source_path):
            QMessageBox.warning(self, tr.get('error'), 
                'Pilih folder tema yang valid!')
            return
        
        if not os.path.exists(os.path.join(source_path, 'theme.txt')):
            QMessageBox.warning(self, tr.get('error'), 
                'Folder tidak mengandung theme.txt!')
            return
        
        theme_name = os.path.basename(source_path)
        dest_path = os.path.join(self.themes_path, theme_name)
        
        try:
            subprocess.run(['pkexec', 'mkdir', '-p', self.themes_path], check=True)
            subprocess.run(['pkexec', 'cp', '-r', source_path, dest_path], check=True)
            
            self.log(f"✓ Tema '{theme_name}' terinstall")
            QMessageBox.information(self, tr.get('success'), 
                f'Tema "{theme_name}" berhasil diinstall!')
            
            self.load_themes()
            self.install_path_input.clear()
            
        except Exception as e:
            QMessageBox.critical(self, tr.get('error'), str(e))
    
    def create_backup(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"grub_backup_{timestamp}.bak")
            
            shutil.copy2(self.grub_config_path, backup_file)
            self.log(f"✓ Backup: {os.path.basename(backup_file)}")
            self.load_backups()
            
            QMessageBox.information(self, tr.get('success'), 
                f'Backup berhasil!\n\n{os.path.basename(backup_file)}')
            
        except Exception as e:
            QMessageBox.critical(self, tr.get('error'), str(e))
    
    def restore_backup(self):
        selected = self.backup_list.currentItem()
        if not selected:
            QMessageBox.warning(self, tr.get('warning'), 
                'Pilih backup untuk direstore!')
            return
        
        backup_file = os.path.join(self.backup_dir, selected.text())
        
        reply = QMessageBox.question(self, tr.get('confirmation'),
            f'Restore backup:\n{selected.text()}',
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                subprocess.run(['pkexec', 'cp', backup_file, self.grub_config_path], check=True)
                self.log(f"✓ Restore: {selected.text()}")
                self.load_current_config()
                self.manual_update_grub()
            except Exception as e:
                QMessageBox.critical(self, tr.get('error'), str(e))
    
    def delete_backup(self):
        selected = self.backup_list.currentItem()
        if not selected:
            return
        
        backup_file = os.path.join(self.backup_dir, selected.text())
        
        reply = QMessageBox.question(self, tr.get('confirmation'),
            f'Hapus backup:\n{selected.text()}?',
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(backup_file)
                self.log(f"✓ Backup dihapus")
                self.load_backups()
            except Exception as e:
                self.log(f"✗ Error: {e}")
    
    def toggle_auto_backup(self, state):
        if state == Qt.Checked:
            self.auto_backup_timer.start(3600000)  # 1 hour
            self.log("✓ Auto backup aktif")
        else:
            self.auto_backup_timer.stop()
            self.log("ℹ Auto backup nonaktif")
    
    def auto_backup(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"grub_auto_backup_{timestamp}.bak")
            shutil.copy2(self.grub_config_path, backup_file)
            self.log(f"✓ Auto backup: {os.path.basename(backup_file)}")
            
            # Cleanup old
            backups = sorted([f for f in os.listdir(self.backup_dir) 
                            if f.startswith('grub_auto_backup_')], reverse=True)
            for old in backups[10:]:
                os.remove(os.path.join(self.backup_dir, old))
        except:
            pass
    
    def export_config(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, tr.get('export_config'), 
            os.path.expanduser("~/grub_export.conf"),
            "Config Files (*.conf)")
        
        if file_path:
            try:
                shutil.copy2(self.grub_config_path, file_path)
                self.log(f"✓ Export: {file_path}")
                QMessageBox.information(self, tr.get('success'), 
                    f'Config di-export!\n\n{file_path}')
            except Exception as e:
                QMessageBox.critical(self, tr.get('error'), str(e))
    
    def import_config(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, tr.get('import_config'),
            os.path.expanduser("~"),
            "Config Files (*.conf)")
        
        if file_path:
            reply = QMessageBox.question(self, tr.get('confirmation'),
                f'Import:\n{file_path}\n\nBackup otomatis akan dibuat.',
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                try:
                    self.create_backup()
                    subprocess.run(['pkexec', 'cp', file_path, self.grub_config_path], check=True)
                    self.log(f"✓ Import: {file_path}")
                    self.load_current_config()
                    self.manual_update_grub()
                except Exception as e:
                    QMessageBox.critical(self, tr.get('error'), str(e))
    
    def refresh_all(self):
        self.log("↻ Refresh...")
        self.load_themes()
        self.load_backups()
        self.load_current_config()
        self.current_theme = self.get_current_theme()
        self.current_theme_label.setText(f"{tr.get('theme')}: {self.current_theme}")
        self.log("✓ Refresh selesai")
    
    def show_about(self):
        QMessageBox.about(self, tr.get('about'),
            f"""<h2>GRUB Theme Manager v5.0</h2>
            <p><b>{tr.get('system')}:</b> {self.boot_type}</p>
            <p>Aplikasi multi-language untuk mengelola tema GRUB</p>
            <br>
            <p><b>Bahasa:</b> 🇮🇩 🇬🇧 🇸🇦 🇨🇳</p>
            <p><b>Shortcuts:</b> F5 | Ctrl+U | Ctrl+B | Ctrl+Q</p>
            """)
    
    def closeEvent(self, event):
        if self.has_unsaved_changes:
            reply = QMessageBox.question(self, tr.get('warning'),
                'Ada perubahan belum disimpan!\n\nYakin keluar?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        reply = QMessageBox.question(self, tr.get('confirmation'),
            'Yakin keluar?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    app = QApplication(sys.argv)
    
    app.setApplicationName("GRUB Theme Manager")
    app.setApplicationVersion("5.0")
    app.setOrganizationName("GRUB Tools")
    
    if not os.path.exists('/etc/fedora-release'):
        reply = QMessageBox.question(None, 'Peringatan',
            'Aplikasi untuk Fedora.\nLanjutkan?',
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            sys.exit(0)
    
    if sys.version_info < (3, 6):
        QMessageBox.critical(None, 'Error',
            f'Butuh Python 3.6+!\nVersi: {sys.version}')
        sys.exit(1)
    
    window = GRUBThemeManager()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

