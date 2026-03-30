<div align="center">

# 🔥 Ember Browser

**Anonymous browser session launcher**

*Proxy rotation · Fingerprint masking · Geolocation spoofing*

---

</div>

## What is Ember?

Ember is a desktop application that launches isolated, anonymous Chromium browser sessions. Each session gets a clean identity — a fresh IP address from a verified geo-location and a fully spoofed browser fingerprint — so that every time you open a new session, the web sees a different person from a different machine.

The interface is minimal by design: pick a country, pick a profile, click Launch.

---

## What it does

### Identity per session

Each launch assigns a unique combination of:

- **IP address** — rotated from a residential proxy pool, geo-verified before use
- **User-Agent** — realistic browser string matching the selected country and OS
- **Screen resolution & language** — consistent with the chosen locale

Previously used IPs are tracked and never reused in the same installation.

### Fingerprint masking

Ember injects scripts into every page before it loads to neutralise the most common browser fingerprinting vectors:

| Vector | What gets masked |
|--------|-----------------|
| WebGL | GPU vendor and renderer string |
| Canvas | Pixel-level noise on 2D and bitmap canvas reads |
| AudioContext | Subtle noise injected into audio processing output |
| WebRTC | Local IP address leaks blocked entirely |
| Navigator | `platform`, `language`, `hardwareConcurrency`, `deviceMemory` |
| Plugins | Realistic plugin list, no automation markers |
| Battery API | Emulated battery state |
| USB / HID | APIs disabled to prevent device enumeration |
| Automation flags | `webdriver`, Playwright and Chromium automation markers removed |

### Two profiles

**STEALTH** — maximum coverage, all masking layers active. For situations where detection resistance matters most.

**COMPATIBILITY** — core masking only (WebGL, WebRTC, navigator properties, fonts). Canvas and audio noise disabled for better site compatibility.

### Supported countries

🇷🇺 Russia · 🇬🇪 Georgia · 🇮🇱 Israel · 🇦🇪 UAE · 🇩🇪 Germany · 🇬🇧 United Kingdom · 🇹🇷 Turkey · 🇺🇸 United States · 🇫🇷 France · 🇦🇲 Armenia · 🇰🇷 South Korea

---

## Stack

- **Python 3.10+** — application runtime
- **PyQt5** — desktop GUI with a dark Kinetic Console theme
- **Playwright** — Chromium browser automation
- **proxy.market** — residential proxy pool for IP rotation

---
---

## Installation

### One command (Fedora / Debian / Ubuntu)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/MirTrudMike/BROWSER_Anon/master/install.sh)
```

Or clone first, then run:

```bash
git clone https://github.com/MirTrudMike/BROWSER_Anon.git
cd BROWSER_Anon
bash install.sh
```

The installer will:
- Install all required system packages (`dnf` on Fedora, `apt` on Debian/Ubuntu)
- Clone the repository to `~/.local/share/ember-browser/`
- Create a Python virtual environment and install all Python dependencies
- Download Playwright Chromium (~170 MB, one-time)
- Create a `proxies.json` credential template
- Install a launch script at `~/.local/bin/ember-browser`
- Register a `.desktop` entry so the app appears in your application menu

### Requirements

- Python 3.10 or newer
- `git`
- Internet connection
- `sudo` access (for system packages and Playwright browser dependencies)

---

## Launching

```bash
# Terminal
ember-browser

# Desktop
# Applications → Ember Browser
```

---

## Proxy configuration

Ember uses [proxy.market](https://proxy.market) as the proxy provider. You must add your credentials before the first launch — without them the browser will not start.

### Step 1 — Proxy usernames (`proxies.json`)

Open:

```
~/.local/share/ember-browser/proxies.json
```

Replace each placeholder with the username proxy.market assigned to that country:

```json
{
  "ru": { "username": "AbCdEfGhIjKl" },
  "ge": { "username": "MnOpQrStUvWx" },
  "il": { "username": "YzAbCdEfGhIj" },
  "ae": { "username": "KlMnOpQrStUv" },
  "de": { "username": "WxYzAbCdEfGh" },
  "gb": { "username": "IjKlMnOpQrSt" },
  "tr": { "username": "UvWxYzAbCdEf" },
  "us": { "username": "GhIjKlMnOpQr" },
  "fr": { "username": "StUvWxYzAbCd" },
  "am": { "username": "EfGhIjKlMnOp" },
  "kr": { "username": "QrStUvWxYzAb" }
}
```

You only need entries for countries you actually use. Countries without credentials will not be available in the UI.

**Where to find usernames:** log in to proxy.market → dashboard → My Proxies. Each geo-location entry has its own username.

### Step 2 — Proxy password (`browser/proxy.py`)

Open:

```
~/.local/share/ember-browser/browser/proxy.py
```

Find line 19:

```python
PROXY_PASSWORD = "your_password_here"
```

Set it to your proxy.market account password. All country usernames share a single password.

---

## Updating

Re-run the installer — it will `git pull` the latest code without touching your credentials:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/MirTrudMike/BROWSER_Anon/master/install.sh)
```

`proxies.json` and `used_ips.json` are never overwritten during updates.

---

## Resetting used IPs

If the proxy pool feels exhausted, clear the used-IP history:

```bash
echo "[]" > ~/.local/share/ember-browser/used_ips.json
```

---

## Uninstalling

```bash
rm -rf ~/.local/share/ember-browser
rm -f  ~/.local/bin/ember-browser
rm -f  ~/.local/share/applications/ember-browser.desktop
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
```
