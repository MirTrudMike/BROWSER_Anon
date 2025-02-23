hardware = {
    'Win64': [
        { 'hardwareConcurrency': 4, 'deviceMemory': 8 },
        { 'hardwareConcurrency': 8, 'deviceMemory': 16 },
        { 'hardwareConcurrency': 12, 'deviceMemory': 32 },
        { 'hardwareConcurrency': 6, 'deviceMemory': 12 },
        { 'hardwareConcurrency': 10, 'deviceMemory': 24 }
    ],
    'Linux x86_64': [
        { 'hardwareConcurrency': 4, 'deviceMemory': 8 },
        { 'hardwareConcurrency': 6, 'deviceMemory': 16 },
        { 'hardwareConcurrency': 8, 'deviceMemory': 32 },
        { 'hardwareConcurrency': 12, 'deviceMemory': 64 }
    ],
    'MacIntel': [
        { 'hardwareConcurrency': 4, 'deviceMemory': 8 },
        { 'hardwareConcurrency': 6, 'deviceMemory': 16 },
        { 'hardwareConcurrency': 8, 'deviceMemory': 32 },
        { 'hardwareConcurrency': 10, 'deviceMemory': 64 },
        { 'hardwareConcurrency': 12, 'deviceMemory': 128 }
    ]}

local_ips = [
    ["192.168.1.1", "10.0.0.1", "fd12:3456:789a:1::1"],
    ["192.168.0.100", "10.0.0.2", "fd12:3456:789a:2::1"],
    ["192.168.2.15", "10.0.0.3", "fd12:3456:789a:3::1"],
    ["192.168.10.50", "10.0.0.4", "fd12:3456:789a:4::1"],
    ["192.168.5.1", "10.0.0.5", "fd12:3456:789a:5::1"],
    ["192.168.3.10", "10.0.0.6", "fd12:3456:789a:6::1"],
    ["192.168.7.20", "10.0.0.7", "fd12:3456:789a:7::1"],
    ["192.168.8.30", "10.0.0.8", "fd12:3456:789a:8::1"],
    ["192.168.9.40", "10.0.0.9", "fd12:3456:789a:9::1"],
    ["192.168.11.60", "10.0.0.10", "fd12:3456:789a:10::1"],
    ["192.168.12.70", "10.0.0.11", "fd12:3456:789a:11::1"],
    ["192.168.13.80", "10.0.0.12", "fd12:3456:789a:12::1"],
    ["192.168.14.90", "10.0.0.13", "fd12:3456:789a:13::1"],
    ["192.168.15.100", "10.0.0.14", "fd12:3456:789a:14::1"],
    ["192.168.16.110", "10.0.0.15", "fd12:3456:789a:15::1"],
    ["192.168.17.120", "10.0.0.16", "fd12:3456:789a:16::1"],
    ["192.168.18.130", "10.0.0.17", "fd12:3456:789a:17::1"],
    ["192.168.19.140", "10.0.0.18", "fd12:3456:789a:18::1"],
    ["192.168.20.150", "10.0.0.19", "fd12:3456:789a:19::1"],
    ["192.168.21.160", "10.0.0.20", "fd12:3456:789a:20::1"],
    ["192.168.22.170", "10.0.0.21", "fd12:3456:789a:21::1"],
    ["192.168.23.180", "10.0.0.22", "fd12:3456:789a:22::1"],
    ["192.168.24.190", "10.0.0.23", "fd12:3456:789a:23::1"],
    ["192.168.25.200", "10.0.0.24", "fd12:3456:789a:24::1"],
    ["192.168.26.210", "10.0.0.25", "fd12:3456:789a:25::1"],
    ["192.168.27.220", "10.0.0.26", "fd12:3456:789a:26::1"],
    ["192.168.28.230", "10.0.0.27", "fd12:3456:789a:27::1"],
    ["192.168.29.240", "10.0.0.28", "fd12:3456:789a:28::1"],
    ["192.168.30.250", "10.0.0.29", "fd12:3456:789a:29::1"],
    ["192.168.31.255", "10.0.0.30", "fd12:3456:789a:30::1"],
    ["192.168.32.10", "10.0.0.31", "fd12:3456:789a:31::1"],
    ["192.168.33.20", "10.0.0.32", "fd12:3456:789a:32::1"],
    ["192.168.34.30", "10.0.0.33", "fd12:3456:789a:33::1"],
    ["192.168.35.40", "10.0.0.34", "fd12:3456:789a:34::1"],
    ["192.168.36.50", "10.0.0.35", "fd12:3456:789a:35::1"],
    ["192.168.37.60", "10.0.0.36", "fd12:3456:789a:36::1"],
    ["192.168.38.70", "10.0.0.37", "fd12:3456:789a:37::1"],
    ["192.168.39.80", "10.0.0.38", "fd12:3456:789a:38::1"],
    ["192.168.40.90", "10.0.0.39", "fd12:3456:789a:39::1"],
    ["192.168.41.100", "10.0.0.40", "fd12:3456:789a:40::1"],
    ["192.168.42.110", "10.0.0.41", "fd12:3456:789a:41::1"],
    ["192.168.43.120", "10.0.0.42", "fd12:3456:789a:42::1"],
    ["192.168.44.130", "10.0.0.43", "fd12:3456:789a:43::1"],
    ["192.168.45.140", "10.0.0.44", "fd12:3456:789a:44::1"],
    ["192.168.46.150", "10.0.0.45", "fd12:3456:789a:45::1"],
    ["192.168.47.160", "10.0.0.46", "fd12:3456:789a:46::1"],
    ["192.168.48.170", "10.0.0.47", "fd12:3456:789a:47::1"],
    ["192.168.49.180", "10.0.0.48", "fd12:3456:789a:48::1"],
    ["192.168.50.190", "10.0.0.49", "fd12:3456:789a:49::1"],
    ["192.168.51.200", "10.0.0.50", "fd12:3456:789a:50::1"]
]

webgl_variants = {
    "Win64": [
        {"vendor": "Intel", "renderer": "Intel HD Graphics 630"},
        {"vendor": "NVIDIA Corporation", "renderer": "NVIDIA GeForce GTX 1080"},
        {"vendor": "AMD", "renderer": "AMD Radeon RX 580"},
        {"vendor": "NVIDIA", "renderer": "NVIDIA Quadro P4000"},
        {"vendor": "Microsoft", "renderer": "Direct3D11"},
        {"vendor": "Intel", "renderer": "Intel UHD Graphics 750"},
        {"vendor": "AMD", "renderer": "AMD Radeon RX 6900 XT"}
    ],
    "MacIntel": [
        {"vendor": "Intel", "renderer": "Intel Iris Plus Graphics 640"},
        {"vendor": "Intel", "renderer": "Intel UHD Graphics 630"},
        {"vendor": "AMD", "renderer": "AMD Radeon Pro 5500M"},
        {"vendor": "AMD", "renderer": "AMD Radeon Pro 560X"},
        {"vendor": "Apple", "renderer": "Apple M1 GPU"},
        {"vendor": "Intel", "renderer": "Intel HD Graphics 5000"},
        {"vendor": "AMD", "renderer": "AMD Radeon Pro Vega 20"}
    ],
    "Linux x86_64": [
        {"vendor": "Intel", "renderer": "Intel HD Graphics 620"},
        {"vendor": "NVIDIA Corporation", "renderer": "NVIDIA GeForce GTX 1660 Ti"},
        {"vendor": "AMD", "renderer": "AMD Radeon RX 570"},
        {"vendor": "NVIDIA", "renderer": "NVIDIA Quadro P2000"},
        {"vendor": "VMware", "renderer": "SVGA3D"},
        {"vendor": "Intel", "renderer": "Intel Iris Xe Graphics"},
        {"vendor": "AMD", "renderer": "AMD Radeon RX 6700 XT"}
    ]
}

canvas = {
    "Win64": [
        {"red": 5, "green": 10, "blue": 15, "image_type": "image/png"},
        {"red": 8, "green": 12, "blue": 18, "image_type": "image/jpeg"},
        {"red": 3, "green": 7, "blue": 11, "image_type": "image/webp"},
        {"red": 6, "green": 14, "blue": 20, "image_type": "image/png"},
        {"red": 9, "green": 13, "blue": 17, "image_type": "image/jpeg"}
    ],
    "MacIntel": [
        {"red": 4, "green": 9, "blue": 14, "image_type": "image/png"},
        {"red": 7, "green": 11, "blue": 16, "image_type": "image/jpeg"},
        {"red": 2, "green": 6, "blue": 10, "image_type": "image/webp"},
        {"red": 5, "green": 12, "blue": 19, "image_type": "image/png"},
        {"red": 8, "green": 10, "blue": 15, "image_type": "image/jpeg"}
    ],
    "Linux x86_64": [
        {"red": 6, "green": 11, "blue": 16, "image_type": "image/png"},
        {"red": 9, "green": 13, "blue": 18, "image_type": "image/jpeg"},
        {"red": 4, "green": 8, "blue": 12, "image_type": "image/webp"},
        {"red": 7, "green": 14, "blue": 20, "image_type": "image/png"},
        {"red": 10, "green": 12, "blue": 17, "image_type": "image/jpeg"}
    ]}

audio = {
    "Win64": [
        {"noiseIntensity": 0.0001},
        {"noiseIntensity": 0.0002},
        {"noiseIntensity": 0.00015},
        {"noiseIntensity": 0.00005},
        {"noiseIntensity": 0.00012}
    ],
    "MacIntel": [
        {"noiseIntensity": 0.00008},
        {"noiseIntensity": 0.00018},
        {"noiseIntensity": 0.0001},
        {"noiseIntensity": 0.00006},
        {"noiseIntensity": 0.00014}
    ],
    "Linux x86_64": [
        {"noiseIntensity": 0.00009},
        {"noiseIntensity": 0.0002},
        {"noiseIntensity": 0.00011},
        {"noiseIntensity": 0.00007},
        {"noiseIntensity": 0.00013}
    ]}

battery = {
    "Win64": [
        {"charging": True, "chargingTime": 0, "dischargingTime": 9999, "level": 1.0},  # Полностью заряжено
        {"charging": True, "chargingTime": 1800, "dischargingTime": 7200, "level": 0.8},  # Заряжается, 80%
        {"charging": False, "chargingTime": 0, "dischargingTime": 3600, "level": 0.5},  # Разряжается, 50%
        {"charging": False, "chargingTime": 0, "dischargingTime": 1800, "level": 0.3},  # Разряжается, 30%
        {"charging": True, "chargingTime": 3600, "dischargingTime": 0, "level": 0.6}   # Заряжается, 60%
    ],
    "MacIntel": [
        {"charging": True, "chargingTime": 0, "dischargingTime": 9999, "level": 1.0},  # Полностью заряжено
        {"charging": True, "chargingTime": 1200, "dischargingTime": 5400, "level": 0.9},  # Заряжается, 90%
        {"charging": False, "chargingTime": 0, "dischargingTime": 2700, "level": 0.4},  # Разряжается, 40%
        {"charging": False, "chargingTime": 0, "dischargingTime": 900, "level": 0.2},   # Разряжается, 20%
        {"charging": True, "chargingTime": 2400, "dischargingTime": 0, "level": 0.7}   # Заряжается, 70%
    ],
    "Linux x86_64": [
        {"charging": True, "chargingTime": 0, "dischargingTime": 9999, "level": 1.0},  # Полностью заряжено
        {"charging": True, "chargingTime": 1500, "dischargingTime": 6000, "level": 0.85},  # Заряжается, 85%
        {"charging": False, "chargingTime": 0, "dischargingTime": 3000, "level": 0.45},  # Разряжается, 45%
        {"charging": False, "chargingTime": 0, "dischargingTime": 1200, "level": 0.25},  # Разряжается, 25%
        {"charging": True, "chargingTime": 3000, "dischargingTime": 0, "level": 0.65}  # Заряжается, 65%
    ]}

usb = [{"disableUSB": True, "disableHID": True},  # Отключить оба API
        {"disableUSB": True, "disableHID": False},  # Отключить только WebUSB
        {"disableUSB": False, "disableHID": True},  # Отключить только WebHID
        {"disableUSB": False, "disableHID": False}]

plugins = {
    "Chrome": [
        {"plugins": ["Chrome PDF Viewer"], "mimeTypes": ["application/pdf"]},  # Только PDF Viewer
        {"plugins": ["Chrome PDF Viewer", "Widevine Content Decryption Module"], "mimeTypes": ["application/pdf", "application/x-ppapi-widevine-cdm"]},  # PDF + Widevine
        {"plugins": ["Chrome PDF Viewer", "Native Client"], "mimeTypes": ["application/pdf", "application/x-nacl"]},  # PDF + Native Client
        {"plugins": ["Widevine Content Decryption Module"], "mimeTypes": ["application/x-ppapi-widevine-cdm"]},  # Только Widevine
        {"plugins": [], "mimeTypes": []}  # Без плагинов
    ],
    "Edge": [
        {"plugins": ["Microsoft Edge PDF Viewer"], "mimeTypes": ["application/pdf"]},  # Только Edge PDF Viewer
        {"plugins": ["Microsoft Edge PDF Viewer", "Widevine Content Decryption Module"], "mimeTypes": ["application/pdf", "application/x-ppapi-widevine-cdm"]},  # PDF + Widevine
        {"plugins": ["Microsoft Edge PDF Viewer", "Native Client"], "mimeTypes": ["application/pdf", "application/x-nacl"]},  # PDF + Native Client
        {"plugins": ["Widevine Content Decryption Module"], "mimeTypes": ["application/x-ppapi-widevine-cdm"]},  # Только Widevine
        {"plugins": [], "mimeTypes": []}  # Без плагинов
    ],
    "Firefox": [
        {"plugins": [], "mimeTypes": []},  # Firefox обычно не показывает плагины
        {"plugins": ["OpenH264 Video Codec provided by Cisco Systems, Inc."], "mimeTypes": ["video/ogg"]},  # Пример с кодеком
        {"plugins": ["Primetime Content Decryption Module"], "mimeTypes": ["application/x-ppapi-widevine-cdm"]},  # Widevine для Firefox
        {"plugins": ["Default Browser Helper"], "mimeTypes": ["application/x-default-browser"]},  # Пример для Firefox
        {"plugins": [], "mimeTypes": []}  # Без плагинов
    ],
    "Safari": [
        {"plugins": [], "mimeTypes": []},  # Safari обычно не показывает плагины
        {"plugins": ["QuickTime Plug-in 7.7.3"], "mimeTypes": ["video/quicktime"]},  # Пример с QuickTime
        {"plugins": ["Adobe Flash Player"], "mimeTypes": ["application/x-shockwave-flash"]},  # Пример с Flash (устаревший)
        {"plugins": ["Silverlight Plug-In"], "mimeTypes": ["application/x-silverlight"]},  # Пример с Silverlight
        {"plugins": [], "mimeTypes": []}  # Без плагинов
    ]
}

canvas_2 = {
    "Win64": [
        {"red": 10, "green": 20, "blue": 30, "image_quality": 0.1, "font": "16px 'Arial', sans-serif"},
        {"red": 5, "green": 15, "blue": 25, "image_quality": 0.2, "font": "14px 'Verdana', sans-serif"},
        {"red": 8, "green": 18, "blue": 28, "image_quality": 0.15, "font": "18px 'Times New Roman', serif"},
        {"red": 12, "green": 22, "blue": 32, "image_quality": 0.1, "font": "16px 'Courier New', monospace"},
        {"red": 7, "green": 17, "blue": 27, "image_quality": 0.25, "font": "14px 'Georgia', serif"}
    ],
    "MacIntel": [
        {"red": 10, "green": 20, "blue": 30, "image_quality": 0.1, "font": "16px 'Helvetica', sans-serif"},
        {"red": 5, "green": 15, "blue": 25, "image_quality": 0.2, "font": "14px 'San Francisco', sans-serif"},
        {"red": 8, "green": 18, "blue": 28, "image_quality": 0.15, "font": "18px 'Times New Roman', serif"},
        {"red": 12, "green": 22, "blue": 32, "image_quality": 0.1, "font": "16px 'Courier New', monospace"},
        {"red": 7, "green": 17, "blue": 27, "image_quality": 0.25, "font": "14px 'Georgia', serif"}
    ],
    "Linux x86_64": [
        {"red": 10, "green": 20, "blue": 30, "image_quality": 0.1, "font": "16px 'DejaVu Sans', sans-serif"},
        {"red": 5, "green": 15, "blue": 25, "image_quality": 0.2, "font": "14px 'Liberation Sans', sans-serif"},
        {"red": 8, "green": 18, "blue": 28, "image_quality": 0.15, "font": "18px 'FreeSerif', serif"},
        {"red": 12, "green": 22, "blue": 32, "image_quality": 0.1, "font": "16px 'Courier New', monospace"},
        {"red": 7, "green": 17, "blue": 27, "image_quality": 0.25, "font": "14px 'Georgia', serif"}
    ]
}


fonts = {
    "Win64": [
        ["Arial", "Times New Roman", "Verdana"],  # Набор 1
        ["Calibri", "Georgia", "Courier New"],    # Набор 2
        ["Tahoma", "Trebuchet MS", "Impact"],     # Набор 3
        ["Arial", "Verdana", "Georgia"],         # Набор 4
        ["Times New Roman", "Courier New", "Arial"],  # Набор 5
        ["Segoe UI", "Cambria", "Consolas"],     # Набор 6
        ["Arial Black", "Comic Sans MS", "Lucida Console"],  # Набор 7
        ["Franklin Gothic Medium", "Palatino Linotype", "Book Antiqua"],  # Набор 8
        ["MS Sans Serif", "MS Serif", "Wingdings"],  # Набор 9
        ["Candara", "Corbel", "Constantia"]      # Набор 10
    ],
    "MacIntel": [
        ["Helvetica", "Times New Roman", "Courier"],  # Набор 1
        ["San Francisco", "Georgia", "Arial"],       # Набор 2
        ["Helvetica", "Verdana", "Courier New"],     # Набор 3
        ["Times New Roman", "Arial", "Georgia"],     # Набор 4
        ["Courier", "Helvetica", "San Francisco"],  # Набор 5
        ["Menlo", "Lucida Grande", "Geneva"],       # Набор 6
        ["Apple Chancery", "Papyrus", "Zapfino"],   # Набор 7
        ["Optima", "Didot", "Futura"],              # Набор 8
        ["Baskerville", "Gill Sans", "Hoefler Text"],  # Набор 9
        ["American Typewriter", "Marker Felt", "Monaco"]  # Набор 10
    ],
    "Linux x86_64": [
        ["DejaVu Sans", "Liberation Sans", "FreeSerif"],  # Набор 1
        ["Ubuntu", "Roboto", "Open Sans"],               # Набор 2
        ["DejaVu Sans", "Arial", "Courier New"],         # Набор 3
        ["Liberation Sans", "Times New Roman", "Georgia"],  # Набор 4
        ["FreeSerif", "DejaVu Sans", "Ubuntu"],          # Набор 5
        ["Noto Sans", "Droid Sans", "Cantarell"],        # Набор 6
        ["Liberation Mono", "Nimbus Sans", "URW Gothic"],  # Набор 7
        ["Fira Sans", "Overpass", "Source Sans Pro"],    # Набор 8
        ["Hack", "Inconsolata", "Fira Code"],           # Набор 9
        ["Lato", "Raleway", "PT Sans"]                  # Набор 10
    ]
}