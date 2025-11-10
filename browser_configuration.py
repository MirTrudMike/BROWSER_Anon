import parameters
import random
from extended_parameters import *
import hashlib
import time
from logger_config import log_info, log_debug, log_exception, log_warning

def generate_session_hash():
    """Генерирует уникальный хеш для сессии на основе времени"""
    try:
        current_time = str(time.time()).encode('utf-8')
        session_hash = hashlib.md5(current_time).hexdigest()
        log_debug(f"Generated session hash: {session_hash}")
        return session_hash
    except Exception as e:
        log_exception(e, "Error generating session hash")
        raise

def get_consistent_random(session_hash, salt):
    """Генерирует предсказуемое случайное число на основе хеша сессии"""
    try:
        combined = (session_hash + salt).encode('utf-8')
        hash_value = hashlib.md5(combined).hexdigest()
        random_value = int(hash_value, 16) / 2**128
        log_debug(f"Generated consistent random for salt '{salt}': {random_value}")
        return random_value
    except Exception as e:
        log_exception(e, f"Error generating consistent random with salt '{salt}'")
        raise

def select_from_list(session_hash, salt, items):
    """Выбирает элемент из списка на основе хеша сессии"""
    try:
        index = int(get_consistent_random(session_hash, salt) * len(items))
        selected_item = items[index]
        log_debug(f"Selected item with salt '{salt}': {selected_item}")
        return selected_item
    except Exception as e:
        log_exception(e, f"Error selecting from list with salt '{salt}'")
        raise

def make_config(system, browser):
    """
    Создает конфигурацию браузера с ротацией параметров,
    но сохраняет консистентность в рамках одной сессии
    """
    try:
        log_info(f"Creating configuration for system: {system}, browser: {browser}")
        session_hash = generate_session_hash()
        
        # Маппинг браузеров для плагинов
        browser_plugin_map = {
            'Chrome': 'Chrome',
            'Edge': 'Chrome',  # Edge использует те же плагины, что и Chrome
            'Firefox': 'Firefox',
            'Safari': 'Chrome'  # Safari тоже будет использовать плагины Chrome
        }
        plugin_browser = browser_plugin_map.get(browser, 'Chrome')
        
        # Базовые параметры браузера
        log_debug("Selecting base browser parameters...")
        webgl = select_from_list(session_hash, "webgl", webgl_variants[system])
        canvas = select_from_list(session_hash, "canvas", canvas_variants[system])
        audio = select_from_list(session_hash, "audio", audio_variants[system])
        local_ip_set = select_from_list(session_hash, "ip", local_ip_variants)
        hardware = select_from_list(session_hash, "hardware", hardware_variants[system])
        battery = select_from_list(session_hash, "battery", battery_variants)
        plugins = select_from_list(session_hash, "plugins", plugins_variants[plugin_browser])
        canvas_2d = select_from_list(session_hash, "canvas2d", canvas_2d_variants[system])
        # Убедимся, что canvas_2d содержит все необходимые параметры
        canvas_2d = {
            'red': canvas_2d.get('red', 1),
            'green': canvas_2d.get('green', 2),
            'blue': canvas_2d.get('blue', 3),
            'quality': canvas_2d.get('quality', 0.92),
            'font': canvas_2d.get('font', '12px Arial')
        }
        fonts = select_from_list(session_hash, "fonts", fonts_variants[system])
        
        # Новые параметры
        log_debug("Selecting screen parameters...")
        screen = select_from_list(session_hash, "screen", screen_variants[system])
        
        # Параметры поведения пользователя
        log_debug("Configuring user behavior parameters...")
        mouse_behavior = {
            "moveSpeed": select_from_list(session_hash, "mouse_speed", user_behavior_variants["mouse"]["moveSpeed"]),
            "clickDelay": select_from_list(session_hash, "click_delay", user_behavior_variants["mouse"]["clickDelay"]),
            "doubleClickDelay": select_from_list(session_hash, "dbl_click", user_behavior_variants["mouse"]["doubleClickDelay"])
        }
        
        keyboard_behavior = {
            "typingSpeed": select_from_list(session_hash, "typing_speed", user_behavior_variants["keyboard"]["typingSpeed"]),
            "typingVariance": select_from_list(session_hash, "typing_var", user_behavior_variants["keyboard"]["typingVariance"]),
            "keyPressTime": select_from_list(session_hash, "key_press", user_behavior_variants["keyboard"]["keyPressTime"])
        }
        
        scroll_behavior = {
            "speed": select_from_list(session_hash, "scroll_speed", user_behavior_variants["scroll"]["speed"]),
            "smoothness": select_from_list(session_hash, "scroll_smooth", user_behavior_variants["scroll"]["smoothness"]),
            "pauseTime": select_from_list(session_hash, "scroll_pause", user_behavior_variants["scroll"]["pauseTime"])
        }
        
        # История браузера
        log_debug("Configuring browser history parameters...")
        history = {
            "visitFrequency": select_from_list(session_hash, "visit_freq", history_variants["visitFrequency"]),
            "timeSpent": select_from_list(session_hash, "time_spent", history_variants["timeSpent"]),
            "bookmarkCount": select_from_list(session_hash, "bookmarks", history_variants["bookmarkCount"]),
            "historyDepth": select_from_list(session_hash, "history_depth", history_variants["historyDepth"])
        }
        
        # Сетевые параметры
        log_debug("Configuring network parameters...")
        network = {
            "bandwidth": select_from_list(session_hash, "bandwidth", network_variants["bandwidth"]),
            "latency": select_from_list(session_hash, "latency", network_variants["latency"]),
            "packetLoss": select_from_list(session_hash, "packet_loss", network_variants["packetLoss"]),
            "connectionType": select_from_list(session_hash, "connection", network_variants["connectionType"])
        }

        # Добавляем небольшую случайность к некоторым числовым параметрам
        log_debug("Applying parameter variations...")
        audio["noiseIntensity"] *= (0.95 + get_consistent_random(session_hash, "noise") * 0.1)
        canvas["quality"] *= (0.98 + get_consistent_random(session_hash, "quality") * 0.04)
        
        # Добавляем небольшую вариацию к параметрам поведения
        mouse_behavior["moveSpeed"] *= (0.95 + get_consistent_random(session_hash, "mouse_var") * 0.1)
        keyboard_behavior["typingSpeed"] *= (0.95 + get_consistent_random(session_hash, "typing_var") * 0.1)
        scroll_behavior["speed"] *= (0.95 + get_consistent_random(session_hash, "scroll_var") * 0.1)

        config = {
            'hardware': hardware,
            'local_ip_set': local_ip_set,
            'webgl': webgl,
            'canvas': canvas,
            'audio': audio,
            'battery': battery,
            'usb': {
                'disableUSB': bool(get_consistent_random(session_hash, "usb") > 0.5),
                'disableHID': bool(get_consistent_random(session_hash, "hid") > 0.5)
            },
            'plugins': plugins,
            'canvas_2d': canvas_2d,
            'fonts': fonts,
            'screen': screen,
            'user_behavior': {
                'mouse': mouse_behavior,
                'keyboard': keyboard_behavior,
                'scroll': scroll_behavior
            },
            'history': history,
            'network': network
        }

        log_info("Configuration created successfully")
        log_debug(f"Final configuration: {config}")
        return config
        
    except Exception as e:
        log_exception(e, "Error creating browser configuration")
        raise