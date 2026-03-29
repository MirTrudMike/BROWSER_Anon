import hashlib
import time

from .logger import logger
from .parameters import (
    webgl_variants, canvas_variants, audio_variants, local_ip_variants,
    hardware_variants, battery_variants, plugins_variants, canvas_2d_variants,
    fonts_variants, screen_variants, user_behavior_variants,
    history_variants, network_variants,
)


class FingerprintGenerator:
    """
    Generates a browser fingerprint configuration for a given platform and browser.

    Uses deterministic randomization based on a session hash: the same session
    always produces the same parameter set, while different sessions produce
    different sets.
    """

    # Edge uses the same plugins as Chrome
    BROWSER_PLUGIN_MAP = {
        "Chrome":  "Chrome",
        "Edge":    "Chrome",
        "Firefox": "Firefox",
        "Safari":  "Chrome",
    }

    def __init__(self, system: str, browser: str):
        self.system  = system
        self.browser = browser
        self._session_hash = self._generate_session_hash()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self) -> dict:
        """Generate and return the full fingerprint configuration dict."""
        try:
            logger.info(f"Creating fingerprint for system: {self.system}, browser: {self.browser}")
            plugin_browser = self.BROWSER_PLUGIN_MAP.get(self.browser, "Chrome")

            webgl        = self._select("webgl",    webgl_variants[self.system])
            canvas       = self._select("canvas",   canvas_variants[self.system])
            audio        = self._select("audio",    audio_variants[self.system])
            local_ip_set = self._select("ip",       local_ip_variants)
            hardware     = self._select("hardware", hardware_variants[self.system])
            battery      = self._select("battery",  battery_variants)
            plugins      = self._select("plugins",  plugins_variants[plugin_browser])

            canvas_2d_raw = self._select("canvas2d", canvas_2d_variants[self.system])
            canvas_2d = {
                "red":     canvas_2d_raw.get("red",     1),
                "green":   canvas_2d_raw.get("green",   2),
                "blue":    canvas_2d_raw.get("blue",    3),
                "quality": canvas_2d_raw.get("quality", 0.92),
                "font":    canvas_2d_raw.get("font",    "12px Arial"),
            }

            fonts  = self._select("fonts",  fonts_variants[self.system])
            screen = self._select("screen", screen_variants[self.system])

            mouse_behavior = {
                "moveSpeed":        self._select("mouse_speed", user_behavior_variants["mouse"]["moveSpeed"]),
                "clickDelay":       self._select("click_delay", user_behavior_variants["mouse"]["clickDelay"]),
                "doubleClickDelay": self._select("dbl_click",   user_behavior_variants["mouse"]["doubleClickDelay"]),
            }
            keyboard_behavior = {
                "typingSpeed":    self._select("typing_speed", user_behavior_variants["keyboard"]["typingSpeed"]),
                "typingVariance": self._select("typing_var",   user_behavior_variants["keyboard"]["typingVariance"]),
                "keyPressTime":   self._select("key_press",    user_behavior_variants["keyboard"]["keyPressTime"]),
            }
            scroll_behavior = {
                "speed":      self._select("scroll_speed",  user_behavior_variants["scroll"]["speed"]),
                "smoothness": self._select("scroll_smooth", user_behavior_variants["scroll"]["smoothness"]),
                "pauseTime":  self._select("scroll_pause",  user_behavior_variants["scroll"]["pauseTime"]),
            }

            history = {
                "visitFrequency": self._select("visit_freq",    history_variants["visitFrequency"]),
                "timeSpent":      self._select("time_spent",    history_variants["timeSpent"]),
                "bookmarkCount":  self._select("bookmarks",     history_variants["bookmarkCount"]),
                "historyDepth":   self._select("history_depth", history_variants["historyDepth"]),
            }

            network = {
                "bandwidth":      self._select("bandwidth",   network_variants["bandwidth"]),
                "latency":        self._select("latency",     network_variants["latency"]),
                "packetLoss":     self._select("packet_loss", network_variants["packetLoss"]),
                "connectionType": self._select("connection",  network_variants["connectionType"]),
            }

            # Apply small per-session variations to numeric parameters
            audio["noiseIntensity"]          *= (0.95 + self._consistent_random("noise")      * 0.1)
            canvas["quality"]                *= (0.98 + self._consistent_random("quality")    * 0.04)
            mouse_behavior["moveSpeed"]      *= (0.95 + self._consistent_random("mouse_var")  * 0.1)
            keyboard_behavior["typingSpeed"] *= (0.95 + self._consistent_random("typing_var") * 0.1)
            scroll_behavior["speed"]         *= (0.95 + self._consistent_random("scroll_var") * 0.1)

            config = {
                "hardware":    hardware,
                "local_ip_set": local_ip_set,
                "webgl":       webgl,
                "canvas":      canvas,
                "audio":       audio,
                "battery":     battery,
                "usb": {
                    "disableUSB": bool(self._consistent_random("usb") > 0.5),
                    "disableHID": bool(self._consistent_random("hid") > 0.5),
                },
                "plugins":   plugins,
                "canvas_2d": canvas_2d,
                "fonts":     fonts,
                "screen":    screen,
                "user_behavior": {
                    "mouse":    mouse_behavior,
                    "keyboard": keyboard_behavior,
                    "scroll":   scroll_behavior,
                },
                "history": history,
                "network":  network,
            }

            logger.info("Fingerprint generated successfully")
            logger.debug(f"Fingerprint config: {config}")
            return config

        except Exception as e:
            logger.exception(e, "Error generating fingerprint")
            raise

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _generate_session_hash(self) -> str:
        try:
            current_time = str(time.time()).encode("utf-8")
            session_hash = hashlib.md5(current_time).hexdigest()
            logger.debug(f"Generated session hash: {session_hash}")
            return session_hash
        except Exception as e:
            logger.exception(e, "Error generating session hash")
            raise

    def _consistent_random(self, salt: str) -> float:
        """Return a deterministic float in [0, 1) derived from session hash + salt."""
        try:
            combined = (self._session_hash + salt).encode("utf-8")
            hash_value = hashlib.md5(combined).hexdigest()
            return int(hash_value, 16) / 2 ** 128
        except Exception as e:
            logger.exception(e, f"Error generating consistent random with salt '{salt}'")
            raise

    def _select(self, salt: str, items: list):
        """Deterministically pick one item from a list using the session hash."""
        try:
            index    = int(self._consistent_random(salt) * len(items))
            selected = items[index]
            logger.debug(f"Selected item with salt '{salt}': {selected}")
            return selected
        except Exception as e:
            logger.exception(e, f"Error selecting from list with salt '{salt}'")
            raise
