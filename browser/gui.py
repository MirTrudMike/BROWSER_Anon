import sys
import asyncio

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QMessageBox,
)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt

from .launcher import BrowserLauncher
from .logger import logger


# Country code → display name mapping with flag emoji.
# To add a new country: add an entry here, then add data to
# country_config.json and proxies.json.
COUNTRY_DISPLAY_NAMES: dict[str, str] = {
    "ru": "🇷🇺 Russia",
    "ge": "🇬🇪 Georgia",
    "il": "🇮🇱 Israel",
    "ae": "🇦🇪 UAE",
    "de": "🇩🇪 Germany",
    "gb": "🇬🇧 Great Britain",
    "tr": "🇹🇷 Turkey",
    "us": "🇺🇸 USA",
    "fr": "🇫🇷 France",
    "kr": "🇰🇷 Korea",
    "am": "🇦🇲 Armenia",
}


class BrowserLauncherApp(QMainWindow):
    """
    Main application window.

    Accepts a BrowserLauncher as a dependency, keeping GUI and
    browser logic cleanly separated.
    """

    def __init__(self, launcher: BrowserLauncher):
        try:
            logger.info("Initializing Browser Launcher application")
            super().__init__()

            self._launcher = launcher
            self._loop     = asyncio.new_event_loop()

            # Build country list from config, filtered by COUNTRY_DISPLAY_NAMES
            available = launcher.load_available_countries()
            self._country_list    = [
                COUNTRY_DISPLAY_NAMES[code]
                for code in available
                if code in COUNTRY_DISPLAY_NAMES
            ]
            self._display_to_code = {v: k for k, v in COUNTRY_DISPLAY_NAMES.items()}

            self.setWindowTitle("Browser Launcher")
            self.setGeometry(100, 100, 400, 300)
            self._setup_ui()
            self._apply_dark_theme()

            logger.info("Browser Launcher initialized successfully")

        except Exception as e:
            logger.exception(e, "Failed to initialize Browser Launcher")
            raise

    # ------------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------------

    def _setup_ui(self):
        try:
            logger.debug("Setting up UI components")

            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.layout = QVBoxLayout(self.central_widget)

            self.welcome_label = QLabel("Welcome to Browser Launcher!")
            self.welcome_label.setFont(QFont("Arial", 14))
            self.welcome_label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(self.welcome_label)

            self.country_label = QLabel("Select country:")
            self.country_label.setFont(QFont("Arial", 12))
            self.layout.addWidget(self.country_label)

            self.country_combo = QComboBox()
            self.country_combo.setFont(QFont("Noto Color Emoji"))
            self.country_combo.addItems(self._country_list)
            self.country_combo.currentIndexChanged.connect(self._on_country_selected)
            self.layout.addWidget(self.country_combo)

            self.launch_button = QPushButton("Launch")
            self.launch_button.setFont(QFont("Arial", 12))
            self.launch_button.setEnabled(False)
            self.launch_button.clicked.connect(self._on_launch_clicked)
            self.layout.addWidget(self.launch_button)

            self.config_label = QLabel("Configuration:")
            self.config_label.setFont(QFont("Arial", 12))
            self.layout.addWidget(self.config_label)

            self.config_display = QLabel("")
            self.config_display.setFont(QFont("Arial", 10))
            self.config_display.setAlignment(Qt.AlignLeft)
            self.layout.addWidget(self.config_display)

            button_layout = QHBoxLayout()

            self.refresh_button = QPushButton("Refresh configuration")
            self.refresh_button.setFont(QFont("Arial", 12))
            self.refresh_button.clicked.connect(self._on_refresh_clicked)
            button_layout.addWidget(self.refresh_button)

            self.exit_button = QPushButton("Exit")
            self.exit_button.setFont(QFont("Arial", 12))
            self.exit_button.clicked.connect(self._on_exit_clicked)
            button_layout.addWidget(self.exit_button)

            self.layout.addLayout(button_layout)
            logger.debug("UI setup completed")

        except Exception as e:
            logger.exception(e, "Failed to setup UI")
            raise

    def _apply_dark_theme(self):
        try:
            logger.debug("Applying dark theme")
            from PyQt5.QtWidgets import QApplication
            palette = QPalette()
            palette.setColor(QPalette.Window,          QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText,      Qt.white)
            palette.setColor(QPalette.Base,            QColor(35, 35, 35))
            palette.setColor(QPalette.AlternateBase,   QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase,     Qt.white)
            palette.setColor(QPalette.ToolTipText,     Qt.white)
            palette.setColor(QPalette.Text,            Qt.white)
            palette.setColor(QPalette.Button,          QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText,      Qt.white)
            palette.setColor(QPalette.BrightText,      Qt.red)
            palette.setColor(QPalette.Highlight,       QColor(142, 45, 197).lighter())
            palette.setColor(QPalette.HighlightedText, Qt.black)
            QApplication.setPalette(palette)
            logger.debug("Dark theme applied successfully")
        except Exception as e:
            logger.exception(e, "Failed to apply dark theme")
            raise

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_country_selected(self):
        try:
            country = self.country_combo.currentText()
            logger.info(f"Country selected: {country}")
            self.launch_button.setEnabled(True)
        except Exception as e:
            logger.exception(e, "Error in country selection")

    def _on_launch_clicked(self):
        try:
            country = self._display_to_code[self.country_combo.currentText()]
            logger.info(f"Launching browser for country: {country}")
            asyncio.run_coroutine_threadsafe(self._launch_browser(country), self._loop)
        except Exception as e:
            logger.exception(e, "Failed to launch browser")
            QMessageBox.critical(self, "Error", f"Failed to launch browser: {str(e)}")

    def _on_refresh_clicked(self):
        try:
            country = self._display_to_code[self.country_combo.currentText()]
            logger.info(f"Refreshing browser for country: {country}")
            asyncio.run_coroutine_threadsafe(self._launch_browser(country), self._loop)
        except Exception as e:
            logger.exception(e, "Failed to refresh browser")
            QMessageBox.critical(self, "Error", f"Failed to refresh: {str(e)}")

    def _on_exit_clicked(self):
        try:
            logger.info("Exiting application")
            asyncio.run_coroutine_threadsafe(self._launcher.close(), self._loop)
            self.close()
        except Exception as e:
            logger.exception(e, "Error during application exit")
            sys.exit(1)

    # ------------------------------------------------------------------
    # Async operations
    # ------------------------------------------------------------------

    async def _launch_browser(self, country: str):
        try:
            logger.info(f"Starting browser launch process for country: {country}")
            await self._launcher.close()  # Close existing browser if any
            browser, config = await self._launcher.start(country)

            if not browser or not config:
                logger.error("Browser or configuration is None")
                QMessageBox.critical(self, "Error", "Failed to start browser")
                return

            logger.info("Updating configuration display")
            self._update_config_display(config)

        except Exception as e:
            logger.exception(e, "Error in browser launch process")
            QMessageBox.critical(self, "Error", f"Browser launch failed: {str(e)}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _update_config_display(self, config: dict):
        try:
            config_text = (
                f"Country: {config['proxy_info']['country']}\n"
                f"City:    {config['proxy_info']['city']}\n"
                f"OS:      {config['system']}\n"
            )
            self.config_display.setText(config_text)
            logger.info("Configuration display updated")
        except Exception as e:
            logger.exception(e, "Failed to update configuration display")
