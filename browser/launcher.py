import json
import random

from playwright.async_api import async_playwright, Browser, Page

from .fingerprint import FingerprintGenerator
from .logger import logger
from .profiles import ProfileConfig, STEALTH
from .proxy import ProxyManager


# ===========================================================================
# ScriptInjector
# ===========================================================================

class ScriptInjector:
    """
    Injects JavaScript masking scripts into browser pages.

    Each method handles one aspect of fingerprint protection.
    Call inject_all() to apply every script in the correct order.
    """

    @staticmethod
    async def inject_base_masking(page: Page):
        """Remove automation markers and add realistic Chrome properties."""
        await page.add_init_script("""
            // Remove Playwright marker
            delete window.playwright;

            // Mask webdriver flag
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
                configurable: true
            });

            // Inject realistic window.chrome object
            Object.defineProperty(window, 'chrome', {
                get: () => {
                    return {
                        app: {
                            isInstalled: false,
                            InstallState: {
                                DISABLED: 'disabled',
                                INSTALLED: 'installed',
                                NOT_INSTALLED: 'not_installed'
                            },
                            RunningState: {
                                CANNOT_RUN: 'cannot_run',
                                READY_TO_RUN: 'ready_to_run',
                                RUNNING: 'running'
                            }
                        },
                        runtime: {
                            OnInstalledReason: {
                                CHROME_UPDATE: 'chrome_update',
                                INSTALL: 'install',
                                SHARED_MODULE_UPDATE: 'shared_module_update',
                                UPDATE: 'update'
                            },
                            OnRestartRequiredReason: {
                                APP_UPDATE: 'app_update',
                                OS_UPDATE: 'os_update',
                                PERIODIC: 'periodic'
                            },
                            PlatformArch: {
                                ARM: 'arm',
                                ARM64: 'arm64',
                                MIPS: 'mips',
                                MIPS64: 'mips64',
                                X86_32: 'x86-32',
                                X86_64: 'x86-64'
                            },
                            PlatformNaclArch: {
                                ARM: 'arm',
                                MIPS: 'mips',
                                MIPS64: 'mips64',
                                X86_32: 'x86-32',
                                X86_64: 'x86-64'
                            },
                            PlatformOs: {
                                ANDROID: 'android',
                                CROS: 'cros',
                                LINUX: 'linux',
                                MAC: 'mac',
                                OPENBSD: 'openbsd',
                                WIN: 'win'
                            },
                            RequestUpdateCheckStatus: {
                                NO_UPDATE: 'no_update',
                                THROTTLED: 'throttled',
                                UPDATE_AVAILABLE: 'update_available'
                            }
                        }
                    }
                }
            });

            // Override Permissions API to avoid automation detection
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({state: Notification.permission}) :
                    originalQuery(parameters)
            );

            // Inject realistic browser plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    },
                    {
                        0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Viewer"
                    },
                    {
                        0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable"},
                        1: {type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable"},
                        description: "Native Client",
                        filename: "internal-nacl-plugin",
                        length: 2,
                        name: "Native Client"
                    }
                ]
            });

            // Match outerWidth/Height to inner to avoid detection
            Object.defineProperty(window, 'outerWidth', {
                get: () => window.innerWidth
            });
            Object.defineProperty(window, 'outerHeight', {
                get: () => window.innerHeight
            });

            // Ensure window.chrome.runtime exists
            window.chrome = {
                runtime: {}
            };

            // Base WebGL masking (overridden with real values by inject_webgl)
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter.apply(this, arguments);
            };
        """)

    @staticmethod
    async def inject_hardware(page: Page, config: dict):
        """Spoof CPU core count and device memory."""
        hardware = config["hardware"]
        await page.add_init_script(f"""
            Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {hardware['hardwareConcurrency']}}});
            Object.defineProperty(navigator, 'deviceMemory', {{get: () => {hardware['deviceMemory']}}});
        """)

    @staticmethod
    async def inject_webrtc(page: Page, local_ip_set: list):
        """Replace local IPs in WebRTC SDP and block enumerateDevices."""
        await page.add_init_script(f"""
        (() => {{
            const getLocalIPs = (callback) => {{
                const ips = ["{local_ip_set[0]}", "{local_ip_set[1]}", "{local_ip_set[2]}"];
                callback(ips);
            }};

            class FakeRTCPeerConnection extends RTCPeerConnection {{
                constructor(config) {{
                    super(config);
                }}

                createOffer(...args) {{
                    return super.createOffer(...args).then((offer) => {{
                        offer.sdp = offer.sdp.replace(
                            /([0-9]{{1,3}}\\.[0-9]{{1,3}}\\.[0-9]{{1,3}}\\.[0-9]{{1,3}})/g,
                            "{local_ip_set[0]}"
                        );
                        return offer;
                    }});
                }}
            }}

            window.RTCPeerConnection = FakeRTCPeerConnection;
            navigator.mediaDevices.enumerateDevices = async () => {{ return []; }};
        }})();
        """)

    @staticmethod
    async def inject_webgl(page: Page, webgl: dict):
        """Spoof WebGL vendor and renderer strings."""
        await page.add_init_script(f"""
        (() => {{
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                if (parameter === 37445) return "{webgl['vendor']}";   // UNMASKED_VENDOR_WEBGL
                if (parameter === 37446) return "{webgl['renderer']}"; // UNMASKED_RENDERER_WEBGL
                return getParameter.call(this, parameter);
            }};
        }})();
        """)

    @staticmethod
    async def inject_canvas(page: Page, canvas: dict):
        """Add noise to Canvas fingerprint via toDataURL and getImageData."""
        await page.add_init_script(f"""
        (() => {{
            const toDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {{
                return toDataURL.call(this, "{canvas['image_type']}");
            }};

            const getImageData = CanvasRenderingContext2D.prototype.getImageData;
            CanvasRenderingContext2D.prototype.getImageData = function(x, y, width, height) {{
                let imageData = getImageData.call(this, x, y, width, height);
                for (let i = 0; i < imageData.data.length; i += 4) {{
                    imageData.data[i]   ^= {canvas['red']};
                    imageData.data[i+1] ^= {canvas['green']};
                    imageData.data[i+2] ^= {canvas['blue']};
                }}
                return imageData;
            }};
        }})();
        """)

    @staticmethod
    async def inject_audio(page: Page, audio: dict):
        """Add noise to AudioBuffer channel data to mask audio fingerprint."""
        await page.add_init_script(f"""
        (() => {{
            const originalGetChannelData = AudioBuffer.prototype.getChannelData;
            AudioBuffer.prototype.getChannelData = function() {{
                const results = originalGetChannelData.apply(this, arguments);
                for (let i = 0; i < results.length; i++) {{
                    results[i] = results[i] + (Math.random() * {audio['noiseIntensity']});
                }}
                return results;
            }};
        }})();
        """)

    @staticmethod
    async def inject_battery(page: Page, battery: dict):
        """Emulate Battery API with configured state values."""
        charging_time    = 'Infinity' if battery['chargingTime']    is None else battery['chargingTime']
        discharging_time = 'Infinity' if battery['dischargingTime'] is None else battery['dischargingTime']
        await page.add_init_script(f"""
        (() => {{
            navigator.getBattery = function() {{
                return new Promise((resolve) => {{
                    resolve({{
                        charging: {str(battery['charging']).lower()},
                        chargingTime: {charging_time},
                        dischargingTime: {discharging_time},
                        level: {battery['level']}
                    }});
                }});
            }};
        }})();
        """)

    @staticmethod
    async def inject_usb(page: Page, usb: dict):
        """Optionally disable USB and HID APIs."""
        await page.add_init_script(f"""
        (() => {{
            {f"navigator.usb = undefined;" if usb['disableUSB'] else ""}
            {f"navigator.hid = undefined;" if usb['disableHID'] else ""}
        }})();
        """)

    @staticmethod
    async def inject_plugins(page: Page, plugins: dict):
        """Spoof navigator.plugins and navigator.mimeTypes."""
        await page.add_init_script(f"""
        (() => {{
            Object.defineProperty(navigator, 'plugins', {{
                get: () => {plugins['plugins']}
            }});
            Object.defineProperty(navigator, 'mimeTypes', {{
                get: () => {plugins['mimeTypes']}
            }});
        }})();
        """)

    @staticmethod
    async def inject_platform(page: Page, system: str):
        """Spoof navigator.platform."""
        await page.add_init_script(f"""
        (() => {{
            Object.defineProperty(navigator, 'platform', {{ get: () => '{system}' }});
        }})();
        """)

    @staticmethod
    async def inject_language(page: Page, language: str):
        """Spoof navigator.language and navigator.languages."""
        primary_language = language.split(",")[0]
        languages_list   = [lang.split(";")[0] for lang in language.split(",")]
        await page.add_init_script(f"""
        (() => {{
            Object.defineProperty(navigator, 'language',  {{ get: () => '{primary_language}' }});
            Object.defineProperty(navigator, 'languages', {{ get: () => {languages_list} }});
        }})();
        """)

    @staticmethod
    async def inject_canvas_2d(page: Page, canvas_2d: dict):
        """Mask Canvas 2D fingerprint: getImageData, toDataURL, fillText."""
        await page.add_init_script(f"""
        (() => {{
            const getContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(type, ...args) {{
                if (type === "2d") {{
                    const context = getContext.apply(this, [type, ...args]);

                    const originalGetImageData = context.getImageData;
                    context.getImageData = function(x, y, width, height) {{
                        let imageData = originalGetImageData.call(this, x, y, width, height);
                        for (let i = 0; i < imageData.data.length; i += 4) {{
                            imageData.data[i]     ^= {canvas_2d.get('red',     1)};
                            imageData.data[i + 1] ^= {canvas_2d.get('green',   2)};
                            imageData.data[i + 2] ^= {canvas_2d.get('blue',    3)};
                        }}
                        return imageData;
                    }};

                    const originalToDataURL = context.canvas.toDataURL;
                    context.canvas.toDataURL = function(type) {{
                        console.log("Canvas fingerprinting attempt detected!");
                        return originalToDataURL.call(this, "image/jpeg", {canvas_2d.get('quality', 0.92)});
                    }};

                    const originalFillText = context.fillText;
                    context.fillText = function(text, x, y) {{
                        context.font = "{canvas_2d.get('font', '12px Arial')}";
                        return originalFillText.call(this, text, x, y);
                    }};

                    return context;
                }}
                return getContext.apply(this, arguments);
            }};

            if (typeof OffscreenCanvas !== "undefined") {{
                const getContextOffscreen = OffscreenCanvas.prototype.getContext;
                OffscreenCanvas.prototype.getContext = function(type, ...args) {{
                    if (type === "2d") {{
                        return null;
                    }}
                    return getContextOffscreen.apply(this, arguments);
                }};
            }}
        }})();
        """)

    @staticmethod
    async def inject_fonts(page: Page, fonts: list):
        """Override computed font-family to mask the system font list."""
        await page.add_init_script(f"""
        (() => {{
            const fakeFonts = {fonts};

            const originalGetComputedStyle = window.getComputedStyle;
            window.getComputedStyle = function(element, pseudoElement) {{
                const computedStyle = originalGetComputedStyle.apply(this, [element, pseudoElement]);
                return new Proxy(computedStyle, {{
                    get(target, prop) {{
                        if (prop === 'fontFamily') return fakeFonts.join(', ');
                        const val = target[prop];
                        return typeof val === 'function' ? val.bind(target) : val;
                    }}
                }});
            }};
        }})();
        """)

    @classmethod
    async def inject_all(
        cls,
        page: Page,
        config: dict,
        system: str,
        language: str,
        profile: ProfileConfig = STEALTH,
    ):
        """Apply masking scripts selected by the given profile."""
        logger.debug(f"Injecting scripts (profile: {profile})")
        if profile.base_masking: await cls.inject_base_masking(page)
        if profile.hardware:     await cls.inject_hardware(page, config)
        if profile.webrtc:       await cls.inject_webrtc(page, config["local_ip_set"])
        if profile.webgl:        await cls.inject_webgl(page, config["webgl"])
        if profile.canvas:       await cls.inject_canvas(page, config["canvas"])
        if profile.audio:        await cls.inject_audio(page, config["audio"])
        if profile.battery:      await cls.inject_battery(page, config["battery"])
        if profile.usb:          await cls.inject_usb(page, config["usb"])
        if profile.plugins:      await cls.inject_plugins(page, config["plugins"])
        if profile.platform:     await cls.inject_platform(page, system)
        if profile.language:     await cls.inject_language(page, language)
        if profile.canvas_2d:    await cls.inject_canvas_2d(page, config["canvas_2d"])
        if profile.fonts:        await cls.inject_fonts(page, config["fonts"])
        logger.debug("Scripts injected")


# ===========================================================================
# BrowserLauncher
# ===========================================================================

class BrowserLauncher:
    """
    Launches a browser with fingerprint masking and proxy support.

    Combines ProxyManager, FingerprintGenerator and ScriptInjector into
    a single lifecycle: start() → (use) → close().
    """

    LAUNCH_ARGS = [
        "--disable-webrtc-encryption",
        "--disable-blink-features=AutomationControlled",
        "--disable-automation",
        "--disable-blink-features",
        "--no-sandbox",
        "--disable-web-security",
        "--disable-features=IsolateOrigins,site-per-process,SitePerProcess",
        "--disable-dev-shm-usage",
        "--disable-accelerated-2d-canvas",
        "--hide-scrollbars",
        "--disable-gpu",
        "--metrics-recording-only",
        "--disable-setuid-sandbox",
        "--no-zygote",
    ]

    def __init__(self, country_config_file: str, proxy_manager: ProxyManager):
        self._country_config_file = country_config_file
        self._proxy_manager       = proxy_manager
        self._playwright          = None
        self._browser: Browser | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def start(
        self,
        country: str,
        profile: ProfileConfig = STEALTH,
    ) -> tuple[Browser, dict] | tuple[None, None]:
        """
        Launch a browser for the given country code.
        Returns (browser, country_config) or (None, None) on failure.
        """
        try:
            logger.info(f"Starting browser for country: {country}")

            country_config = self._build_country_config(country)
            if not country_config:
                logger.error("Failed to build country configuration")
                return None, None

            system      = country_config["system"]
            user_agent  = country_config["user_agent"]
            screen_size = country_config["screen_size"]
            language    = country_config["language"]
            proxy_info  = country_config["proxy_info"]
            timezone    = proxy_info["timezone"]
            latitude    = proxy_info["location"]["latitude"]
            longitude   = proxy_info["location"]["longitude"]

            browser_type = self._detect_browser_type(user_agent)
            logger.debug(f"Detected browser type: {browser_type}")

            fingerprint = FingerprintGenerator(system, browser_type).generate()
            logger.debug("Fingerprint configuration created")

            if self._playwright is None:
                logger.debug("Initializing Playwright...")
                self._playwright = await async_playwright().start()

            args = self.LAUNCH_ARGS + [f"--window-size={screen_size[0]},{screen_size[1]}"]

            logger.debug("Launching browser...")
            self._browser = await self._playwright.chromium.launch(
                headless=False,
                proxy=proxy_info["credentials"],
                args=args,
            )

            logger.debug("Creating browser context...")
            context = await self._browser.new_context(
                user_agent=user_agent,
                viewport={"width": screen_size[0], "height": screen_size[1]},
                timezone_id=timezone,
                locale=language,
                geolocation={"latitude": latitude, "longitude": longitude},
                permissions=["geolocation"],
                color_scheme="light",
                reduced_motion="no-preference",
                forced_colors="none",
                accept_downloads=True,
                ignore_https_errors=True,
                has_touch=False,
                is_mobile=False,
                device_scale_factor=1,
                strict_selectors=False,
            )

            logger.debug("Creating new page...")
            page = await context.new_page()

            await ScriptInjector.inject_all(page, fingerprint, system, language, profile)

            logger.info("Browser started successfully")
            return self._browser, country_config

        except Exception as e:
            logger.exception(e, "Error starting browser")
            return None, None

    async def close(self):
        """Close the current browser if one is running."""
        try:
            if self._browser:
                logger.info("Closing browser...")
                await self._browser.close()
                self._browser = None
                logger.info("Browser closed successfully")
        except Exception as e:
            logger.exception(e, "Error closing browser")

    def load_available_countries(self) -> list[str]:
        """Return the list of country codes present in the config file."""
        try:
            with open(self._country_config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return list(data.keys())
        except Exception as e:
            logger.exception(e, "Error loading available countries")
            return []

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_country_config(self, country: str) -> dict | None:
        """Assemble a full launch configuration for the given country."""
        try:
            logger.info(f"Getting configuration for country: {country}")

            proxy_info = self._proxy_manager.find_proxy(country)
            if not proxy_info:
                logger.error("Failed to get proxy info")
                return None

            with open(self._country_config_file, "r", encoding="utf-8") as f:
                ua_data = json.load(f)

            if country not in ua_data:
                logger.error(f"No user agent data found for country: {country}")
                return None

            system = random.choice(["Win64", "MacIntel", "Linux x86_64"])
            logger.debug(f"Selected system: {system}")

            ua_kit = random.choice(ua_data[country][system])
            logger.debug(f"Selected user agent kit: {ua_kit}")

            config = {
                "proxy_info": proxy_info,
                "system":     system,
                "user_agent": ua_kit["user_agent"],
                "screen_size": ua_kit["screen_size"],
                "language":   ua_kit["language"],
            }

            logger.info("Country configuration created successfully")
            return config

        except Exception as e:
            logger.exception(e, "Error building country config")
            return None

    @staticmethod
    def _detect_browser_type(user_agent: str) -> str:
        """Detect browser type from User-Agent string."""
        if "Edg" in user_agent or "Edge" in user_agent:
            return "Edge"
        if "Chrome" in user_agent:
            return "Chrome"
        if "Firefox" in user_agent:
            return "Firefox"
        if "Safari" in user_agent:
            return "Safari"
        return "Chrome"
