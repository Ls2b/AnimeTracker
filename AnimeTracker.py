import sys
import os
import json
import webbrowser
import requests
import urllib3
import hashlib
import shutil
from urllib.parse import quote

# Отключаем предупреждения об SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from PyQt6 import sip
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QScrollArea, QGridLayout,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QDialog, QFileDialog, QFormLayout, QSpinBox, QTabWidget, QMessageBox, 
    QMenu, QCheckBox, QComboBox, QSlider
)
from PyQt6.QtGui import QPixmap, QIcon, QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QTimer, QEvent

# ИМПОРТИРУЕМ НАШ СКОМПИЛИРОВАННЫЙ ФАЙЛ РЕСУРСОВ
try:
    import sprites_rc
except ImportError:
    print("Предупреждение: файл ресурсов sprites_rc.py не найден. Скомпилируйте его через pyrcc6.")

try:
    import ctypes
    myappid = 'mycompany.animeapp.v1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

DATA_FILE = "anime_data.json"
CONFIG_FILE = "config.json"
COVERS_DIR = "anime_covers"
CACHE_DIR = "anime_covers_cache"
WALLPAPERS_DIR = "app_wallpapers"

for folder in [COVERS_DIR, CACHE_DIR, WALLPAPERS_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- СТИЛИ ОФОРМЛЕНИЯ (QSS) ---
# --- СТИЛИ ОФОРМЛЕНИЯ (QSS) ---
DARK_STYLE = """
    QMainWindow {{ background-color: #121214; }}
    QTabWidget::pane {{ border: 1px solid #27272a; background-color: {pane_rgba}; border-radius: 8px; top: -1px; }}
    QTabBar::tab {{ background-color: #1e1e24; color: #a1a1aa; padding: 10px 20px; font-weight: bold; font-size: 13px; border: 1px solid #27272a; border-bottom-color: transparent; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 4px; }}
    QTabBar::tab:selected {{ background-color: #18181b; color: #3b82f6; border-bottom-color: #18181b; }}
    QTabBar::tab:hover {{ background-color: #27272a; color: #f4f4f5; }}
    QLineEdit {{ background-color: #27272a; color: #f4f4f5; border: 1px solid #3f3f46; border-radius: 6px; padding: 6px 10px; font-size: 13px; }}
    QLineEdit:focus {{ border: 1px solid #3b82f6; }}
    QSpinBox {{ background-color: #27272a; color: #f4f4f5; border: 1px solid #3f3f46; border-radius: 6px; padding: 4px; min-height: 25px; }}
    QSpinBox:focus {{ border: 1px solid #3f3f46; outline: none; }}
    QScrollArea {{ border: none; background-color: transparent; }}
    QWidget#scroll_content {{ background-color: {content_rgba}; }}
    QScrollBar:vertical {{ border: none; background: transparent; width: 12px; margin: 4px 2px 4px 2px; border-radius: 4px; }}
    QScrollBar::handle:vertical {{ background: #3f3f46; border-radius: 4px; min-height: 30px; }}
    QScrollBar::handle:vertical:hover {{ background: #3b82f6; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ background: none; border: none; }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
    QDialog {{ background-color: #18181b; }}
    QDialog QLabel {{ color: #e4e4e7; }}
    QMessageBox {{ background-color: #18181b; }}
    QMessageBox QLabel {{ color: #e4e4e7; }}
    QMessageBox QPushButton {{ background-color: #27272a; color: #f4f4f5; border: 1px solid #3f3f46; padding: 5px 15px; border-radius: 4px; }}
    QMenu {{ background-color: #1e1e24; color: #f4f4f5; border: 1px solid #27272a; border-radius: 6px; }}
    QMenu::item:selected {{ background-color: #3b82f6; }}
    QCheckBox {{ color: #e4e4e7; }}
    QComboBox {{ background-color: #27272a; color: #f4f4f5; border: 1px solid #3f3f46; border-radius: 6px; padding: 4px; }}

    /* СТИЛИ КНОПОК КАРТОЧКИ ДЛЯ ТЕМНОЙ ТЕМЫ */
    QPushButton#card_fav_btn, QPushButton#card_arch_btn, QPushButton#card_edit_btn {{ 
        background-color: #3f3f46; border: 1px solid #52525b; border-radius: 6px; 
    }}
    QPushButton#card_fav_btn:hover {{ background-color: #52525b; border: 1px solid #3b82f6; }}
    QPushButton#card_arch_btn:hover {{ background-color: #52525b; border: 1px solid #16a34a; }}
    QPushButton#card_edit_btn:hover {{ background-color: #52525b; border: 1px solid #2563eb; }}
    
    QPushButton#card_rate_btn {{ 
        background-color: #27272a; border: 1px solid #3f3f46; border-radius: 6px; font-size: 11px; font-weight: bold; color: #fbbf24; 
    }}
    QPushButton#card_rate_btn:hover {{ background-color: #3f3f46; border: 1px solid #fbbf24; }}
    
    QPushButton#card_del_btn {{ 
        background-color: #451a1a; border: 1px solid #991b1b; border-radius: 6px; 
    }}
    QPushButton#card_del_btn:hover {{ background-color: #7f1d1d; border: 1px solid #ef4444; }}
"""

LIGHT_STYLE = """
    QMainWindow {{ background-color: #f4f4f5; }}
    QTabWidget::pane {{ border: 1px solid #e4e4e7; background-color: {pane_rgba}; border-radius: 8px; top: -1px; }}
    QTabBar::tab {{ background-color: #e4e4e7; color: #71717a; padding: 10px 20px; font-weight: bold; font-size: 13px; border: 1px solid #d4d4d8; border-bottom-color: transparent; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 4px; }}
    QTabBar::tab:selected {{ background-color: #ffffff; color: #2563eb; border-bottom-color: #ffffff; border-top: 2px solid #2563eb; }}
    QTabBar::tab:hover {{ background-color: #f4f4f5; color: #18181b; }}
    QLineEdit {{ background-color: #ffffff; color: #18181b; border: 1px solid #d4d4d8; border-radius: 6px; padding: 6px 10px; font-size: 13px; }}
    QLineEdit:focus {{ border: 1px solid #2563eb; }}
    QSpinBox {{ background-color: #ffffff; color: #18181b; border: 1px solid #d4d4d8; border-radius: 6px; padding: 4px; min-height: 25px; }}
    QSpinBox:focus {{ border: 1px solid #2563eb; outline: none; }}
    QScrollArea {{ border: none; background-color: transparent; }}
    QWidget#scroll_content {{ background-color: {content_rgba}; }}
    QScrollBar:vertical {{ border: none; background: transparent; width: 12px; margin: 4px 2px 4px 2px; border-radius: 4px; }}
    QScrollBar::handle:vertical {{ background: #d4d4d8; border-radius: 4px; min-height: 30px; }}
    QScrollBar::handle:vertical:hover {{ background: #2563eb; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ background: none; border: none; }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
    QDialog {{ background-color: #ffffff; }}
    QDialog QLabel {{ color: #18181b; }}
    QMessageBox {{ background-color: #ffffff; }}
    QMessageBox QLabel {{ color: #18181b; }}
    QMessageBox QPushButton {{ background-color: #e4e4e7; color: #18181b; border: 1px solid #d4d4d8; padding: 5px 15px; border-radius: 4px; }}
    QMenu {{ background-color: #ffffff; color: #18181b; border: 1px solid #e4e4e7; border-radius: 6px; }}
    QMenu::item:selected {{ background-color: #2563eb; color: white; }}
    QCheckBox {{ color: #18181b; }}
    QComboBox {{ background-color: #ffffff; color: #18181b; border: 1px solid #d4d4d8; border-radius: 6px; padding: 4px; }}

    /* СТИЛИ КНОПОК КАРТОЧКИ ДЛЯ СВЕТЛОЙ ТЕМЫ */
    QPushButton#card_fav_btn, QPushButton#card_arch_btn, QPushButton#card_edit_btn {{ 
        background-color: #e4e4e7; border: 1px solid #d4d4d8; border-radius: 6px; 
    }}
    QPushButton#card_fav_btn:hover {{ background-color: #d4d4d8; border: 1px solid #2563eb; }}
    QPushButton#card_arch_btn:hover {{ background-color: #d4d4d8; border: 1px solid #16a34a; }}
    QPushButton#card_edit_btn:hover {{ background-color: #d4d4d8; border: 1px solid #2563eb; }}
    
    QPushButton#card_rate_btn {{ 
        background-color: #f4f4f5; border: 1px solid #d4d4d8; border-radius: 6px; font-size: 11px; font-weight: bold; color: #d97706; 
    }}
    QPushButton#card_rate_btn:hover {{ background-color: #e4e4e7; border: 1px solid #d97706; }}
    
    QPushButton#card_del_btn {{ 
        background-color: #fee2e2; border: 1px solid #fca5a5; border-radius: 6px; 
    }}
    QPushButton#card_del_btn:hover {{ background-color: #fca5a5; border: 1px solid #dc2626; }}
"""

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEnginePage
except ImportError:
    pass

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_config():
    default_config = {"theme": "dark", "use_wallpaper": False, "wallpaper_path": "", "opacity": 85}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return {**default_config, **json.load(f)}
        except:
            return default_config
    return default_config

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


class ImageLoaderThread(QThread):
    loaded = pyqtSignal(str, QPixmap)

    def __init__(self, uid, url):
        super().__init__()
        self.uid = uid
        self.url = url
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        self.cache_filepath = os.path.join(CACHE_DIR, f"{url_hash}.png")

    def run(self):
        if self.isInterruptionRequested():
            return

        if os.path.exists(self.cache_filepath):
            pixmap = QPixmap()
            if pixmap.load(self.cache_filepath):
                if not self.isInterruptionRequested():
                    self.loaded.emit(self.uid, pixmap)
                return

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            res = requests.get(self.url, headers=headers, timeout=5, verify=False)
            
            if self.isInterruptionRequested():
                return

            if res.status_code == 200:
                pixmap = QPixmap()
                if pixmap.loadFromData(res.content):
                    if pixmap.width() > 300 or pixmap.height() > 300:
                        pixmap = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    
                    pixmap.save(self.cache_filepath, "PNG")
                    
                    if not self.isInterruptionRequested():
                        self.loaded.emit(self.uid, pixmap)
                    return
        except:
            pass
        
        if not self.isInterruptionRequested():
            self.loaded.emit(self.uid, QPixmap())


class CustomWebPage(QWebEnginePage):
    def __init__(self, alert_callback, parent=None):
        super().__init__(parent)
        self.alert_callback = alert_callback

    def javaScriptAlert(self, securityOrigin, message):
        self.alert_callback(message)


class MiniBrowserDialog(QDialog):
    image_selected = pyqtSignal(str)

    def __init__(self, search_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Google Картинки")
        self.resize(1100, 750)
        layout = QVBoxLayout(self)
        self.browser = QWebEngineView(self)
        self.custom_page = CustomWebPage(self.handle_js_alert, self.browser)
        self.browser.setPage(self.custom_page)
        layout.addWidget(self.browser)
        query = quote(f"{search_text} anime poster")
        url = f"https://www.google.com/search?q={query}&tbm=isch"
        self.browser.setUrl(QUrl(url))
        self.browser.loadFinished.connect(self.inject_click_tracker)

    def inject_click_tracker(self):
        js_code = """
        document.addEventListener('click', function(e) {
            let element = e.target;
            let container = element.closest('div[data-ril]') || element.closest('a');
            if (element.tagName === 'IMG' || container) {
                let imgElement = container ? container.querySelector('img') : element;
                if (imgElement && imgElement.src) {
                    let src = imgElement.src;
                    if (src.startsWith('data:') && container) {
                        let href = container.getAttribute('href');
                        if (href) {
                            let urlParams = new URLSearchParams(href.substr(href.indexOf('?')));
                            let imgUrl = urlParams.get('imgurl');
                            if (imgUrl) { e.preventDefault(); alert("FOUND:" + imgUrl); return; }
                        }
                    }
                    if (src && !src.startsWith('data:')) { e.preventDefault(); alert("FOUND:" + src); }
                }
            }
        }, true);
        """
        self.browser.page().runJavaScript(js_code)

    def handle_js_alert(self, message):
        if message.startswith("FOUND:"):
            image_url = message.replace("FOUND:", "")
            QTimer.singleShot(100, lambda: self.finish_selection(image_url))

    def finish_selection(self, url):
        self.image_selected.emit(url)
        self.accept()


class EditAnimeDialog(QDialog):
    def __init__(self, parent=None, edit_data=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать аниме" if edit_data else "Добавить аниме")
        self.setFixedWidth(460)
        layout = QFormLayout(self)
        layout.setSpacing(10)
        
        self.title_input = QLineEdit(self)
        self.link_input = QLineEdit(self)
        self.voice_input = QLineEdit(self)
        self.cover_input = QLineEdit(self)
        
        if edit_data:
            self.title_input.setText(edit_data.get("title", ""))
            self.link_input.setText(edit_data.get("link", ""))
            self.voice_input.setText(edit_data.get("voice", ""))
            self.cover_input.setText(edit_data.get("cover", ""))
            
        self.file_btn = QPushButton("📁 Выбрать файл на ПК", self)
        self.file_btn.setStyleSheet("background-color: #27272a; color: #f4f4f5; border: 1px solid #3f3f46; padding: 6px; border-radius: 6px;")
        self.file_btn.clicked.connect(self.choose_local_file)
        
        self.web_btn = QPushButton("✨ Умный выбор в Google", self)
        self.web_btn.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; padding: 6px; border-radius: 6px;")
        self.web_btn.clicked.connect(self.open_embedded_browser)

        layout.addRow("Название аниме:", self.title_input)
        layout.addRow("Ссылка на плеер:", self.link_input)
        layout.addRow("Озвучка / Перевод:", self.voice_input)
        layout.addRow("Ссылка/Путь обложки:", self.cover_input)
        layout.addRow("Локальный выбор:", self.file_btn)
        layout.addRow("Авто-поиск:", self.web_btn)
        
        self.save_btn = QPushButton("Сохранить", self)
        self.save_btn.setStyleSheet("background-color: #16a34a; color: white; font-weight: bold; padding: 8px; border-radius: 6px; margin-top: 10px;")
        self.save_btn.clicked.connect(self.accept)
        layout.addRow(self.save_btn)

    def choose_local_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите обложку", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if file_path:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(COVERS_DIR, filename)
            try:
                shutil.copy2(file_path, dest_path)
                self.cover_input.setText(dest_path)
            except:
                self.cover_input.setText(os.path.abspath(file_path))

    def open_embedded_browser(self):
        title = self.title_input.text().strip()
        if title:
            browser_dialog = MiniBrowserDialog(title, self)
            browser_dialog.image_selected.connect(self.cover_input.setText)
            browser_dialog.exec()

    def get_data(self):
        return {
            "title": self.title_input.text().strip(),
            "link": self.link_input.text().strip(),
            "voice": self.voice_input.text().strip(),
            "cover": self.cover_input.text().strip()
        }


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки приложения")
        self.setFixedWidth(440)
        self.config = load_config()
        
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        self.theme_combo = QComboBox(self)
        self.theme_combo.addItems(["Темная", "Светлая"])
        self.theme_combo.setCurrentIndex(0 if self.config.get("theme", "dark") == "dark" else 1)
        layout.addRow("Тема интерфейса:", self.theme_combo)
        
        # --- БЛОК НАСТРОЙКИ ПРОЗРАЧНОСТИ ---
        self.opacity_label = QLabel(f"Прозрачность вкладок: {self.config.get('opacity', 85)}%", self)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.opacity_slider.setMinimum(10) # Минимально 10%, чтобы вкладки полностью не исчезали
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(self.config.get("opacity", 85))
        self.opacity_slider.valueChanged.connect(self.update_opacity_label)
        layout.addRow(self.opacity_label, self.opacity_slider)
        
        # --- БЛОК ОБОЕВ ---
        self.wallpaper_checkbox = QCheckBox("Включить обои приложения", self)
        self.wallpaper_checkbox.setChecked(self.config.get("use_wallpaper", False))
        self.wallpaper_checkbox.stateChanged.connect(self.toggle_wallpaper_widgets)
        layout.addRow(self.wallpaper_checkbox)
        
        self.wp_input = QLineEdit(self)
        self.wp_input.setText(self.config.get("wallpaper_path", ""))
        self.wp_input.setReadOnly(True)
        self.wp_input.setPlaceholderText("Обои не выбраны")
        
        self.choose_wp_btn = QPushButton("📁 Выбрать картинку обоев", self)
        self.choose_wp_btn.setStyleSheet("background-color: #27272a; color: #f4f4f5; border: 1px solid #3f3f46; padding: 6px; border-radius: 6px;")
        self.choose_wp_btn.clicked.connect(self.choose_wallpaper)
        
        layout.addRow("Файл обоев:", self.wp_input)
        layout.addRow(self.choose_wp_btn)
        
        self.toggle_wallpaper_widgets()
        
        self.save_btn = QPushButton("Сохранить настройки", self)
        self.save_btn.setStyleSheet("background-color: #16a34a; color: white; font-weight: bold; padding: 8px; border-radius: 6px; margin-top: 10px;")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addRow(self.save_btn)
        
    def update_opacity_label(self, value):
        self.opacity_label.setText(f"Прозрачность вкладок: {value}%")
        
    def toggle_wallpaper_widgets(self):
        enabled = self.wallpaper_checkbox.isChecked()
        self.wp_input.setEnabled(enabled)
        self.choose_wp_btn.setEnabled(enabled)
        
    def choose_wallpaper(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите обои приложения", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if file_path:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(WALLPAPERS_DIR, filename)
            try:
                shutil.copy2(file_path, dest_path)
                self.wp_input.setText(dest_path)
            except:
                self.wp_input.setText(os.path.abspath(file_path))
            
    def save_settings(self):
        self.config["theme"] = "dark" if self.theme_combo.currentIndex() == 0 else "light"
        self.config["use_wallpaper"] = self.wallpaper_checkbox.isChecked()
        self.config["wallpaper_path"] = self.wp_input.text().strip()
        self.config["opacity"] = self.opacity_slider.value() # Сохраняем прозрачность
        save_config(self.config)
        self.accept()


class AnimeCard(QWidget):
    def __init__(self, anime_id, data, on_update, on_edit, on_toggle_archive, on_toggle_favorite, on_delete, app_instance):
        super().__init__()
        self.anime_id = anime_id
        self.data = data
        self.on_update = on_update
        self.on_edit = on_edit
        self.on_toggle_archive = on_toggle_archive
        self.on_toggle_favorite = on_toggle_favorite
        self.on_delete = on_delete
        self.app_instance = app_instance
        self.setFixedWidth(196)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        
        top_bar = QHBoxLayout()
        
        self.fav_btn = QPushButton(self)
        self.fav_btn.setObjectName("card_fav_btn") # Привязываем к QSS
        is_favorite = self.data.get("favorite", False)
        icon_path = ":/icons/sprites/star_full.png" if is_favorite else ":/icons/sprites/star_empty.png"
        self.fav_btn.setIcon(QIcon(icon_path))
        self.fav_btn.setFixedSize(28, 28)
        self.fav_btn.setToolTip("Добавить / Удалить из Избранного")
        self.fav_btn.clicked.connect(lambda: self.on_toggle_favorite(self.data))
        top_bar.addWidget(self.fav_btn)
        
        self.archive_btn = QPushButton(self)
        self.archive_btn.setObjectName("card_arch_btn") # Привязываем к QSS
        is_archived = self.data.get("archived", False)
        check_icon = ":/icons/sprites/check.png" if is_archived else ":/icons/sprites/uncheck.png"
        self.archive_btn.setIcon(QIcon(check_icon))
        self.archive_btn.setFixedSize(28, 28)
        self.archive_btn.setToolTip("Переместить в Архив (Просмотрено) или обратно в Список ожидания")
        self.archive_btn.clicked.connect(lambda: self.on_toggle_archive(self.data))
        top_bar.addWidget(self.archive_btn)
        
        self.rate_btn = QPushButton(self)
        self.rate_btn.setObjectName("card_rate_btn") # Привязываем к QSS
        rating = self.data.get("rating", None)
        self.rate_btn.setText(f"⭐ {rating}" if rating else "⭐ —")
        self.rate_btn.setFixedSize(42, 28)
        self.rate_btn.setToolTip("Поставить свою оценку релизу")
        self.rate_btn.clicked.connect(self.show_rating_menu)
        top_bar.addWidget(self.rate_btn)
        
        top_bar.addStretch()
        
        self.delete_btn = QPushButton(self)
        self.delete_btn.setObjectName("card_del_btn") # Привязываем к QSS
        self.delete_btn.setIcon(QIcon(":/icons/sprites/trash.png"))
        self.delete_btn.setFixedSize(28, 28)
        self.delete_btn.setToolTip("Полностью удалить релиз из базы данных")
        self.delete_btn.clicked.connect(self.confirm_and_delete)
        top_bar.addWidget(self.delete_btn)
        
        layout.addLayout(top_bar)
        
        self.img_label = QLabel(self)
        self.img_label.setFixedSize(176, 176)
        self.img_label.setStyleSheet("border: 1px solid #3f3f46; background-color: #121214; border-radius: 6px; color: #71717a;")
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_cover()
        layout.addWidget(self.img_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(self.data.get("title", "Без названия"), self)
        title_label.setWordWrap(True)
        title_label.setFixedWidth(176)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        theme = load_config().get("theme", "dark")
        title_color = "#f4f4f5" if theme == "dark" else "#18181b"
        title_label.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {title_color}; min-height: 32px;")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        voice_text = self.data.get("voice", "").strip()
        self.voice_label = QLabel(f"🎙 {voice_text}" if voice_text else "🎙 Озвучка не указана", self)
        self.voice_label.setFixedWidth(176)
        self.voice_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.voice_label.setStyleSheet("font-size: 11px; color: #a1a1aa; font-style: italic;")
        layout.addWidget(self.voice_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        spin_layout = QHBoxLayout()
        
        self.season_spin = QSpinBox(self)
        self.season_spin.setPrefix("Сез. ")
        self.season_spin.setValue(self.data.get("season", 1))
        self.season_spin.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.season_spin.setToolTip("Текущий сезон")
        self.season_spin.installEventFilter(self)
        self.season_spin.valueChanged.connect(self.save_progress)
        
        self.episode_spin = QSpinBox(self)
        self.episode_spin.setPrefix("Сер. ")
        self.episode_spin.setValue(self.data.get("episode", 1))
        self.episode_spin.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.episode_spin.setToolTip("Текущая просмотренная серия")
        self.episode_spin.installEventFilter(self)
        self.episode_spin.valueChanged.connect(self.save_progress)
        
        spin_layout.addWidget(self.season_spin)
        spin_layout.addWidget(self.episode_spin)
        layout.addLayout(spin_layout)
        
        control_layout = QHBoxLayout()
        
        play_btn = QPushButton("▶ Смотреть", self)
        play_btn.setToolTip("Перейти на сайт просмотра")
        play_btn.setStyleSheet("background-color: #16a34a; color: white; font-weight: bold; padding: 6px; border-radius: 6px; font-size: 12px;")
        play_btn.clicked.connect(self.play_anime)
        
        edit_btn = QPushButton(self)
        edit_btn.setObjectName("card_edit_btn") # Привязываем к QSS
        edit_btn.setIcon(QIcon(":/icons/sprites/pencil.png"))
        edit_btn.setFixedSize(34, 28)
        edit_btn.setToolTip("Редактировать релиз")
        edit_btn.clicked.connect(lambda: self.on_edit(self.data))
        
        control_layout.addWidget(play_btn)
        control_layout.addWidget(edit_btn)
        layout.addLayout(control_layout)
        
        if theme == "dark":
            self.setStyleSheet("AnimeCard { border: 1px solid #3f3f46; border-radius: 8px; background-color: #2d2d34; } AnimeCard:hover { border: 1px solid #3b82f6; background-color: #35353d; }")
        else:
            self.setStyleSheet("AnimeCard { border: 1px solid #d4d4d8; border-radius: 8px; background-color: #ffffff; } AnimeCard:hover { border: 1px solid #2563eb; background-color: #f8fafc; }")

    def eventFilter(self, watched, event):
        if isinstance(watched, QSpinBox):
            if event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton and event.type() != QEvent.Type.MouseButtonDblClick:
                    QTimer.singleShot(1, watched.lineEdit().deselect)
            if event.type() == QEvent.Type.FocusIn:
                QTimer.singleShot(1, watched.lineEdit().deselect)
        return super().eventFilter(watched, event)

    def save_progress(self):
        self.data["season"] = self.season_spin.value()
        self.data["episode"] = self.episode_spin.value()
        self.on_update()
        QTimer.singleShot(1, self.season_spin.lineEdit().deselect)
        QTimer.singleShot(1, self.episode_spin.lineEdit().deselect)

    def show_rating_menu(self):
        menu = QMenu(self)
        for i in range(1, 6):
            action = QAction(f"⭐ {i}", self)
            action.triggered.connect(lambda checked, val=i: self.set_rating(val))
            menu.addAction(action)
        
        clear_action = QAction("Сбросить", self)
        clear_action.triggered.connect(lambda: self.set_rating(None))
        menu.addAction(clear_action)
        menu.exec(self.rate_btn.mapToGlobal(self.rate_btn.rect().bottomLeft()))

    def set_rating(self, val):
        self.data["rating"] = val
        self.rate_btn.setText(f"⭐ {val}" if val else "⭐ —")
        self.on_update()

    def confirm_and_delete(self):
        title = self.data.get("title", "это аниме")
        reply = QMessageBox.question(self, "Подтверждение", f"Удалить аниме \"{title}\" навсегда?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes: self.on_delete(self.data)

    def update_cover(self):
        cover_path = self.data.get("cover", "").strip()
        if not cover_path:
            self.img_label.setText("Нет обложки")
            return

        if cover_path.startswith("http"):
            if cover_path in self.app_instance.cover_cache:
                self.set_scaled_pixmap(self.app_instance.cover_cache[cover_path])
                return

            url_hash = hashlib.md5(cover_path.encode('utf-8')).hexdigest()
            local_cache_path = os.path.join(CACHE_DIR, f"{url_hash}.png")
            
            if os.path.exists(local_cache_path):
                pixmap = QPixmap()
                if pixmap.load(local_cache_path):
                    self.app_instance.cover_cache[cover_path] = pixmap
                    self.set_scaled_pixmap(pixmap)
                    return

            self.img_label.setText("Загрузка...")
            self.app_instance.start_url_loader(str(self.anime_id), cover_path, self.on_single_load)
        
        elif os.path.exists(cover_path):
            self.set_scaled_pixmap(QPixmap(cover_path))
        else:
            rel_path = os.path.basename(cover_path)
            local_project_path = os.path.join(COVERS_DIR, rel_path)
            if os.path.exists(local_project_path):
                self.set_scaled_pixmap(QPixmap(local_project_path))
            else:
                self.img_label.setText("Файл не найден")

    def on_single_load(self, pixmap):
        if sip.isdeleted(self) or sip.isdeleted(self.img_label): return
        if not pixmap.isNull():
            if pixmap.width() > 400 or pixmap.height() > 400:
                pixmap = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                
            url = self.data.get("cover")
            self.app_instance.cover_cache[url] = pixmap
            self.set_scaled_pixmap(pixmap)
        else:
            self.img_label.setText("Ошибка загрузки")

    def set_scaled_pixmap(self, pixmap):
        if sip.isdeleted(self) or sip.isdeleted(self.img_label): return
        if not pixmap.isNull():
            scaled = pixmap.scaled(176, 176, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.img_label.setPixmap(scaled)

    def play_anime(self):
        link = self.data.get("link", "").strip()
        if link: webbrowser.open(link)
        else: webbrowser.open(f"https://www.google.com/search?q=смотреть+аниме+{self.data.get('title', '')}")


class AnimeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cover_cache = {}
        self.config = load_config()
        
        # Переменные для запоминания вкладки до начала поиска
        self.tab_before_search = 0
        self.is_searching = False
        
        self.setWindowTitle("Мой Аниме Список")
        self.resize(940, 680)
        self.setWindowIcon(QIcon(":/icons/sprites/app_icon.ico"))
        
        self.apply_theme_style()
        
        self.anime_list = load_data()
        self.url_loaders = {}
        
        self.init_ui()
        self.refresh_grids()
        self.showMaximized()

    def apply_theme_style(self):
        # Получаем прозрачность из конфига (по умолчанию 85%, если не задано)
        opacity_pct = self.config.get("opacity", 85)
        # Переводим проценты (0-100) в альфа-канал для CSS (0.0 - 1.0)
        alpha = opacity_pct / 100.0

        # Формируем цвета в зависимости от выбранной темы
        if self.config.get("theme", "dark") == "dark":
            # Для темной темы базовый фон окон: #18181b -> rgba(24, 24, 27, alpha)
            pane_rgba = f"rgba(24, 24, 27, {alpha})"
            content_rgba = f"rgba(24, 24, 27, {alpha})"
            base_style = DARK_STYLE.format(pane_rgba=pane_rgba, content_rgba=content_rgba)
        else:
            # Для светлой темы базовый фон окон: #ffffff -> rgba(255, 255, 255, alpha)
            pane_rgba = f"rgba(255, 255, 255, {alpha})"
            content_rgba = f"rgba(255, 255, 255, {alpha})"
            base_style = LIGHT_STYLE.format(pane_rgba=pane_rgba, content_rgba=content_rgba)
            
        self.setStyleSheet(base_style)
        self.update_wallpaper_background()

    def update_wallpaper_background(self):
        if self.config.get("use_wallpaper", False) and self.config.get("wallpaper_path", ""):
            wp_path = self.config["wallpaper_path"].replace("\\", "/")
            if os.path.exists(wp_path):
                self.setStyleSheet(self.styleSheet() + f"\nQMainWindow {{ background-image: url('{wp_path}'); background-position: center; background-repeat: no-repeat; background-attachment: fixed; }}")

    def init_ui(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        
        top_layout = QHBoxLayout()
        add_btn = QPushButton("+ Добавить новый релиз", self)
        add_btn.setStyleSheet("font-size: 13px; padding: 8px 18px; background-color: #2563eb; color: white; border-radius: 6px; font-weight: bold; border: none;")
        add_btn.clicked.connect(self.add_anime)
        top_layout.addWidget(add_btn)
        
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("🔍 Поиск релиза по названию...")
        self.search_input.setFixedWidth(280)
        self.search_input.textChanged.connect(self.handle_search_changed)
        top_layout.addWidget(self.search_input)
        
        top_layout.addStretch()
        
        settings_btn = QPushButton("⚙ Настройки", self)
        settings_btn.setStyleSheet("font-size: 13px; padding: 8px 14px; background-color: #27272a; color: #f4f4f5; border-radius: 6px; border: 1px solid #3f3f46;")
        settings_btn.clicked.connect(self.open_settings)
        top_layout.addWidget(settings_btn)
        
        self.main_layout.addLayout(top_layout)
        
        self.tabs = QTabWidget(self)
        self.tabs.currentChanged.connect(self.handle_tab_changed)
        self.main_layout.addWidget(self.tabs)
        
        self.current_grid_layout = QGridLayout()
        self.current_grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        current_widget = QWidget()
        current_widget.setObjectName("scroll_content")
        current_widget.setLayout(self.current_grid_layout)
        self.current_scroll = QScrollArea()
        self.current_scroll.setWidgetResizable(True)
        self.current_scroll.setWidget(current_widget)
        
        self.favorite_grid_layout = QGridLayout()
        self.favorite_grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        favorite_widget = QWidget()
        favorite_widget.setObjectName("scroll_content")
        favorite_widget.setLayout(self.favorite_grid_layout)
        self.favorite_scroll = QScrollArea()
        self.favorite_scroll.setWidgetResizable(True)
        self.favorite_scroll.setWidget(favorite_widget)
        
        self.archive_grid_layout = QGridLayout()
        self.archive_grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        archive_widget = QWidget()
        archive_widget.setObjectName("scroll_content")
        archive_widget.setLayout(self.archive_grid_layout)
        self.archive_scroll = QScrollArea()
        self.archive_scroll.setWidgetResizable(True)
        self.archive_scroll.setWidget(archive_widget)
        
        self.tabs.addTab(self.current_scroll, "📺 Смотрю")
        self.tabs.addTab(self.favorite_scroll, QIcon(":/icons/sprites/star_full.png"), "Избранное")
        self.tabs.addTab(self.archive_scroll, "📦 Архив")
        
        self.update_tab_counters()

    def update_tab_counters(self):
        QTimer.singleShot(1, self._execute_count)

    def _execute_count(self):
        count_current = 0
        count_favorite = 0
        count_archive = 0

        # Получаем текущий поисковый запрос (приводим к нижнему регистру)
        search_query = self.search_input.text().strip().lower() if hasattr(self, 'search_input') else ""

        for anime_data in self.anime_list:
            title = anime_data.get("title", "").lower()
            
            # Если есть поисковый запрос и название аниме под него не подходит — пропускаем его (не считаем)
            if search_query and search_query not in title:
                continue

            # Считаем только те карточки, которые прошли фильтр поиска
            if anime_data.get("favorite", False):
                count_favorite += 1
            
            if anime_data.get("archived", False):
                count_archive += 1
            else:
                count_current += 1

        # Обновляем текст на вкладках с актуальными цифрами
        self.tabs.setTabText(0, f"📺 Смотрю ({count_current})")
        self.tabs.setTabText(1, f"Избранное ({count_favorite})")
        self.tabs.setTabText(2, f"📦 Архив ({count_archive})")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.refresh_grids()

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.config = load_config()
            self.apply_theme_style()
            self.refresh_grids()

    def handle_tab_changed(self, index):
        # Запоминаем вкладку только тогда, когда пользователь переключает их вручную без активного поиска
        if not self.is_searching:
            self.tab_before_search = index
        self.refresh_grids()

    def handle_search_changed(self, text):
        query = text.strip().lower()
        
        if not query:
            self.is_searching = False
            self.tabs.setCurrentIndex(self.tab_before_search)
            self.refresh_grids()
            self.update_tab_counters() # Добавлено: обновляем счетчики при очистке
            return

        if not self.is_searching:
            self.tab_before_search = self.tabs.currentIndex()
            self.is_searching = True

        current_tab = self.tabs.currentIndex()
        has_matches_in_current = self.check_matches_in_tab(current_tab, query)
        
        if not has_matches_in_current:
            if current_tab != 0 and self.check_matches_in_tab(0, query):
                self.tabs.setCurrentIndex(0)
            elif current_tab != 2 and self.check_matches_in_tab(2, query):
                self.tabs.setCurrentIndex(2)
                
        self.refresh_grids()
        self.update_tab_counters() # Добавлено: динамически обновляем счетчики при вводе текста

    def check_matches_in_tab(self, tab_index, query):
        """Вспомогательный метод для проверки наличия результатов в конкретной вкладке"""
        for anime in self.anime_list:
            title = anime.get("title", "").lower()
            if query in title:
                if tab_index == 0 and not anime.get("archived", False):
                    return True
                if tab_index == 1 and anime.get("favorite", False):
                    return True
                if tab_index == 2 and anime.get("archived", False):
                    return True
        return False

    def refresh_grids(self):
        for uid in list(self.url_loaders.keys()):
            thread = self.url_loaders[uid]
            if thread and thread.isFinished():
                del self.url_loaders[uid]

        for grid in [self.current_grid_layout, self.favorite_grid_layout, self.archive_grid_layout]:
            while grid.count():
                item = grid.takeAt(0)
                widget = item.widget()
                if widget: widget.deleteLater()

        tab_width = self.tabs.width()
        card_width = 210  
        columns = max(3, tab_width // card_width) 

        current_idx = 0
        favorite_idx = 0
        archive_idx = 0
        
        search_query = self.search_input.text().strip().lower() if hasattr(self, 'search_input') else ""
        
        for index, anime_data in enumerate(self.anime_list):
            title = anime_data.get("title", "").lower()
            
            # Фильтрация карточек на лету
            if search_query and search_query not in title:
                continue
                
            card = AnimeCard(
                index, anime_data, 
                self.update_anime_data, self.edit_anime, self.toggle_archive, self.toggle_favorite, self.delete_anime, 
                self
            )
            
            if anime_data.get("archived", False):
                self.archive_grid_layout.addWidget(card, archive_idx // columns, archive_idx % columns)
                archive_idx += 1
            else:
                self.current_grid_layout.addWidget(card, current_idx // columns, current_idx % columns)
                current_idx += 1
                
            if anime_data.get("favorite", False):
                fav_card = AnimeCard(
                    index, anime_data, 
                    self.update_anime_data, self.edit_anime, self.toggle_archive, self.toggle_favorite, self.delete_anime, 
                    self
                )
                self.favorite_grid_layout.addWidget(fav_card, favorite_idx // columns, favorite_idx % columns)
                favorite_idx += 1

        if current_idx > 0: self.current_grid_layout.setColumnStretch(columns, 1)
        if favorite_idx > 0: self.favorite_grid_layout.setColumnStretch(columns, 1)
        if archive_idx > 0: self.archive_grid_layout.setColumnStretch(columns, 1)

    def add_anime(self):
        dialog = EditAnimeDialog(self)
        if dialog.exec():
            new_anime = dialog.get_data()
            if new_anime["title"]:
                new_anime.update({"season": 1, "episode": 1, "archived": False, "favorite": False, "rating": None})
                self.anime_list.append(new_anime)
                save_data(self.anime_list)
                self.refresh_grids()
                self.update_tab_counters()

    def edit_anime(self, item_data):
        dialog = EditAnimeDialog(self, edit_data=item_data)
        if dialog.exec():
            updated_fields = dialog.get_data()
            item_data.update(updated_fields)
            save_data(self.anime_list)
            self.refresh_grids()

    def delete_anime(self, item_data):
        if item_data in self.anime_list:
            self.anime_list.remove(item_data)
            save_data(self.anime_list)
            self.refresh_grids()
            self.update_tab_counters()

    def start_url_loader(self, uid, url, callback):
        if url in [t.url for t in self.url_loaders.values() if hasattr(t, 'url')]:
            return
            
        thread = ImageLoaderThread(uid, url)
        thread.setParent(self) 
        thread.loaded.connect(lambda uid, pixmap: self.on_url_loaded(uid, pixmap, callback))
        thread.finished.connect(thread.deleteLater)
        
        self.url_loaders[uid] = thread
        thread.start()

    def on_url_loaded(self, uid, pixmap, callback):
        if uid in self.url_loaders:
            del self.url_loaders[uid]
            if callback and hasattr(callback, '__self__') and not sip.isdeleted(callback.__self__):
                callback(pixmap)

    def update_anime_data(self):
        save_data(self.anime_list)
        self.update_tab_counters()

    def toggle_archive(self, item_data):
        item_data["archived"] = not item_data.get("archived", False)
        save_data(self.anime_list)
        self.refresh_grids()
        self.update_tab_counters()

    def toggle_favorite(self, item_data):
        item_data["favorite"] = not item_data.get("favorite", False)
        save_data(self.anime_list)
        self.refresh_grids()
        self.update_tab_counters()

    def closeEvent(self, event):
        for uid in list(self.url_loaders.keys()):
            thread = self.url_loaders[uid]
            thread.requestInterruption() 
            thread.quit()
            if not thread.wait(1000):
                thread.terminate() 
        event.accept()


if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--no-sandbox'
        os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1'
        
    sys.argv.append("--log-level=3")
    
    app = QApplication(sys.argv)
    window = AnimeApp()
    window.show()
    sys.exit(app.exec())