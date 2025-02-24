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

code_to_str = {'ru': '🇷🇺 Russia',
               'ge': '🇬🇪 Georgia',
               'il': '🇮🇱 Israel',
               'ae': '🇦🇪 UAE',
               'de': '🇩🇪 Germany',
               'gb': '🇬🇧 Great Britain',
               'tr': '🇹🇷 Turkey',
               'us': '🇺🇸 USA',
               'fr': '🇫🇷 France'}

str_to_code = {}
for code, string in code_to_str.items():
    str_to_code.update({string: code})

country_list = [code_to_str[code] for code in read_country_config_file().keys()]

# country = str_to_code[self.country_combo.currentText()]
# country = str_to_code[self.country_combo.currentText()]


# Основное окно приложения
class BrowserLauncherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Browser Launcher")
        self.setGeometry(100, 100, 400, 300)
        self.setup_ui()
        self.apply_dark_theme()
        self.browser = None
        self.loop = asyncio.new_event_loop()  # Создаем новый цикл событий

    def setup_ui(self):
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

    def apply_dark_theme(self):
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

    def on_country_selected(self):
        # Активируем кнопку запуска при выборе страны
        self.launch_button.setEnabled(True)

    def on_launch_clicked(self):
        # Запуск браузера
        country = str_to_code[self.country_combo.currentText()]

        # Если уже есть запущенный браузер, закрываем его перед новым запуском
        if self.browser:
            asyncio.run_coroutine_threadsafe(self.close_browser(), self.loop)

        # Запускаем новую сессию браузера
        future = asyncio.run_coroutine_threadsafe(self.launch_browser(country), self.loop)

        # Сохраняем Future, чтобы можно было контролировать выполнение
        self.browser_task = future

    async def launch_browser(self, country):
        # Запуск браузера и обновление конфигурации
        self.browser, config = await start_browser(country)
        self.update_config_display(config)

        self.browser = self.browser

        await self.browser.wait_for_event("close")  # Ждем закрытия браузера
        self.browser = None

    def update_config_display(self, config):
        # Обновление отображения конфигурации
        config_text = (
            f"Страна: {config['proxy_info']['country']}\n"
            f"Город: {config['proxy_info']['city']}\n"
            f"ОС: {config['system']}\n"
        )
        self.config_display.setText(config_text)

    async def close_browser(self):
        if self.browser:
            await self.browser.close()  # Закрываем браузер
            self.browser = None  # Убираем ссылку на браузер

    def on_refresh_clicked(self):
        # Обновление конфигурации
        country = str_to_code[self.country_combo.currentText()]
        asyncio.run_coroutine_threadsafe(self.close_browser(), self.loop)
        asyncio.run_coroutine_threadsafe(self.launch_browser(country), self.loop)

    def on_exit_clicked(self):
        # Закрытие браузера и приложения
        asyncio.run_coroutine_threadsafe(self.close_browser(), self.loop)
        self.close()  # Закрываем окно GUI


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrowserLauncherApp()

    # Запускаем цикл событий asyncio в отдельном потоке
    def run_asyncio_loop():
        asyncio.set_event_loop(window.loop)
        window.loop.run_forever()

    import threading
    threading.Thread(target=run_asyncio_loop, daemon=True).start()

    window.show()
    sys.exit(app.exec_())


