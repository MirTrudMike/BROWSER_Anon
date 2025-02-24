from playwright.async_api import async_playwright
import asyncio
import time
import json
import os
import requests
import random
from browser_configuration import make_config


def read_country_config_file():
    with open(f'{os.path.abspath('country_config.json')}', 'r', encoding='utf-8') as file:
        return json.load(file)


def read_used_ips():
    with open(f'{os.path.abspath('used_ips.json')}') as file:
        used_ips = json.load(file)
    return used_ips


def write_used_ip(ip):
    with open(f'{os.path.abspath('used_ips.json')}') as file:
        used_ips = json.load(file)
    used_ips.append(ip)
    with open(f'{os.path.abspath('used_ips.json')}', mode='w') as file:
        json.dump(used_ips, file, indent=4)


def read_proxy_credentials():
    with open(f"{os.path.abspath('proxies.json')}") as file:
        proxies = json.load(file)
    return proxies


def get_proxy_info(server, port, username, password):
    proxies = {
        'http': f'http://{username}:{password}@{server}:{port}',
        'https': f'http://{username}:{password}@{server}:{port}'}

    response = requests.get('http://ip-api.com/json/', proxies=proxies).json()
    info = {
        'ip': response['query'],
        'country': response['country'],
        'countryCode': response['countryCode'],
        'city': response['city'],
        'timezone': response['timezone'],
        'location': {'latitude': response['lat'], 'longitude': response['lon']}
    }

    return info


def find_proxy(country):
    proxy_server = "pool.proxy.market"
    proxy_port = 10000
    proxy_password = 'RNW78Fm5'
    proxy_username = read_proxy_credentials()[country]['username']

    used_ips = read_used_ips()

    for i in range(1000):
        try:
            proxy_port += i
            proxy_info = get_proxy_info(proxy_server, proxy_port, proxy_username, proxy_password)
            ip = proxy_info['ip']

            if not ip in used_ips:
                write_used_ip(ip)

                proxy_info.update({'credentials':
                                       {'server': f"http://{proxy_server}:{proxy_port}",
                                        'username': proxy_username,
                                        'password': proxy_password}})
                return proxy_info

            time.sleep(1)

        except Exception as e:
            continue

    return False


def get_country_config(country):
    config = {}
    proxy_info = find_proxy(country)

    user_agents_data = read_country_config_file()
    random_systems = random.choice(['Win64', 'MacIntel', 'Linux x86_64'])
    random_user_agent_kit = random.choice(user_agents_data[country][random_systems])

    config.update({'proxy_info': proxy_info,
                   'system': random_systems,
                   'user_agent': random_user_agent_kit['user_agent'],
                   'screen_size': random_user_agent_kit['screen_size'],
                   'language': random_user_agent_kit['language']})
    return config

playwright = None
async def start_browser(country):
    country_based_config = get_country_config(country)
    print(country_based_config)

    proxy_info = country_based_config['proxy_info']

    # Стандартные параметры браузера
    system = country_based_config['system']
    user_agent = country_based_config['user_agent']
    screen_size = country_based_config['screen_size']
    timezone = country_based_config['proxy_info']['timezone']
    language = country_based_config['language']
    latitude = country_based_config['proxy_info']['location']['latitude']
    longitude = country_based_config['proxy_info']['location']['longitude']

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

    config = make_config(system=system, browser=browser_type)

    global playwright
    if playwright is None:  # Запускаем Playwright только один раз
        playwright = await async_playwright().start()

    browser = await playwright.chromium.launch(
            headless=False,
            proxy=proxy_info['credentials'],
            args=[
                "--disable-webrtc-encryption"
            ]
        )

    context = await browser.new_context(
            user_agent=user_agent,
            viewport={"width": (screen_size[0]), "height": screen_size[1]},
            timezone_id=timezone,
            locale=language,
            geolocation={"latitude": latitude, "longitude": longitude},  # Нью-Йорк
            permissions=["geolocation"],
        )

        # Создание новой страницы и добавление скриптов для подмены характеристик
    page = await context.new_page()
    await page.add_init_script(f"""
            // Подмена свойств браузера для маскировки
            Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
            Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {config['hardware']['hardwareConcurrency']}}});
            Object.defineProperty(navigator, 'deviceMemory', {{get: () => {config['hardware']['deviceMemory']}}});
        """)

    # # Подмена WebRTC, чтобы скрыть локальные IP
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

        # Подмена WebGL для блокировки идентификации устройства по рендеру
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

    # Подмена Canvas для предотвращения фингерпринтинга
    canvas = config['canvas']
    await page.add_init_script(f"""
    (() => {{
        // Подмена toDataURL
        const toDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {{
            return toDataURL.call(this, "{canvas['image_type']}"); // Подмена типа изображения
        }};
    
        // Подмена getImageData
        const getImageData = CanvasRenderingContext2D.prototype.getImageData;
        CanvasRenderingContext2D.prototype.getImageData = function(x, y, width, height) {{
            let imageData = getImageData.call(this, x, y, width, height);
            for (let i = 0; i < imageData.data.length; i += 4) {{
                imageData.data[i] ^= {canvas['red']};   // Изменение красного канала
                imageData.data[i+1] ^= {canvas['green']}; // Изменение зелёного канала
                imageData.data[i+2] ^= {canvas['blue']}; // Изменение синего канала
            }}
            return imageData;
        }};
    }})();
    """)
    #
    # Изменения для предотвращения фингерпринтинга по аудио
    audio = config['audio']
    await page.add_init_script(f"""
    (() => {{
        const originalGetChannelData = AudioBuffer.prototype.getChannelData;
        AudioBuffer.prototype.getChannelData = function() {{
            const results = originalGetChannelData.apply(this, arguments);
            for (let i = 0; i < results.length; i++) {{
                results[i] = results[i] + (Math.random() * {audio['noiseIntensity']}); // Добавление шума
            }}
            return results;
        }};
    }})();
    """)
    #
    # # Подмена данных батареи для обхода фингерпринтинга
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
    #
    # Блокировка USB и HID устройства
    usb = config['usb']
    await page.add_init_script( f"""
    (() => {{
        {f"navigator.usb = undefined;" if usb['disableUSB'] else ""}
        {f"navigator.hid = undefined;" if usb['disableHID'] else ""}
    }})();
    """)

    # Блокировка информации о плагинах
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

    # Маскировка платформы
    await page.add_init_script(f"""
        (() => {{
            Object.defineProperty(navigator, 'platform', {{ get: () => '{system}' }});
        }})();
    """)

    # Маскировка языка браузера
    primary_language = language.split(",")[0]
    languages_list = [lang.split(";")[0] for lang in language.split(",")]
    await page.add_init_script(f"""
(() => {{
    Object.defineProperty(navigator, 'language', {{ get: () => '{primary_language}' }});
    Object.defineProperty(navigator, 'languages', {{ get: () => {languages_list} }});
}})();
""")

    # Переопределение методов Canvas для защиты от Canvas Fingerprinting
    canvas_2 = config['canvas_2']
    await page.add_init_script(f"""
    (() => {{
        const getContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type, ...args) {{
            if (type === "2d") {{
                const context = getContext.apply(this, [type, ...args]);
    
                const originalGetImageData = context.getImageData;
                context.getImageData = function(x, y, width, height) {{
                    let imageData = originalGetImageData.call(this, x, y, width, height);
                    // Подмена цветов (красный, зеленый, синий)
                    for (let i = 0; i < imageData.data.length; i += 4) {{
                        imageData.data[i] ^= {canvas_2['red']};   // Красный канал
                        imageData.data[i + 1] ^= {canvas_2['green']}; // Зеленый канал
                        imageData.data[i + 2] ^= {canvas_2['blue']}; // Синий канал
                    }}
                    return imageData;
                }};
    
                const originalToDataURL = context.canvas.toDataURL;
                context.canvas.toDataURL = function(type) {{
                    console.log("Canvas fingerprinting attempt detected!");
                    // Применяем низкое качество изображения, чтобы скрыть детали
                    return originalToDataURL.call(this, "image/jpeg", {canvas_2['image_quality']}); // Уменьшаем качество JPEG
                }};
    
                // Подмена шрифта для текста на Canvas (если используется)
                const originalFillText = context.fillText;
                context.fillText = function(text, x, y) {{
                    context.font = "{canvas_2['font']}"; // Применяем фиктивный шрифт
                    return originalFillText.call(this, text, x, y);
                }};
    
                return context;
            }}
            return getContext.apply(this, arguments);
        }};
    
        // Подмена для OffscreenCanvas, если поддерживается
        if (typeof OffscreenCanvas !== "undefined") {{
            const getContextOffscreen = OffscreenCanvas.prototype.getContext;
            OffscreenCanvas.prototype.getContext = function(type, ...args) {{
                if (type === "2d") {{
                    return null; // Блокируем попытки Canvas Fingerprinting
                }}
                return getContextOffscreen.apply(this, arguments);
            }};
        }}
    }})();
    """)


    fonts = config['fonts']
    await page.add_init_script( f"""
    (() => {{
        // Создаём фиктивные шрифты для подмены
        const fakeFonts = {fonts};
    
        // Переопределяем метод `getComputedStyle` для подмены шрифтов
        const originalGetComputedStyle = window.getComputedStyle;
        window.getComputedStyle = function(element, pseudoElement) {{
            const computedStyle = originalGetComputedStyle.apply(this, [element, pseudoElement]);
    
            // Проверяем стиль font-family
            if (computedStyle.fontFamily) {{
                // Заменяем на фиктивный шрифт
                computedStyle.fontFamily = fakeFonts.join(', ');
            }}
    
            return computedStyle;
        }};
    
        // Переопределяем `document.fonts` для предотвращения реальной проверки шрифтов
        const originalAdd = Document.prototype.fonts.add;
        Document.prototype.fonts.add = function(font) {{
            // Можно также блокировать или подменить добавление новых шрифтов
            console.log(`Font added: ${{font.family}}`);
            // Не добавляем реальный шрифт, только фиктивный
            originalAdd.call(this, font);
        }};
    
        // Блокируем или подменяем запросы на установку шрифтов
        const originalMatch = FontFace.prototype.load;
        FontFace.prototype.load = function() {{
            // Подменяем шрифты, которые загружаются
            const fakeFont = new FontFace('FakeFont', 'url(fake-font-url)');
            return fakeFont.load();
        }};
    
        console.log("Font fingerprinting blocked!");
    }})();
    """)

    # Переход на сайт для тестирования IP
    await page.goto("https://browserleaks.com/", wait_until="networkidle")

    # while True:
    #     close = input('\r\rEXIT to close browser: ')
    #     if close.strip() == 'exit':
    #         await browser.close()
    #         break
    #     else:
    #         continue
    return browser, country_based_config




# asyncio.run(start_browser('il'))
