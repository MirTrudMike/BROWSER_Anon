"""
Расширенные параметры для более реалистичной эмуляции браузера
"""

# WebGL параметры с реальными значениями от разных GPU
webgl_variants = {
    "Win64": [
        # NVIDIA
        {"vendor": "NVIDIA Corporation", "renderer": "NVIDIA GeForce GTX 1660/PCIe/SSE2"},
        {"vendor": "NVIDIA Corporation", "renderer": "NVIDIA GeForce RTX 2060/PCIe/SSE2"},
        {"vendor": "NVIDIA Corporation", "renderer": "NVIDIA GeForce RTX 3070/PCIe/SSE2"},
        {"vendor": "NVIDIA Corporation", "renderer": "NVIDIA GeForce GTX 1050 Ti/PCIe/SSE2"},
        {"vendor": "NVIDIA Corporation", "renderer": "NVIDIA GeForce GTX 1070/PCIe/SSE2"},
        # AMD
        {"vendor": "AMD", "renderer": "AMD Radeon RX 580 Series"},
        {"vendor": "AMD", "renderer": "AMD Radeon RX 6600 XT"},
        {"vendor": "AMD", "renderer": "AMD Radeon RX 5700 XT"},
        {"vendor": "AMD", "renderer": "AMD Radeon(TM) Graphics"},
        {"vendor": "AMD", "renderer": "AMD Radeon RX Vega 56"},
        # Intel
        {"vendor": "Intel", "renderer": "Intel(R) UHD Graphics 630"},
        {"vendor": "Intel", "renderer": "Intel(R) Iris(R) Xe Graphics"},
        {"vendor": "Intel", "renderer": "Intel(R) HD Graphics 520"},
        {"vendor": "Intel", "renderer": "Intel(R) Core(TM) i7-8565U"},
        {"vendor": "Intel", "renderer": "Mesa Intel(R) UHD Graphics 620 (WHL GT2)"}
    ],
    "MacIntel": [
        # Apple Silicon
        {"vendor": "Apple", "renderer": "Apple M1"},
        {"vendor": "Apple", "renderer": "Apple M1 Pro"},
        {"vendor": "Apple", "renderer": "Apple M1 Max"},
        {"vendor": "Apple", "renderer": "Apple M2"},
        # Intel Integrated
        {"vendor": "Intel Inc.", "renderer": "Intel(R) Iris(TM) Plus Graphics 645"},
        {"vendor": "Intel Inc.", "renderer": "Intel(R) Iris(TM) Plus Graphics 655"},
        {"vendor": "Intel Inc.", "renderer": "Intel Iris Pro Graphics 5200"},
        # AMD Dedicated
        {"vendor": "AMD", "renderer": "AMD Radeon Pro 5500M"},
        {"vendor": "AMD", "renderer": "AMD Radeon Pro 5600M"},
        {"vendor": "AMD", "renderer": "AMD Radeon Pro Vega 20"}
    ],
    "Linux x86_64": [
        # NVIDIA
        {"vendor": "NVIDIA Corporation", "renderer": "NVIDIA GeForce GTX 1660 Ti/PCIe/SSE2"},
        {"vendor": "NVIDIA Corporation", "renderer": "NVIDIA GeForce RTX 3060/PCIe/SSE2"},
        {"vendor": "NVIDIA Corporation", "renderer": "NVIDIA GeForce GTX 1650/PCIe/SSE2"},
        # AMD
        {"vendor": "AMD", "renderer": "AMD RADV NAVI14"},
        {"vendor": "AMD", "renderer": "AMD RADV RENOIR"},
        {"vendor": "AMD", "renderer": "Mesa DRI AMD Radeon RX 5500 XT"},
        {"vendor": "X.Org", "renderer": "AMD RADV NAVI21"},
        # Intel
        {"vendor": "Intel", "renderer": "Mesa Intel(R) UHD Graphics 620 (KBL GT2)"},
        {"vendor": "Intel", "renderer": "Mesa Intel(R) HD Graphics 5500 (BDW GT2)"},
        {"vendor": "Intel Open Source Technology Center", "renderer": "Mesa DRI Intel(R) HD Graphics 4000 (IVB GT2)"}
    ]
}

# Расширенные параметры Canvas для более реалистичного рендеринга
canvas_variants = {
    "Win64": [
        {"red": 2, "green": 3, "blue": 4, "image_type": "image/png", "quality": 0.95},
        {"red": 1, "green": 2, "blue": 3, "image_type": "image/webp", "quality": 0.92},
        {"red": 3, "green": 4, "blue": 5, "image_type": "image/jpeg", "quality": 0.85},
        {"red": 4, "green": 5, "blue": 6, "image_type": "image/png", "quality": 0.90},
        {"red": 2, "green": 4, "blue": 6, "image_type": "image/webp", "quality": 0.88}
    ],
    "MacIntel": [
        {"red": 1, "green": 3, "blue": 5, "image_type": "image/png", "quality": 0.92},
        {"red": 2, "green": 4, "blue": 6, "image_type": "image/jpeg", "quality": 0.88},
        {"red": 3, "green": 5, "blue": 7, "image_type": "image/webp", "quality": 0.95},
        {"red": 4, "green": 6, "blue": 8, "image_type": "image/png", "quality": 0.93},
        {"red": 1, "green": 2, "blue": 3, "image_type": "image/jpeg", "quality": 0.89}
    ],
    "Linux x86_64": [
        {"red": 2, "green": 4, "blue": 6, "image_type": "image/webp", "quality": 0.90},
        {"red": 3, "green": 5, "blue": 7, "image_type": "image/png", "quality": 0.93},
        {"red": 1, "green": 3, "blue": 5, "image_type": "image/jpeg", "quality": 0.87},
        {"red": 4, "green": 6, "blue": 8, "image_type": "image/webp", "quality": 0.91},
        {"red": 2, "green": 3, "blue": 4, "image_type": "image/png", "quality": 0.94}
    ]
}

# Реалистичные параметры аудио с вариациями шума
audio_variants = {
    "Win64": [
        {"noiseIntensity": 0.0001, "sampleRate": 44100, "channelCount": 2},
        {"noiseIntensity": 0.00015, "sampleRate": 48000, "channelCount": 2},
        {"noiseIntensity": 0.00012, "sampleRate": 96000, "channelCount": 2},
        {"noiseIntensity": 0.00018, "sampleRate": 44100, "channelCount": 1},
        {"noiseIntensity": 0.00014, "sampleRate": 48000, "channelCount": 2}
    ],
    "MacIntel": [
        {"noiseIntensity": 0.00011, "sampleRate": 44100, "channelCount": 2},
        {"noiseIntensity": 0.00013, "sampleRate": 48000, "channelCount": 2},
        {"noiseIntensity": 0.00016, "sampleRate": 96000, "channelCount": 2},
        {"noiseIntensity": 0.00012, "sampleRate": 44100, "channelCount": 1},
        {"noiseIntensity": 0.00015, "sampleRate": 48000, "channelCount": 2}
    ],
    "Linux x86_64": [
        {"noiseIntensity": 0.00013, "sampleRate": 44100, "channelCount": 2},
        {"noiseIntensity": 0.00016, "sampleRate": 48000, "channelCount": 2},
        {"noiseIntensity": 0.00014, "sampleRate": 96000, "channelCount": 2},
        {"noiseIntensity": 0.00017, "sampleRate": 44100, "channelCount": 1},
        {"noiseIntensity": 0.00015, "sampleRate": 48000, "channelCount": 2}
    ]
}

# Реалистичные локальные IP адреса для разных подсетей
local_ip_variants = [
    # Домашние подсети
    ["192.168.1.100", "fe80::1234:5678:9abc:def0", "10.0.0.15"],
    ["192.168.0.150", "fe80::abcd:ef01:2345:6789", "10.0.0.20"],
    ["192.168.2.200", "fe80::fedc:ba98:7654:3210", "10.0.0.25"],
    # Корпоративные подсети
    ["10.50.100.150", "fe80::1111:2222:3333:4444", "172.16.0.100"],
    ["10.60.200.250", "fe80::5555:6666:7777:8888", "172.16.1.150"],
    ["10.70.150.200", "fe80::9999:aaaa:bbbb:cccc", "172.16.2.200"],
    # Смешанные конфигурации
    ["192.168.5.150", "fe80::2222:3333:4444:5555", "10.10.0.100"],
    ["172.16.50.100", "fe80::6666:7777:8888:9999", "192.168.10.150"],
    ["10.100.200.250", "fe80::aaaa:bbbb:cccc:dddd", "172.20.0.200"]
]

# Расширенные характеристики оборудования
hardware_variants = {
    "Win64": [
        {"hardwareConcurrency": 4, "deviceMemory": 8, "platform": "Win64", "oscpu": "Windows NT 10.0"},
        {"hardwareConcurrency": 6, "deviceMemory": 16, "platform": "Win64", "oscpu": "Windows NT 10.0"},
        {"hardwareConcurrency": 8, "deviceMemory": 16, "platform": "Win64", "oscpu": "Windows NT 10.0"},
        {"hardwareConcurrency": 12, "deviceMemory": 32, "platform": "Win64", "oscpu": "Windows NT 10.0"},
        {"hardwareConcurrency": 16, "deviceMemory": 32, "platform": "Win64", "oscpu": "Windows NT 10.0"}
    ],
    "MacIntel": [
        {"hardwareConcurrency": 8, "deviceMemory": 16, "platform": "MacIntel", "oscpu": "Intel Mac OS X 10.15"},
        {"hardwareConcurrency": 10, "deviceMemory": 16, "platform": "MacIntel", "oscpu": "Intel Mac OS X 11.0"},
        {"hardwareConcurrency": 8, "deviceMemory": 8, "platform": "MacIntel", "oscpu": "Intel Mac OS X 10.14"},
        {"hardwareConcurrency": 12, "deviceMemory": 32, "platform": "MacIntel", "oscpu": "Intel Mac OS X 12.0"},
        {"hardwareConcurrency": 10, "deviceMemory": 16, "platform": "MacIntel", "oscpu": "Intel Mac OS X 11.5"}
    ],
    "Linux x86_64": [
        {"hardwareConcurrency": 4, "deviceMemory": 8, "platform": "Linux x86_64", "oscpu": "Linux x86_64"},
        {"hardwareConcurrency": 8, "deviceMemory": 16, "platform": "Linux x86_64", "oscpu": "Linux x86_64"},
        {"hardwareConcurrency": 12, "deviceMemory": 32, "platform": "Linux x86_64", "oscpu": "Linux x86_64"},
        {"hardwareConcurrency": 16, "deviceMemory": 64, "platform": "Linux x86_64", "oscpu": "Linux x86_64"},
        {"hardwareConcurrency": 6, "deviceMemory": 8, "platform": "Linux x86_64", "oscpu": "Linux x86_64"}
    ]
}

# Реалистичные параметры батареи
battery_variants = [
    # Полностью заряжен
    {"charging": True, "chargingTime": 0, "dischargingTime": None, "level": 1.0},
    # Заряжается
    {"charging": True, "chargingTime": 1800, "dischargingTime": None, "level": 0.67},
    {"charging": True, "chargingTime": 3600, "dischargingTime": None, "level": 0.45},
    # Разряжается
    {"charging": False, "chargingTime": None, "dischargingTime": 7200, "level": 0.82},
    {"charging": False, "chargingTime": None, "dischargingTime": 3600, "level": 0.51},
    {"charging": False, "chargingTime": None, "dischargingTime": 1800, "level": 0.23},
    # Почти разряжен
    {"charging": False, "chargingTime": None, "dischargingTime": 900, "level": 0.15},
    # Критический уровень
    {"charging": False, "chargingTime": None, "dischargingTime": 300, "level": 0.05}
]

# Расширенные варианты плагинов
plugins_variants = {
    "Chrome": [
        # Базовый набор
        {
            "plugins": [
                {"name": "Chrome PDF Plugin", "filename": "internal-pdf-viewer", "description": "Portable Document Format"},
                {"name": "Chrome PDF Viewer", "filename": "internal-pdf-viewer", "description": "Portable Document Format"},
                {"name": "Native Client", "filename": "internal-nacl-plugin", "description": "Native Client"}
            ],
            "mimeTypes": [
                {"type": "application/pdf", "suffixes": "pdf", "description": "Portable Document Format"},
                {"type": "application/x-google-chrome-pdf", "suffixes": "pdf", "description": "Portable Document Format"},
                {"type": "application/x-nacl", "suffixes": "", "description": "Native Client"}
            ]
        },
        # Расширенный набор
        {
            "plugins": [
                {"name": "Chrome PDF Plugin", "filename": "internal-pdf-viewer", "description": "Portable Document Format"},
                {"name": "Chrome PDF Viewer", "filename": "internal-pdf-viewer", "description": "Portable Document Format"},
                {"name": "Native Client", "filename": "internal-nacl-plugin", "description": "Native Client"},
                {"name": "Widevine Content Decryption Module", "filename": "widevinecdm", "description": "Enables Widevine licenses for playback of HTML audio/video content."}
            ],
            "mimeTypes": [
                {"type": "application/pdf", "suffixes": "pdf", "description": "Portable Document Format"},
                {"type": "application/x-google-chrome-pdf", "suffixes": "pdf", "description": "Portable Document Format"},
                {"type": "application/x-nacl", "suffixes": "", "description": "Native Client"},
                {"type": "application/x-ppapi-widevine-cdm", "suffixes": "", "description": "Widevine Content Decryption Module"}
            ]
        }
    ],
    "Firefox": [
        # Минимальный набор
        {
            "plugins": [],
            "mimeTypes": []
        },
        # Базовый набор
        {
            "plugins": [
                {"name": "PDF.js", "filename": "pdf.js", "description": "Portable Document Format"}
            ],
            "mimeTypes": [
                {"type": "application/pdf", "suffixes": "pdf", "description": "Portable Document Format"}
            ]
        }
    ]
}

# Расширенные параметры для Canvas 2D
canvas_2d_variants = {
    "Win64": [
        {"font": "12px Arial", "textBaseline": "alphabetic", "fillStyle": "#000000", "quality": 0.92},
        {"font": "14px Helvetica", "textBaseline": "top", "fillStyle": "#242424", "quality": 0.95},
        {"font": "16px Segoe UI", "textBaseline": "middle", "fillStyle": "#121212", "quality": 0.88},
        {"font": "13px Verdana", "textBaseline": "bottom", "fillStyle": "#1a1a1a", "quality": 0.90}
    ],
    "MacIntel": [
        {"font": "12px -apple-system", "textBaseline": "alphabetic", "fillStyle": "#000000", "quality": 0.92},
        {"font": "14px San Francisco", "textBaseline": "top", "fillStyle": "#242424", "quality": 0.95},
        {"font": "16px Helvetica Neue", "textBaseline": "middle", "fillStyle": "#121212", "quality": 0.88},
        {"font": "13px Arial", "textBaseline": "bottom", "fillStyle": "#1a1a1a", "quality": 0.90}
    ],
    "Linux x86_64": [
        {"font": "12px Ubuntu", "textBaseline": "alphabetic", "fillStyle": "#000000", "quality": 0.92},
        {"font": "14px Liberation Sans", "textBaseline": "top", "fillStyle": "#242424", "quality": 0.95},
        {"font": "16px DejaVu Sans", "textBaseline": "middle", "fillStyle": "#121212", "quality": 0.88},
        {"font": "13px Noto Sans", "textBaseline": "bottom", "fillStyle": "#1a1a1a", "quality": 0.90}
    ]
}

# Расширенные наборы шрифтов
fonts_variants = {
    "Win64": [
        # Стандартный набор Windows
        ["Arial", "Times New Roman", "Calibri", "Verdana", "Segoe UI"],
        # Расширенный набор
        ["Georgia", "Tahoma", "Trebuchet MS", "Arial Black", "Impact"],
        # Профессиональный набор
        ["Helvetica", "Palatino Linotype", "Book Antiqua", "Garamond", "Courier New"],
        # Креативный набор
        ["Comic Sans MS", "Brush Script MT", "Lucida Handwriting", "Papyrus", "Harrington"]
    ],
    "MacIntel": [
        # Стандартный набор macOS
        ["-apple-system", "SF Pro Text", "Helvetica Neue", "Helvetica", "Arial"],
        # Расширенный набор
        ["Times", "Georgia", "Palatino", "Baskerville", "Courier"],
        # Профессиональный набор
        ["Avenir", "Futura", "Optima", "Didot", "American Typewriter"],
        # Креативный набор
        ["Marker Felt", "Bradley Hand", "Snell Roundhand", "Zapfino", "Chalkboard"]
    ],
    "Linux x86_64": [
        # Стандартный набор Linux
        ["Ubuntu", "Liberation Sans", "DejaVu Sans", "Noto Sans", "FreeSans"],
        # Расширенный набор
        ["Liberation Serif", "DejaVu Serif", "Noto Serif", "FreeSerif", "Nimbus Roman"],
        # Монospace набор
        ["Ubuntu Mono", "Liberation Mono", "DejaVu Sans Mono", "Noto Mono", "FreeMono"],
        # Дополнительный набор
        ["Cantarell", "Droid Sans", "LXGW WenKai", "Noto Sans CJK", "Garuda"]
    ]
}

# Реалистичные параметры экрана
screen_variants = {
    "Win64": [
        {"width": 1920, "height": 1080, "colorDepth": 24, "pixelDepth": 24, "dpi": 96},
        {"width": 2560, "height": 1440, "colorDepth": 24, "pixelDepth": 24, "dpi": 96},
        {"width": 1366, "height": 768, "colorDepth": 24, "pixelDepth": 24, "dpi": 96},
        {"width": 3840, "height": 2160, "colorDepth": 24, "pixelDepth": 24, "dpi": 96},
        {"width": 1600, "height": 900, "colorDepth": 24, "pixelDepth": 24, "dpi": 96}
    ],
    "MacIntel": [
        {"width": 2560, "height": 1600, "colorDepth": 24, "pixelDepth": 24, "dpi": 227},
        {"width": 2880, "height": 1800, "colorDepth": 24, "pixelDepth": 24, "dpi": 227},
        {"width": 1440, "height": 900, "colorDepth": 24, "pixelDepth": 24, "dpi": 127},
        {"width": 3456, "height": 2234, "colorDepth": 24, "pixelDepth": 24, "dpi": 254},
        {"width": 3024, "height": 1964, "colorDepth": 24, "pixelDepth": 24, "dpi": 254}
    ],
    "Linux x86_64": [
        {"width": 1920, "height": 1080, "colorDepth": 24, "pixelDepth": 24, "dpi": 96},
        {"width": 2560, "height": 1440, "colorDepth": 24, "pixelDepth": 24, "dpi": 96},
        {"width": 3840, "height": 2160, "colorDepth": 24, "pixelDepth": 24, "dpi": 96},
        {"width": 1680, "height": 1050, "colorDepth": 24, "pixelDepth": 24, "dpi": 96},
        {"width": 1600, "height": 900, "colorDepth": 24, "pixelDepth": 24, "dpi": 96}
    ]
}

# Расширенные параметры для эмуляции поведения пользователя
user_behavior_variants = {
    "mouse": {
        "moveSpeed": [0.8, 1.0, 1.2, 1.5],  # Скорость движения мыши
        "clickDelay": [50, 100, 150, 200],   # Задержка между кликами в мс
        "doubleClickDelay": [200, 250, 300, 350]  # Задержка двойного клика в мс
    },
    "keyboard": {
        "typingSpeed": [100, 150, 200, 250],  # Скорость печати (мс между нажатиями)
        "typingVariance": [10, 20, 30, 40],   # Вариация скорости печати в мс
        "keyPressTime": [50, 70, 90, 110]     # Время удержания клавиши в мс
    },
    "scroll": {
        "speed": [100, 150, 200, 250],        # Скорость скролла
        "smoothness": [0.8, 0.9, 1.0, 1.1],   # Плавность скролла
        "pauseTime": [500, 1000, 1500, 2000]  # Пауза между скроллами в мс
    }
}

# Расширенные параметры для эмуляции истории браузера
history_variants = {
    "visitFrequency": [
        {"daily": 20, "weekly": 100, "monthly": 400},
        {"daily": 50, "weekly": 200, "monthly": 800},
        {"daily": 30, "weekly": 150, "monthly": 600},
        {"daily": 40, "weekly": 180, "monthly": 700}
    ],
    "timeSpent": [
        {"min": 30, "avg": 120, "max": 300},
        {"min": 60, "avg": 180, "max": 400},
        {"min": 45, "avg": 150, "max": 350},
        {"min": 40, "avg": 160, "max": 380}
    ],
    "bookmarkCount": [10, 25, 50, 100],
    "historyDepth": [7, 14, 30, 60]  # дней
}

# Расширенные параметры для эмуляции сетевого поведения
network_variants = {
    "bandwidth": [
        {"download": 10000000, "upload": 5000000},  # 10/5 Mbps
        {"download": 50000000, "upload": 20000000}, # 50/20 Mbps
        {"download": 100000000, "upload": 40000000}, # 100/40 Mbps
        {"download": 200000000, "upload": 100000000} # 200/100 Mbps
    ],
    "latency": [
        {"min": 10, "avg": 20, "max": 40},
        {"min": 20, "avg": 35, "max": 60},
        {"min": 30, "avg": 50, "max": 80},
        {"min": 40, "avg": 70, "max": 100}
    ],
    "packetLoss": [0.0, 0.1, 0.2, 0.5],  # процент потери пакетов
    "connectionType": ["wifi", "ethernet", "4g", "5g"]
} 