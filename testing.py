from playwright.async_api import async_playwright
import asyncio
import time
import json
import os
import requests
import random
from browser_configuration import make_config
from logger_config import log_info, log_debug, log_exception, log_warning, log_error


def read_country_config_file():
    try:
        log_debug("Reading country configuration file...")
        file_path = os.path.abspath('country_config.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
        log_info("Country configuration loaded successfully")
        return config
    except FileNotFoundError:
        log_error(f"Country configuration file not found at {file_path}")
        raise
    except json.JSONDecodeError as e:
        log_exception(e, "Error parsing country configuration file")
        raise
    except Exception as e:
        log_exception(e, "Unexpected error reading country configuration")
        raise


def read_used_ips():
    try:
        log_debug("Reading used IPs file...")
        file_path = os.path.abspath('used_ips.json')
        with open(file_path) as file:
            used_ips = json.load(file)
        log_debug(f"Loaded {len(used_ips)} used IPs")
        return used_ips
    except FileNotFoundError:
        log_warning("Used IPs file not found, creating new one")
        with open(file_path, 'w') as file:
            json.dump([], file)
        return []
    except Exception as e:
        log_exception(e, "Error reading used IPs file")
        raise


def write_used_ip(ip):
    try:
        log_debug(f"Writing new used IP: {ip}")
        file_path = os.path.abspath('used_ips.json')
        with open(file_path) as file:
            used_ips = json.load(file)
        used_ips.append(ip)
        with open(file_path, mode='w') as file:
            json.dump(used_ips, file, indent=4)
        log_debug("IP written successfully")
    except Exception as e:
        log_exception(e, "Error writing used IP")
        raise


def read_proxy_credentials():
    try:
        log_debug("Reading proxy credentials...")
        file_path = os.path.abspath('proxies.json')
        with open(file_path) as file:
            proxies = json.load(file)
        log_info("Proxy credentials loaded successfully")
        return proxies
    except FileNotFoundError:
        log_error(f"Proxy credentials file not found at {file_path}")
        raise
    except json.JSONDecodeError as e:
        log_exception(e, "Error parsing proxy credentials file")
        raise
    except Exception as e:
        log_exception(e, "Unexpected error reading proxy credentials")
        raise


def get_proxy_info(server, port, username, password):
    try:
        log_info(f"Getting proxy info for server: {server}:{port}")
        proxies = {
            'http': f'http://{username}:{password}@{server}:{port}',
            'https': f'http://{username}:{password}@{server}:{port}'
        }

        log_debug("Making request to ip-api.com...")
        response = requests.get('http://ip-api.com/json/', proxies=proxies)
        response.raise_for_status()  # Проверка на ошибки HTTP
        response_data = response.json()

        info = {
            'ip': response_data['query'],
            'country': response_data['country'],
            'countryCode': response_data['countryCode'],
            'city': response_data['city'],
            'timezone': response_data['timezone'],
            'location': {'latitude': response_data['lat'], 'longitude': response_data['lon']}
        }

        log_info(f"Successfully got proxy info for IP: {info['ip']}")
        return info

    except requests.RequestException as e:
        log_exception(e, f"Error making request to ip-api.com with proxy {server}:{port}")
        return False
    except KeyError as e:
        log_exception(e, "Missing required field in ip-api.com response")
        return False
    except Exception as e:
        log_exception(e, "Unexpected error getting proxy info")
        return False


def find_proxy(country):
    try:
        log_info(f"Finding proxy for country: {country}")
        proxy_server = "pool.proxy.market"
        proxy_port = 10000
        proxy_password = 'RNW78Fm5'
        
        proxy_credentials = read_proxy_credentials()
        if country not in proxy_credentials:
            log_error(f"No proxy credentials found for country: {country}")
            return False
            
        proxy_username = proxy_credentials[country]['username']
        used_ips = read_used_ips()

        for i in range(1000):
            try:
                proxy_port += i
                log_debug(f"Trying proxy port: {proxy_port}")
                
                proxy_info = get_proxy_info(proxy_server, proxy_port, proxy_username, proxy_password)
                if not proxy_info:
                    continue

                ip = proxy_info['ip']
                if ip not in used_ips:
                    write_used_ip(ip)
                    proxy_info.update({
                        'credentials': {
                            'server': f"http://{proxy_server}:{proxy_port}",
                            'username': proxy_username,
                            'password': proxy_password
                        }
                    })
                    log_info(f"Found suitable proxy with IP: {ip}")
                    return proxy_info

                log_debug(f"IP {ip} already used, trying next port")
                time.sleep(1)

            except Exception as e:
                log_exception(e, f"Error trying proxy port {proxy_port}")
                continue

        log_error(f"Failed to find suitable proxy for country {country} after 1000 attempts")
        return False

    except Exception as e:
        log_exception(e, f"Unexpected error in find_proxy for country {country}")
        return False


def get_country_config(country):
    try:
        log_info(f"Getting configuration for country: {country}")
        config = {}
        
        # Получаем информацию о прокси
        proxy_info = find_proxy(country)
        if not proxy_info:
            log_error("Failed to get proxy info")
            return None

        # Загружаем конфигурацию User-Agent
        user_agents_data = read_country_config_file()
        if country not in user_agents_data:
            log_error(f"No user agent data found for country: {country}")
            return None

        # Выбираем случайную систему и User-Agent
        random_systems = random.choice(['Win64', 'MacIntel', 'Linux x86_64'])
        log_debug(f"Selected system: {random_systems}")
        
        random_user_agent_kit = random.choice(user_agents_data[country][random_systems])
        log_debug(f"Selected user agent kit: {random_user_agent_kit}")

        config.update({
            'proxy_info': proxy_info,
            'system': random_systems,
            'user_agent': random_user_agent_kit['user_agent'],
            'screen_size': random_user_agent_kit['screen_size'],
            'language': random_user_agent_kit['language']
        })

        log_info("Country configuration created successfully")
        return config

    except Exception as e:
        log_exception(e, "Error creating country configuration")
        return None

playwright = None
async def start_browser(country):
    try:
        log_info(f"Starting browser for country: {country}")
        
        # Получаем конфигурацию для страны
        country_based_config = get_country_config(country)
        if not country_based_config:
            log_error("Failed to get country configuration")
            return None
            
        log_debug(f"Country configuration: {country_based_config}")
        proxy_info = country_based_config['proxy_info']

        # Стандартные параметры браузера
        system = country_based_config['system']
        user_agent = country_based_config['user_agent']
        screen_size = country_based_config['screen_size']
        timezone = country_based_config['proxy_info']['timezone']
        language = country_based_config['language']
        latitude = country_based_config['proxy_info']['location']['latitude']
        longitude = country_based_config['proxy_info']['location']['longitude']

        # Определяем тип браузера
        if "Chrome" in user_agent:
            browser_type = "Chrome"
        elif "Edg" in user_agent or "Edge" in user_agent:
            browser_type = "Edge"
        elif "Firefox" in user_agent:
            browser_type = "Firefox"
        elif "Safari" in user_agent:
            browser_type = "Safari"
        else:
            browser_type = "Chrome"

        log_debug(f"Detected browser type: {browser_type}")
        
        # Создаем конфигурацию браузера
        config = make_config(system=system, browser=browser_type)
        log_debug("Browser configuration created")

        # Инициализация Playwright
        global playwright
        if playwright is None:
            log_debug("Initializing Playwright...")
            playwright = await async_playwright().start()

        # Запуск браузера
        log_debug("Launching browser...")
        browser = await playwright.chromium.launch(
            headless=False,
            proxy=proxy_info['credentials'],
            args=[
                "--disable-webrtc-encryption",
                "--disable-blink-features=AutomationControlled",
                "--disable-automation",
                "--disable-blink-features",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process,SitePerProcess",
                f"--window-size={screen_size[0]},{screen_size[1]}",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--hide-scrollbars",
                "--disable-gpu",
                "--metrics-recording-only",
                "--disable-setuid-sandbox",
                "--no-zygote"
            ]
        )

        # Создание контекста
        log_debug("Creating browser context...")
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={"width": (screen_size[0]), "height": screen_size[1]},
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
            strict_selectors=False
        )

        # Создание новой страницы
        log_debug("Creating new page...")
        page = await context.new_page()
        
        # Добавление скриптов для маскировки
        log_debug("Adding masking scripts...")
        await page.add_init_script("""
            // Маскировка Playwright
            delete window.playwright;
            
            // Маскировка webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
                configurable: true
            });
            
            // Маскировка Chrome
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
            
            // Маскировка Permissions API
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({state: Notification.permission}) :
                    originalQuery(parameters)
            );
            
            // Добавление "живых" свойств браузера
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
            
            // Эмуляция реальных размеров окна
            Object.defineProperty(window, 'outerWidth', {
                get: () => window.innerWidth
            });
            Object.defineProperty(window, 'outerHeight', {
                get: () => window.innerHeight
            });
            
            // Добавление стандартных функций
            window.chrome = {
                runtime: {}
            };
            
            // Маскировка отпечатка WebGL
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                // Подмена UNMASKED_VENDOR_WEBGL
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                // Подмена UNMASKED_RENDERER_WEBGL
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter.apply(this, arguments);
            };
        """)
        
        log_debug("Adding hardware configuration scripts...")
        await page.add_init_script(f"""
            Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {config['hardware']['hardwareConcurrency']}}});
            Object.defineProperty(navigator, 'deviceMemory', {{get: () => {config['hardware']['deviceMemory']}}});
        """)

        log_debug("Adding WebRTC configuration...")
        local_ip_set = config['local_ip_set']
        await page.add_init_script(f"""
        (() => {{
            const getLocalIPs = (callback) => {{
                const ips = ["{local_ip_set[0]}", "{local_ip_set[1]}", "{local_ip_set[2]}"]; // Фейковые IP
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
            navigator.mediaDevices.enumerateDevices = async () => {{ return []; }}; // Блокируем enumerateDevices
        }})();
        """)

        log_debug("Adding WebGL configuration...")
        webgl = config['webgl']
        await page.add_init_script(f"""
        (() => {{
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                if (parameter === 37445) return "{webgl['vendor']}";  // UNMASKED_VENDOR_WEBGL
                if (parameter === 37446) return "{webgl['renderer']}"; // UNMASKED_RENDERER_WEBGL
                return getParameter.call(this, parameter);
            }};
        }})();
        """)

        log_debug("Adding Canvas configuration...")
        canvas = config['canvas']
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
                    imageData.data[i] ^= {canvas['red']};
                    imageData.data[i+1] ^= {canvas['green']};
                    imageData.data[i+2] ^= {canvas['blue']};
                }}
                return imageData;
            }};
        }})();
        """)

        log_debug("Adding Audio configuration...")
        audio = config['audio']
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

        log_debug("Adding Battery configuration...")
        battery = config['battery']
        await page.add_init_script(f"""
        (() => {{
            navigator.getBattery = function() {{
                return new Promise((resolve) => {{
                    resolve({{
                        charging: {str(battery['charging']).lower()},
                        chargingTime: {battery['chargingTime']},
                        dischargingTime: {battery['dischargingTime']},
                        level: {battery['level']}
                    }});
                }});
            }};
        }})();
        """)

        log_debug("Adding USB configuration...")
        usb = config['usb']
        await page.add_init_script(f"""
        (() => {{
            {f"navigator.usb = undefined;" if usb['disableUSB'] else ""}
            {f"navigator.hid = undefined;" if usb['disableHID'] else ""}
        }})();
        """)

        log_debug("Adding Plugins configuration...")
        plugins = config['plugins']
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

        log_debug("Adding Platform configuration...")
        await page.add_init_script(f"""
        (() => {{
            Object.defineProperty(navigator, 'platform', {{ get: () => '{system}' }});
        }})();
        """)

        log_debug("Adding Language configuration...")
        primary_language = language.split(",")[0]
        languages_list = [lang.split(";")[0] for lang in language.split(",")]
        await page.add_init_script(f"""
        (() => {{
            Object.defineProperty(navigator, 'language', {{ get: () => '{primary_language}' }});
            Object.defineProperty(navigator, 'languages', {{ get: () => {languages_list} }});
        }})();
        """)

        log_debug("Adding Canvas 2D configuration...")
        canvas_2 = config['canvas_2d']
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
                            imageData.data[i] ^= {canvas_2.get('red', 1)};
                            imageData.data[i + 1] ^= {canvas_2.get('green', 2)};
                            imageData.data[i + 2] ^= {canvas_2.get('blue', 3)};
                        }}
                        return imageData;
                    }};
        
                    const originalToDataURL = context.canvas.toDataURL;
                    context.canvas.toDataURL = function(type) {{
                        console.log("Canvas fingerprinting attempt detected!");
                        return originalToDataURL.call(this, "image/jpeg", {canvas_2.get('quality', 0.92)});
                    }};
        
                    const originalFillText = context.fillText;
                    context.fillText = function(text, x, y) {{
                        context.font = "{canvas_2.get('font', '12px Arial')}";
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

        log_debug("Adding Fonts configuration...")
        fonts = config['fonts']
        await page.add_init_script(f"""
        (() => {{
            const fakeFonts = {fonts};
        
            const originalGetComputedStyle = window.getComputedStyle;
            window.getComputedStyle = function(element, pseudoElement) {{
                const computedStyle = originalGetComputedStyle.apply(this, [element, pseudoElement]);
        
                if (computedStyle.fontFamily) {{
                    computedStyle.fontFamily = fakeFonts.join(', ');
                }}
        
                return computedStyle;
            }};
        
            const originalAdd = Document.prototype.fonts.add;
            Document.prototype.fonts.add = function(font) {{
                console.log(`Font added: ${{font.family}}`);
                originalAdd.call(this, font);
            }};
        
            const originalMatch = FontFace.prototype.load;
            FontFace.prototype.load = function() {{
                const fakeFont = new FontFace('FakeFont', 'url(fake-font-url)');
                return fakeFont.load();
            }};
        
            console.log("Font fingerprinting blocked!");
        }})();
        """)

        log_info("Browser started successfully")
        return browser, country_based_config

    except Exception as e:
        log_exception(e, "Error starting browser")
        return None, None




# asyncio.run(start_browser('il'))
