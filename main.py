import sys
import os
import asyncio
import threading

from PyQt5.QtWidgets import QApplication

from browser.proxy import ProxyManager
from browser.launcher import BrowserLauncher
from browser.gui import BrowserLauncherApp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    proxy_manager = ProxyManager(
        proxies_file=os.path.join(BASE_DIR, "proxies.json"),
        used_ips_file=os.path.join(BASE_DIR, "used_ips.json"),
    )
    launcher = BrowserLauncher(
        country_config_file=os.path.join(BASE_DIR, "country_config.json"),
        proxy_manager=proxy_manager,
    )

    app = QApplication(sys.argv)
    window = BrowserLauncherApp(launcher)

    def run_asyncio_loop():
        try:
            asyncio.set_event_loop(window._loop)
            window._loop.run_forever()
        except Exception as e:
            from browser.logger import logger
            logger.exception(e, "Error in asyncio event loop")
            sys.exit(1)

    threading.Thread(target=run_asyncio_loop, daemon=True).start()

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
