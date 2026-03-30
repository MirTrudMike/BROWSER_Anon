#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  Ember Browser — Installer
#  Supports: Fedora, RHEL, Debian, Ubuntu
#  Usage: bash <(curl -fsSL https://raw.githubusercontent.com/MirTrudMike/BROWSER_Anon/master/install.sh)
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

REPO_URL="https://github.com/MirTrudMike/BROWSER_Anon.git"
INSTALL_DIR="${HOME}/.local/share/ember-browser"
BIN_LINK="${HOME}/.local/bin/ember-browser"
DESKTOP_FILE="${HOME}/.local/share/applications/ember-browser.desktop"

# ── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
step()  { echo -e "\n${CYAN}${BOLD}──▶ $*${NC}"; }
die()   { echo -e "${RED}[✗] ERROR: $*${NC}" >&2; exit 1; }

# ── Detect package manager ────────────────────────────────────────────────────
detect_distro() {
    if command -v dnf &>/dev/null; then
        PKG_MGR="dnf"
    elif command -v apt-get &>/dev/null; then
        PKG_MGR="apt"
    else
        PKG_MGR="unknown"
        warn "Unknown package manager. Skipping system dependency installation."
        warn "Make sure you have: git, python3, python3-pip, python3-venv"
        warn "and Qt5/PyQt5 system libraries installed."
    fi
}

# ── System dependencies ───────────────────────────────────────────────────────
install_system_deps() {
    step "Installing system dependencies"

    if [[ "${PKG_MGR}" == "dnf" ]]; then
        info "Detected Fedora/RHEL — using dnf"
        sudo dnf install -y \
            git \
            python3 \
            python3-pip \
            python3-virtualenv \
            python3-devel \
            gcc \
            libxcb \
            libxkbcommon \
            libxkbcommon-x11 \
            xcb-util-wm \
            xcb-util-keysyms \
            xcb-util-image \
            xcb-util-renderutil \
            xcb-util-cursor \
            mesa-libGL \
            mesa-libEGL \
            nss \
            nspr \
            at-spi2-atk \
            at-spi2-core \
            cups-libs \
            gtk3 \
            alsa-lib \
            pango \
            cairo \
            glib2 \
            dbus-libs \
            libdrm \
            libgbm 2>/dev/null || true
        info "System packages installed"

    elif [[ "${PKG_MGR}" == "apt" ]]; then
        info "Detected Debian/Ubuntu — using apt"
        sudo apt-get update -qq
        sudo apt-get install -y \
            git \
            python3 \
            python3-pip \
            python3-venv \
            python3-dev \
            build-essential \
            libxcb-xinerama0 \
            libxkbcommon-x11-0 \
            libxcb-cursor0 \
            libgl1 \
            libnss3 \
            libnspr4 \
            libatk1.0-0 \
            libatk-bridge2.0-0 \
            libcups2 \
            libgtk-3-0 \
            libasound2 \
            libpangocairo-1.0-0 \
            libcairo-gobject2 \
            libgbm1 \
            libdrm2 \
            libxss1 2>/dev/null || true
        info "System packages installed"
    fi
}

# ── Clone / update ────────────────────────────────────────────────────────────
clone_or_update() {
    step "Setting up application files"

    if [[ -d "${INSTALL_DIR}/.git" ]]; then
        info "Existing installation found — updating..."
        git -C "${INSTALL_DIR}" pull --ff-only
    else
        info "Cloning repository to ${INSTALL_DIR}"
        mkdir -p "$(dirname "${INSTALL_DIR}")"
        git clone "${REPO_URL}" "${INSTALL_DIR}"
    fi
    info "Repository ready"
}

# ── Python venv & dependencies ────────────────────────────────────────────────
setup_venv() {
    step "Setting up Python environment"

    local python_bin
    python_bin=$(command -v python3) || die "python3 not found"

    info "Creating virtual environment with ${python_bin}"
    "${python_bin}" -m venv "${INSTALL_DIR}/.venv"

    local pip="${INSTALL_DIR}/.venv/bin/pip"
    local playwright="${INSTALL_DIR}/.venv/bin/playwright"

    info "Upgrading pip..."
    "${pip}" install --upgrade pip --quiet

    info "Installing Python dependencies (this may take a minute)..."
    "${pip}" install -r "${INSTALL_DIR}/requirements.txt" --quiet
    info "Python dependencies installed"

    info "Downloading Playwright Chromium browser (this may take several minutes)..."
    "${playwright}" install chromium

    info "Installing Playwright system dependencies..."
    sudo "${playwright}" install-deps chromium 2>/dev/null \
        || warn "playwright install-deps failed — you can run it manually: sudo ${playwright} install-deps chromium"

    info "Playwright Chromium ready"
}

# ── Template config files ─────────────────────────────────────────────────────
create_templates() {
    step "Creating configuration files"

    # proxies.json — only if missing (never overwrite user's credentials)
    if [[ ! -f "${INSTALL_DIR}/proxies.json" ]]; then
        cat > "${INSTALL_DIR}/proxies.json" << 'PROXIES_EOF'
{
  "ru": { "username": "YOUR_RU_USERNAME" },
  "ge": { "username": "YOUR_GE_USERNAME" },
  "il": { "username": "YOUR_IL_USERNAME" },
  "ae": { "username": "YOUR_AE_USERNAME" },
  "de": { "username": "YOUR_DE_USERNAME" },
  "gb": { "username": "YOUR_GB_USERNAME" },
  "tr": { "username": "YOUR_TR_USERNAME" },
  "us": { "username": "YOUR_US_USERNAME" },
  "fr": { "username": "YOUR_FR_USERNAME" },
  "am": { "username": "YOUR_AM_USERNAME" },
  "kr": { "username": "YOUR_KR_USERNAME" }
}
PROXIES_EOF
        warn "proxies.json created as template — fill in your credentials before first launch"
    else
        info "proxies.json already exists — skipping"
    fi

    # used_ips.json — empty list (safe to recreate if missing)
    if [[ ! -f "${INSTALL_DIR}/used_ips.json" ]]; then
        echo "[]" > "${INSTALL_DIR}/used_ips.json"
        info "used_ips.json created"
    fi

    # logs directory
    mkdir -p "${INSTALL_DIR}/logs"
    info "Logs directory ready"
}

# ── Launcher script ───────────────────────────────────────────────────────────
create_launcher() {
    step "Installing launcher script"

    mkdir -p "$(dirname "${BIN_LINK}")"

    cat > "${BIN_LINK}" << LAUNCHER_EOF
#!/usr/bin/env bash
# Ember Browser launcher — auto-generated by install.sh
cd "${INSTALL_DIR}"
source "${INSTALL_DIR}/.venv/bin/activate"
exec python "${INSTALL_DIR}/main.py" "\$@"
LAUNCHER_EOF

    chmod +x "${BIN_LINK}"
    info "Launcher created at ${BIN_LINK}"

    # Offer to add ~/.local/bin to PATH if not already there
    if [[ ":${PATH}:" != *":${HOME}/.local/bin:"* ]]; then
        warn "~/.local/bin is not in your PATH"
        warn "Add it to your shell profile:"
        echo ""
        echo "    echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
        echo "    source ~/.bashrc"
        echo ""
    fi
}

# ── Desktop entry (.desktop file) ────────────────────────────────────────────
create_desktop_file() {
    step "Installing desktop entry"

    mkdir -p "$(dirname "${DESKTOP_FILE}")"

    cat > "${DESKTOP_FILE}" << DESKTOP_EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Ember Browser
GenericName=Anonymous Browser Launcher
Comment=Launch anonymous browser sessions with proxy and fingerprint masking
Exec=${BIN_LINK}
Icon=${INSTALL_DIR}/icon.png
Terminal=false
Categories=Network;WebBrowser;
Keywords=browser;proxy;anonymous;privacy;ember;
StartupNotify=true
StartupWMClass=ember-browser
DESKTOP_EOF

    # Refresh desktop database so the app appears in menus immediately
    if command -v update-desktop-database &>/dev/null; then
        update-desktop-database "${HOME}/.local/share/applications/" 2>/dev/null || true
    fi

    # Refresh icon cache (Fedora / GTK)
    if command -v gtk-update-icon-cache &>/dev/null; then
        gtk-update-icon-cache -f "${HOME}/.local/share/icons/" 2>/dev/null || true
    fi

    info "Desktop entry installed at ${DESKTOP_FILE}"
}

# ── Post-install summary ──────────────────────────────────────────────────────
print_summary() {
    echo ""
    echo -e "${BOLD}${GREEN}═══════════════════════════════════════════${NC}"
    echo -e "${BOLD}${GREEN}   Ember Browser installed successfully!   ${NC}"
    echo -e "${BOLD}${GREEN}═══════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${BOLD}Launch from terminal:${NC}   ember-browser"
    echo -e "  ${BOLD}Launch from desktop:${NC}    Applications → Ember Browser"
    echo -e "  ${BOLD}Installation path:${NC}      ${INSTALL_DIR}"
    echo ""
    echo -e "${YELLOW}${BOLD}  ⚠ Before first launch — configure your proxies:${NC}"
    echo ""
    echo -e "  1. Open:  ${CYAN}${INSTALL_DIR}/proxies.json${NC}"
    echo -e "     Fill in proxy usernames for each country (from proxy.market)"
    echo ""
    echo -e "  2. Open:  ${CYAN}${INSTALL_DIR}/browser/proxy.py${NC}  (line 19)"
    echo -e "     Set your proxy password:  PROXY_PASSWORD = \"your_password\""
    echo ""
    echo -e "  See README.md for full configuration instructions."
    echo ""
}

# ── Entry point ───────────────────────────────────────────────────────────────
main() {
    echo ""
    echo -e "${BOLD}${CYAN}"
    echo "  ╔═════════════════════════════════════╗"
    echo "  ║        Ember Browser Installer      ║"
    echo "  ╚═════════════════════════════════════╝"
    echo -e "${NC}"

    detect_distro
    install_system_deps
    clone_or_update
    setup_venv
    create_templates
    create_launcher
    create_desktop_file
    print_summary
}

main "$@"
