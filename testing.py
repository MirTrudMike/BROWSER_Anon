from playwright.async_api import async_playwright
import asyncio
import time
import json
import os
import requests
import random


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
    random_systems = random.choice(['windows', 'mac', 'linux'])
    random_user_agent_kit = random.choice(user_agents_data[country][random_systems])

    config.update({'proxy_info': proxy_info,
                   'user_agent': random_user_agent_kit['user_agent'],
                   'screen_size': random_user_agent_kit['screen_size'],
                   'language': random_user_agent_kit['language']})
    return config



async def start_browser(country):
    country_based_config = get_country_config(country)
    print(country_based_config)

    proxy_info = country_based_config['proxy_info']

    # Стандартные параметры браузера
    user_agent = country_based_config['user_agent']
    screen_size = country_based_config['screen_size']
    timezone = country_based_config['proxy_info']['timezone']
    language = country_based_config['language']
    latitude = country_based_config['proxy_info']['location']['latitude']
    longitude = country_based_config['proxy_info']['location']['longitude']

    # Запуск браузера с Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(
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
        await page.add_init_script("""
            // Подмена свойств браузера для маскировки
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
            Object.defineProperty(navigator, 'deviceMemory', {get: () => 16});
        """)

        # # Подмена WebRTC, чтобы скрыть локальные IP
        await page.add_init_script("""
        (() => {
            const getLocalIPs = (callback) => {
                const ips = ["192.168.1.1", "10.0.0.1", "fd12:3456:789a:1::1"]; // Фейковые IP
                callback(ips);
            };

            class FakeRTCPeerConnection extends RTCPeerConnection {
                constructor(config) {
                    super(config);
                }

                createOffer(...args) {
                    return super.createOffer(...args).then((offer) => {
                        offer.sdp = offer.sdp.replace(
                            /([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3})/g,
                            "192.168.1.1"
                        );
                        return offer;
                    });
                }
            }

            window.RTCPeerConnection = FakeRTCPeerConnection;
            navigator.mediaDevices.enumerateDevices = async () => { return []; }; // Блокируем enumerateDevices
        })();
        """)

        # Подмена WebGL для блокировки идентификации устройства по рендеру
        await page.add_init_script("""
        (() => {
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return "Intel HD Graphics";  // UNMASKED_VENDOR_WEBGL
                if (parameter === 37446) return "Intel Inc.";         // UNMASKED_RENDERER_WEBGL
                return getParameter.call(this, parameter);
            };
        })();
        """)

        # Подмена Canvas для предотвращения фингерпринтинга
        await page.add_init_script("""
        (() => {
            const toDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                console.log("Canvas fingerprinting blocked!");
                return toDataURL.call(this, "image/png"); // Подмена типа изображения
            };

            const getImageData = CanvasRenderingContext2D.prototype.getImageData;
            CanvasRenderingContext2D.prototype.getImageData = function(x, y, width, height) {
                let imageData = getImageData.call(this, x, y, width, height);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i] ^= 10;   // Изменение красного канала
                    imageData.data[i+1] ^= 20; // Изменение зелёного канала
                    imageData.data[i+2] ^= 30; // Изменение синего канала
                }
                return imageData;
            };
        })();
        """)
        #
        # Изменения для предотвращения фингерпринтинга по аудио
        await page.add_init_script("""
        (() => {
            const originalGetChannelData = AudioBuffer.prototype.getChannelData;
            AudioBuffer.prototype.getChannelData = function() {
                const results = originalGetChannelData.apply(this, arguments);
                for (let i = 0; i < results.length; i++) {
                    results[i] = results[i] + (Math.random() * 0.0001); // Незаметное изменение аудиосигнала
                }
                return results;
            };
        })();
        """)
        #
        # # Подмена данных батареи для обхода фингерпринтинга
        await page.add_init_script("""
        (() => {
            navigator.getBattery = function() {
                return new Promise((resolve) => {
                    resolve({
                        charging: true,
                        chargingTime: 0,
                        dischargingTime: 9999,
                        level: 1
                    });
                });
            };
        })();
        """)
        #
        # Блокировка USB и HID устройства
        await page.add_init_script("""
        (() => {
            navigator.usb = undefined;
            navigator.hid = undefined;
        })();
        """)

        # Блокировка информации о плагинах
        await page.add_init_script("""
        (() => {
            Object.defineProperty(navigator, 'plugins', { get: () => [] });
            Object.defineProperty(navigator, 'mimeTypes', { get: () => [] });
        })();
        """)

        # Маскировка платформы (например, под Windows)
        await page.add_init_script("""
        (() => {
            Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
        })();
        """)

        # Маскировка языка браузера
        await page.add_init_script("""
        (() => {
            Object.defineProperty(navigator, 'language', { get: () => 'en-US' });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        })();
        """)

        # Переопределение методов Canvas для защиты от Canvas Fingerprinting
        await page.add_init_script("""
        (() => {
            const getContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(type, ...args) {
                if (type === "2d") {
                    const context = getContext.apply(this, [type, ...args]);

                    const originalGetImageData = context.getImageData;
                    context.getImageData = function(x, y, width, height) {
                        let imageData = originalGetImageData.call(this, x, y, width, height);
                        // Подмена цветов (красный, зеленый, синий)
                        for (let i = 0; i < imageData.data.length; i += 4) {
                            imageData.data[i] ^= 10;   // Красный канал
                            imageData.data[i + 1] ^= 20; // Зеленый канал
                            imageData.data[i + 2] ^= 30; // Синий канал
                        }
                        return imageData;
                    };

                    const originalToDataURL = context.canvas.toDataURL;
                    context.canvas.toDataURL = function(type) {
                        console.log("Canvas fingerprinting attempt detected!");
                        // Применяем низкое качество изображения, чтобы скрыть детали
                        return originalToDataURL.call(this, "image/jpeg", 0.1); // Уменьшаем качество JPEG
                    };

                    // Подмена шрифта для текста на Canvas (если используется)
                    const originalFillText = context.fillText;
                    context.fillText = function(text, x, y) {
                        context.font = "16px 'Arial', sans-serif"; // Применяем фиктивный шрифт
                        return originalFillText.call(this, text, x, y);
                    };

                    return context;
                }
                return getContext.apply(this, arguments);
            };

            // Подмена для OffscreenCanvas, если поддерживается
            if (typeof OffscreenCanvas !== "undefined") {
                const getContextOffscreen = OffscreenCanvas.prototype.getContext;
                OffscreenCanvas.prototype.getContext = function(type, ...args) {
                    if (type === "2d") {
                        return null; // Блокируем попытки Canvas Fingerprinting
                    }
                    return getContextOffscreen.apply(this, arguments);
                };
            }
        })();
        """)

        await page.add_init_script("""
        (() => {
            // Создаём фиктивные шрифты для подмены
            const fakeFonts = [
                'FakeFont1',
                'FakeFont2',
                'FakeFont3',
            ];

            // Переопределяем метод `getComputedStyle` для подмены шрифтов
            const originalGetComputedStyle = window.getComputedStyle;
            window.getComputedStyle = function(element, pseudoElement) {
                const computedStyle = originalGetComputedStyle.apply(this, [element, pseudoElement]);

                // Проверяем стиль font-family
                if (computedStyle.fontFamily) {
                    // Заменяем на фиктивный шрифт
                    computedStyle.fontFamily = fakeFonts.join(', ');
                }

                return computedStyle;
            };

            // Переопределяем `document.fonts` для предотвращения реальной проверки шрифтов
            const originalAdd = Document.prototype.fonts.add;
            Document.prototype.fonts.add = function(font) {
                // Можно также блокировать или подменить добавление новых шрифтов
                console.log(`Font added: ${font.family}`);
                // Не добавляем реальный шрифт, только фиктивный
                originalAdd.call(this, font);
            };

            // Блокируем или подменяем запросы на установку шрифтов
            const originalMatch = FontFace.prototype.load;
            FontFace.prototype.load = function() {
                // Подменяем шрифты, которые загружаются
                const fakeFont = new FontFace('FakeFont', 'url(fake-font-url)');
                return fakeFont.load();
            };

            console.log("Font fingerprinting blocked!");
        })();
        """)

        # Переход на сайт для тестирования IP
        # await page.goto("https://browserleaks.com/")
        await page.goto("https://google.com/")

        while True:
            close = input('\r\rEXIT to close browser: ')
            if close.strip() == 'exit':
                await browser.close()
                break
            else:
                continue


asyncio.run(start_browser('gb'))
