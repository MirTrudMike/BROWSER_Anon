from dataclasses import dataclass, field


@dataclass
class ProfileConfig:
    """
    Controls which fingerprint masking scripts are injected into pages.

    Every field maps 1-to-1 to a ScriptInjector method.
    base_masking and webrtc should always stay True — disabling them
    immediately exposes automation markers or leaks the real IP.
    """

    # Core — disabling breaks the main purpose of the tool
    base_masking: bool = True   # Remove playwright/webdriver markers, inject chrome object
    webrtc:       bool = True   # Replace local IPs in WebRTC SDP, block enumerateDevices
    platform:     bool = True   # navigator.platform  (must match User-Agent)
    language:     bool = True   # navigator.language / navigator.languages

    # Hardware & GPU
    hardware:     bool = True   # navigator.hardwareConcurrency, navigator.deviceMemory
    webgl:        bool = True   # WebGL vendor and renderer strings

    # Fingerprinting noise
    canvas:       bool = True   # Canvas toDataURL / getImageData noise
    canvas_2d:    bool = True   # Canvas 2D context: getImageData, fillText, toDataURL
    audio:        bool = True   # AudioBuffer channel data noise
    fonts:        bool = True   # Override getComputedStyle fontFamily

    # Peripheral / API emulation
    battery:      bool = True   # navigator.getBattery() emulation
    usb:          bool = True   # Disable navigator.usb / navigator.hid
    plugins:      bool = True   # navigator.plugins / navigator.mimeTypes


# ---------------------------------------------------------------------------
# Built-in presets
# ---------------------------------------------------------------------------

# Maximum protection — every script active.
STEALTH = ProfileConfig()

# Compatibility — disable scripts that can break sites or trigger detection
# by their mere presence (canvas noise, audio noise) or break web apps (USB).
COMPATIBILITY = ProfileConfig(
    canvas=False,
    canvas_2d=False,
    audio=False,
    battery=False,
    usb=False,
    plugins=False,
)

# Debug — same defaults as STEALTH; intended to be copied and mutated freely.
DEBUG = ProfileConfig()
