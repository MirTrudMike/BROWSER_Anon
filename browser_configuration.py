import parameters
import random


def make_config(system, browser):
    hardware_config = random.choice(parameters.hardware[system])
    local_ip_set = random.choice(parameters.local_ips)
    webgl = random.choice(parameters.webgl_variants[system])
    canvas = random.choice(parameters.canvas[system])
    audio = random.choice(parameters.audio[system])
    battery = random.choice(parameters.battery[system])
    usb = random.choice(parameters.usb)
    plugins = random.choice(parameters.plugins[browser])
    canvas_2 = random.choice(parameters.canvas_2[system])
    fonts = random.choice(parameters.fonts[system])

    config = {'hardware': hardware_config,
              'local_ip_set': local_ip_set,
              'webgl': webgl,
              'canvas': canvas,
              'audio': audio,
              'battery': battery,
              'usb': usb,
              'plugins': plugins,
              'canvas_2': canvas_2,
              'fonts': fonts}


    return config