import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QMessageBox
)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QEventLoop
import asyncio
from functools import partial
from testing import read_country_config_file
from testing import start_browser
from logger_config import log_info, log_debug, log_exception, log_warning, log_error

code_to_str = {'ru': '🇷🇺 Russia',
               'ge': '🇬🇪 Georgia',
               'il': '🇮🇱 Israel',
               'ae': '🇦🇪 UAE',
               'de': '🇩🇪 Germany',
               'gb': '🇬🇧 Great Britain',
               'tr': '🇹🇷 Turkey',
               'us': '🇺🇸 USA',
               'fr': '🇫🇷 France',
               'kr': '🇰🇷 Korea',
               'am': '🇦🇲 Armenia'}

str_to_code = {}
for code, string in code_to_str.items():
    str_to_code.update({string: code})

try:
    log_debug("Loading country configuration...")
    country_list = [code_to_str[code] for code in read_country_config_file().keys()]
    log_info(f"Loaded {len(country_list)} countries")
except Exception as e:
    log_exception(e, "Failed to load country configuration")
    sys.exit(1)

# country = str_to_code[self.country_combo.currentText()]
# country = str_to_code[self.country_combo.currentText()]


# Основное окно приложения
class BrowserLauncherApp(QMainWindow):
    def __init__(self):
        try:
            log_info("Initializing Browser Launcher application")
            super().__init__()
            self.setWindowTitle("Browser Launcher")
            self.setGeometry(100, 100, 400, 300)
            self.setup_ui()
            self.apply_dark_theme()
            self.browser = None
            self.loop = asyncio.new_event_loop()  # Создаем новый цикл событий
            log_info("Browser Launcher initialized successfully")
        except Exception as e:
            log_exception(e, "Failed to initialize Browser Launcher")
            raise

    def setup_ui(self):
        try:
            log_debug("Setting up UI components")
            # Основной контейнер
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.layout = QVBoxLayout(self.central_widget)

            # Приветствие
            self.welcome_label = QLabel("Добро пожаловать в Browser Launcher!")
            self.welcome_label.setFont(QFont("Arial", 14))
            self.welcome_label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(self.welcome_label)

            # Выбор страны
            self.country_label = QLabel("Выберите страну:")
            self.country_label.setFont(QFont("Arial", 12))
            self.layout.addWidget(self.country_label)

            font = QFont("Noto Color Emoji")
            self.country_combo = QComboBox()
            self.country_combo.setFont(font)
            self.country_combo.addItems(country_list)  # Пример списка стран
            self.country_combo.currentIndexChanged.connect(self.on_country_selected)
            self.layout.addWidget(self.country_combo)

            # Кнопка запуска
            self.launch_button = QPushButton("Запуск")
            self.launch_button.setFont(QFont("Arial", 12))
            self.launch_button.setEnabled(False)  # По умолчанию отключена
            self.launch_button.clicked.connect(self.on_launch_clicked)
            self.layout.addWidget(self.launch_button)

            # Отображение конфигурации
            self.config_label = QLabel("Конфигурация:")
            self.config_label.setFont(QFont("Arial", 12))
            self.layout.addWidget(self.config_label)

            self.config_display = QLabel("")
            self.config_display.setFont(QFont("Arial", 10))
            self.config_display.setAlignment(Qt.AlignLeft)
            self.layout.addWidget(self.config_display)

            # Кнопки "Обновить" и "Выход"
            self.button_layout = QHBoxLayout()
            self.refresh_button = QPushButton("Обновить конфигурацию")
            self.refresh_button.setFont(QFont("Arial", 12))
            self.refresh_button.clicked.connect(self.on_refresh_clicked)
            self.button_layout.addWidget(self.refresh_button)

            self.exit_button = QPushButton("Выход")
            self.exit_button.setFont(QFont("Arial", 12))
            self.exit_button.clicked.connect(self.on_exit_clicked)
            self.button_layout.addWidget(self.exit_button)

            self.layout.addLayout(self.button_layout)
            log_debug("UI setup completed")
        except Exception as e:
            log_exception(e, "Failed to setup UI")
            raise

    def apply_dark_theme(self):
        try:
            log_debug("Applying dark theme")
            # Темная тема
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.WindowText, Qt.white)
            dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
            dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
            dark_palette.setColor(QPalette.ToolTipText, Qt.white)
            dark_palette.setColor(QPalette.Text, Qt.white)
            dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ButtonText, Qt.white)
            dark_palette.setColor(QPalette.BrightText, Qt.red)
            dark_palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
            dark_palette.setColor(QPalette.HighlightedText, Qt.black)
            QApplication.setPalette(dark_palette)
            log_debug("Dark theme applied successfully")
        except Exception as e:
            log_exception(e, "Failed to apply dark theme")
            raise

    def on_country_selected(self):
        try:
            country = self.country_combo.currentText()
            log_info(f"Country selected: {country}")
            self.launch_button.setEnabled(True)
        except Exception as e:
            log_exception(e, "Error in country selection")

    def on_launch_clicked(self):
        try:
            country = str_to_code[self.country_combo.currentText()]
            log_info(f"Launching browser for country: {country}")

            if self.browser:
                log_debug("Closing existing browser session")
                asyncio.run_coroutine_threadsafe(self.close_browser(), self.loop)

            log_debug("Starting new browser session")
            future = asyncio.run_coroutine_threadsafe(self.launch_browser(country), self.loop)
            self.browser_task = future
        except Exception as e:
            log_exception(e, "Failed to launch browser")
            QMessageBox.critical(self, "Error", f"Failed to launch browser: {str(e)}")

    async def launch_browser(self, country):
        try:
            log_info(f"Starting browser launch process for country: {country}")
            self.browser, config = await start_browser(country)
            
            if not self.browser or not config:
                log_error("Browser or configuration is None")
                QMessageBox.critical(self, "Error", "Failed to start browser")
                return
                
            log_info("Updating configuration display")
            self.update_config_display(config)
            
        except Exception as e:
            log_exception(e, "Error in browser launch process")
            QMessageBox.critical(self, "Error", f"Browser launch failed: {str(e)}")

    def update_config_display(self, config):
        try:
            log_info("Updating configuration display")
            config_text = (
                f"Страна: {config['proxy_info']['country']}\n"
                f"Город: {config['proxy_info']['city']}\n"
                f"ОС: {config['system']}\n"
            )
            self.config_display.setText(config_text)
            log_info("Configuration display updated")
        except Exception as e:
            log_exception(e, "Failed to update configuration display")

    async def close_browser(self):
        try:
            if self.browser:
                log_info("Closing browser")
                await self.browser.close()
                self.browser = None
                log_info("Browser closed successfully")
        except Exception as e:
            log_exception(e, "Error closing browser")

    def on_refresh_clicked(self):
        try:
            country = str_to_code[self.country_combo.currentText()]
            log_info(f"Refreshing browser for country: {country}")
            asyncio.run_coroutine_threadsafe(self.close_browser(), self.loop)
            asyncio.run_coroutine_threadsafe(self.launch_browser(country), self.loop)
        except Exception as e:
            log_exception(e, "Failed to refresh browser")
            QMessageBox.critical(self, "Error", f"Failed to refresh browser: {str(e)}")

    def on_exit_clicked(self):
        try:
            log_info("Exiting application")
            asyncio.run_coroutine_threadsafe(self.close_browser(), self.loop)
            self.close()  # Закрываем окно GUI
        except Exception as e:
            log_exception(e, "Error during application exit")
            sys.exit(1)


if __name__ == "__main__":
    try:
        log_info("Starting Browser Launcher application")
        app = QApplication(sys.argv)
        window = BrowserLauncherApp()

        # Запускаем цикл событий asyncio в отдельном потоке
        def run_asyncio_loop():
            try:
                log_debug("Starting asyncio event loop")
                asyncio.set_event_loop(window.loop)
                window.loop.run_forever()
            except Exception as e:
                log_exception(e, "Error in asyncio event loop")
                sys.exit(1)

        import threading
        threading.Thread(target=run_asyncio_loop, daemon=True).start()
        log_info("Asyncio event loop started in background thread")

        window.show()
        log_info("Application window shown")
        sys.exit(app.exec_())
    except Exception as e:
        log_exception(e, "Fatal error in main application")
        sys.exit(1)


