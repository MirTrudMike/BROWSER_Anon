"""
Ember — anonymous browser session management.
Design system: "The Kinetic Console" by Google Stitch.
"""

import asyncio

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QMessageBox,
    QScrollArea, QFrame, QApplication, QSizePolicy,
    QGraphicsDropShadowEffect, QStyledItemDelegate, QStyle,
)
from PyQt5.QtGui import (
    QColor, QPainter, QPainterPath, QBrush, QPen, QPalette, QFont,
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect, QSize

from .launcher import BrowserLauncher
from .profiles import ProfileConfig, STEALTH, COMPATIBILITY
from .logger import logger


# ── Colour tokens ─────────────────────────────────────────────────────────────
# All from the Stitch "Kinetic Console" design system.

_BG   = "#131313"   # surface / background
_SC   = "#201f1f"   # surface-container
_SCL  = "#1c1b1b"   # surface-container-low  (toggle row bg)
_SCH  = "#2a2a2a"   # surface-container-high (hover / toolbar)
_SCX  = "#353534"   # surface-container-highest
_SLO  = "#0e0e0e"   # surface-container-lowest (inputs / footer)
_ACC  = "#ff5722"   # primary-container / Ember orange
_ACCH = "#ff6e40"   # slightly lighter for hover feedback
_TXT  = "#e5e2e1"   # on-surface
_TXTS = "#ab8980"   # outline (secondary text)
_TXTO = "#5b4039"   # outline-variant (ghost borders)
_GRN  = "#13ff43"   # secondary-container (matrix green — status active)
_GRND = "#00e639"   # secondary-fixed-dim green
_ERRC = "#93000a"   # error-container (WARN badge background)
_ERRE = "#ffdad6"   # on-error-container (WARN badge text)
_TOFF = "#352a27"   # toggle OFF colour (outline-variant/40 blended)


# ── Country map ───────────────────────────────────────────────────────────────

_COUNTRIES: dict[str, str] = {
    "ru": "[RU]  RUSSIA",
    "ge": "[GE]  GEORGIA",
    "il": "[IL]  ISRAEL",
    "ae": "[AE]  UAE",
    "de": "[DE]  GERMANY",
    "gb": "[GB]  GREAT BRITAIN",
    "tr": "[TR]  TURKEY",
    "us": "[US]  USA",
    "fr": "[FR]  FRANCE",
    "kr": "[KR]  KOREA",
    "am": "[AM]  ARMENIA",
}


# ── Field metadata ────────────────────────────────────────────────────────────

_FIELDS: dict[str, dict] = {
    "base_masking": {
        "label": "KERNEL_BYPASS_MODE",
        "desc":  "removes webdriver/playwright markers",
        "crit":  True,
    },
    "webrtc": {
        "label": "WEB_RTC_LEAK_PREVENT",
        "desc":  "replaces real IPs in WebRTC SDP",
        "crit":  True,
    },
    "platform": {
        "label": "PLATFORM_SPOOF",
        "desc":  "navigator.platform must match UA os",
        "crit":  True,
    },
    "language": {
        "label": "LANGUAGE_MASK",
        "desc":  "navigator.language aligned to country",
        "crit":  True,
    },
    "hardware": {
        "label": "HW_CONCURRENCY_SPOOF",
        "desc":  "navigator.hardwareConcurrency, deviceMemory",
        "crit":  False,
    },
    "webgl": {
        "label": "VENDOR_ID_MASK",
        "desc":  "GPU vendor and renderer strings",
        "crit":  False,
    },
    "canvas": {
        "label": "CANVAS_NOISE_INJECT",
        "desc":  "toDataURL / getImageData pixel noise",
        "crit":  False,
    },
    "canvas_2d": {
        "label": "CANVAS_2D_NOISE",
        "desc":  "2D context fillText, getImageData noise",
        "crit":  False,
    },
    "audio": {
        "label": "AUDIO_CONTEXT_MASK",
        "desc":  "AudioBuffer channel floating-point noise",
        "crit":  False,
    },
    "fonts": {
        "label": "FONTS_ENUM_SPOOF",
        "desc":  "getComputedStyle fontFamily override",
        "crit":  False,
    },
    "battery": {
        "label": "BATTERY_API_EMUL",
        "desc":  "navigator.getBattery() emulation",
        "crit":  False,
    },
    "usb": {
        "label": "USB_HID_BLOCK",
        "desc":  "navigator.usb, hid — disabled",
        "crit":  False,
    },
    "plugins": {
        "label": "PLUGINS_MIME_SPOOF",
        "desc":  "navigator.plugins / mimeTypes list",
        "crit":  False,
    },
}

_GROUPS: list[tuple[str, list[str]]] = [
    ("01_CORE_SYSTEM",       ["base_masking", "webrtc", "platform", "language"]),
    ("02_HARDWARE_GPU",      ["hardware", "webgl"]),
    ("03_FINGERPRINT_NOISE", ["canvas", "canvas_2d", "audio", "fonts"]),
    ("04_API_EMULATION",     ["battery", "usb", "plugins"]),
]


# ── Custom widgets ────────────────────────────────────────────────────────────

class CountryDelegate(QStyledItemDelegate):
    """
    Renders flag emoji in colour by explicitly using Noto Color Emoji font
    for the regional-indicator characters, and a monospace font for the name.
    Solves the PyQt5-on-Linux B&W emoji rendering issue.
    """

    @staticmethod
    def _mono_font() -> QFont:
        f = QFont()
        f.setFamilies(["JetBrains Mono", "Fira Code", "Consolas", "monospace"])
        f.setPointSize(10)
        f.setWeight(QFont.Medium)
        return f

    def paint(self, painter, option, index):
        text = index.data(Qt.DisplayRole) or ""

        painter.save()
        is_sel = bool(option.state & QStyle.State_Selected)
        painter.fillRect(option.rect, QColor(_SCH if is_sel else _SLO))

        font = self._mono_font()
        painter.setFont(font)

        # Placeholder
        if text.startswith("—"):
            painter.setPen(QColor(_TXTS))
            painter.drawText(
                option.rect.adjusted(10, 0, -4, 0), Qt.AlignVCenter, text
            )
            painter.restore()
            return

        # Format: "[RU]  RUSSIA" — split on "]"
        code = ""
        name = text
        if text.startswith("["):
            close = text.find("]")
            if close > 0:
                code = text[:close + 1]        # "[RU]"
                name = text[close + 1:].strip()  # "RUSSIA"

        x = option.rect.x() + 10
        fm = painter.fontMetrics()

        # Code in accent colour
        if code:
            code_w = fm.horizontalAdvance(code)
            code_rect = QRect(x, option.rect.y(), code_w + 2, option.rect.height())
            painter.setPen(QColor(_ACC))
            painter.drawText(code_rect, Qt.AlignVCenter, code)
            x += code_w + 10

        # Name in primary text colour
        name_rect = QRect(x, option.rect.y(), option.rect.right() - x - 4,
                          option.rect.height())
        painter.setPen(QColor(_TXT))
        painter.drawText(name_rect, Qt.AlignVCenter, name)

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 38)


class DotGridWidget(QWidget):
    """
    Widget with a subtle dot-grid background texture.
    All content children are laid on top; they should be transparent
    unless they explicitly set their own background.
    """

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(_BG))
        p.setPen(QPen(QColor(_SCH), 1))
        step = 24
        for x in range(0, self.width() + step, step):
            for y in range(0, self.height() + step, step):
                p.drawPoint(x, y)
        p.end()


class FlatToggle(QWidget):
    """24 × 12 sharp-edged rectangle toggle — no rounded corners, no animation."""

    toggled = pyqtSignal(bool)
    W, H = 28, 14

    def __init__(self, checked: bool = True, parent=None):
        super().__init__(parent)
        self._checked = checked
        self.setFixedSize(self.W, self.H)
        self.setCursor(Qt.PointingHandCursor)

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, val: bool):
        if self._checked == val:
            return
        self._checked = val
        self.update()
        self.toggled.emit(val)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setChecked(not self._checked)

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(0, 0, self.W, self.H,
                   QBrush(QColor(_ACC if self._checked else _TOFF)))
        p.end()


class SegmentedControl(QWidget):
    """Three-option profile selector with Kinetic Console styling."""

    selectionChanged = pyqtSignal(int)
    _OPTS = ["STEALTH", "COMPAT", "DEBUG"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._idx = 0
        self._btns: list[QPushButton] = []

        lo = QHBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)

        for i, label in enumerate(self._OPTS):
            btn = QPushButton(label)
            btn.setFixedHeight(32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, i=i: self.select(i))
            self._btns.append(btn)
            lo.addWidget(btn)

        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(_SLO))
        self.setPalette(pal)
        self._refresh()

    def _style(self, active: bool) -> str:
        bg = _ACC if active else "transparent"
        fg = "#541200" if active else f"rgba(229,226,225,100)"
        return (
            f"QPushButton{{"
            f"background:{bg};color:{fg};border:none;border-radius:0;"
            f"font-family:'Space Grotesk','Ubuntu',sans-serif;"
            f"font-size:10px;font-weight:700;padding:0 8px;}}"
            f"QPushButton:hover{{background:{'#ff6e40' if active else _SCH};"
            f"color:{_TXT};}}"
        )

    def _refresh(self):
        for i, btn in enumerate(self._btns):
            btn.setStyleSheet(self._style(i == self._idx))

    def select(self, idx: int):
        if self._idx == idx:
            return
        self._idx = idx
        self._refresh()
        self.selectionChanged.emit(idx)

    def currentIndex(self) -> int:
        return self._idx


class ProfileHero(QWidget):
    """
    Shield icon displayed when Stealth or Compat profile is active.
    Shows the profile name and an orange shield on a dark tile.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._status_active = False
        self.setFixedSize(96, 96)

    def setStatusActive(self, val: bool):
        self._status_active = val
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        # Dark tile background
        p.fillRect(self.rect(), QColor(_SLO))

        # Shield shape
        cx   = float(self.width()) / 2
        top  = 16.0
        bot  = float(self.height()) - 14.0
        left = 16.0
        right = float(self.width()) - 16.0
        mid  = top + (bot - top) * 0.44

        shield = QPainterPath()
        shield.moveTo(cx, top)
        shield.lineTo(right, top + 14)
        shield.lineTo(right, mid)
        shield.cubicTo(right, bot - 8, cx + 14, bot - 2, cx, bot)
        shield.cubicTo(cx - 14, bot - 2, left, bot - 8, left, mid)
        shield.lineTo(left, top + 14)
        shield.closeSubpath()

        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(_ACC)))
        p.drawPath(shield)

        # Status dot: green if session active, dimmed otherwise
        dot_color = QColor(_GRN) if self._status_active else QColor(_TXTO)
        p.setBrush(QBrush(dot_color))
        p.drawRect(self.width() - 14, 6, 10, 10)

        p.end()


class ToggleRow(QWidget):
    """
    One row in the debug panel: label + optional WARN badge + flat toggle.
    Compact, monospace — matches Kinetic Console data-grid style.
    """

    def __init__(self, field_name: str, parent=None):
        super().__init__(parent)
        meta = _FIELDS[field_name]

        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(_SCL))
        self.setPalette(pal)
        self.setCursor(Qt.ArrowCursor)

        lo = QHBoxLayout(self)
        lo.setContentsMargins(12, 8, 12, 8)
        lo.setSpacing(8)

        # Left: label column
        col = QVBoxLayout()
        col.setSpacing(2)
        col.setContentsMargins(0, 0, 0, 0)

        lbl_row = QHBoxLayout()
        lbl_row.setSpacing(6)
        lbl_row.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(meta["label"])
        lbl.setStyleSheet(
            f"color:{_TXT};font-size:10px;font-weight:500;"
            f"font-family:'JetBrains Mono','Fira Code','Consolas',monospace;"
            f"background:transparent;"
        )
        lbl_row.addWidget(lbl)

        if meta["crit"]:
            badge = QLabel("WARN")
            badge.setStyleSheet(
                f"color:{_ERRE};background:{_ERRC};"
                f"font-size:8px;font-weight:700;"
                f"font-family:'JetBrains Mono','Consolas',monospace;"
                f"border-radius:0;padding:1px 4px;"
            )
            lbl_row.addWidget(badge)

        lbl_row.addStretch()
        col.addLayout(lbl_row)

        desc = QLabel(meta["desc"])
        desc.setStyleSheet(
            f"color:{_TXTS};font-size:9px;"
            f"font-family:'JetBrains Mono','Fira Code','Consolas',monospace;"
            f"background:transparent;"
        )
        col.addWidget(desc)

        lo.addLayout(col)

        # Right: toggle
        self.toggle = FlatToggle(checked=True)
        lo.addWidget(self.toggle, 0, Qt.AlignVCenter)

        if meta["crit"]:
            self.toggle.toggled.connect(self._on_crit)

    def _on_crit(self, checked: bool):
        if not checked:
            QMessageBox.warning(
                self, "WARN",
                "This is a core protection parameter.\n"
                "Disabling it may immediately expose your identity."
            )

    def isChecked(self) -> bool:
        return self.toggle.isChecked()

    def enterEvent(self, event):
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(_SCH))
        self.setPalette(pal)

    def leaveEvent(self, event):
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(_SCL))
        self.setPalette(pal)


class DebugPanel(QWidget):
    """
    Debug section: grouped toggle rows under section headers.
    Sits inside the scrollable content area.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: dict[str, ToggleRow] = {}

        lo = QVBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(16)

        for gname, fields in _GROUPS:
            lo.addLayout(self._group(gname, fields))

    def _group(self, name: str, fields: list[str]) -> QVBoxLayout:
        gl = QVBoxLayout()
        gl.setSpacing(0)
        gl.setContentsMargins(0, 0, 0, 0)

        # Header row: label + orange line
        hdr_lo = QHBoxLayout()
        hdr_lo.setSpacing(8)
        hdr_lo.setContentsMargins(0, 0, 0, 6)

        hdr_lbl = QLabel(name)
        hdr_lbl.setStyleSheet(
            f"color:{_ACC};font-size:9px;font-weight:700;"
            f"font-family:'JetBrains Mono','Consolas',monospace;"
            f"background:transparent;"
        )
        hdr_lo.addWidget(hdr_lbl)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFixedHeight(1)
        line.setAutoFillBackground(True)
        lpal = line.palette()
        # outline-variant at ~20% on _BG → dull brownish
        lpal.setColor(QPalette.Window, QColor("#241918"))
        line.setPalette(lpal)
        hdr_lo.addWidget(line)

        gl.addLayout(hdr_lo)

        # Toggle rows
        for fname in fields:
            row = ToggleRow(fname)
            self._rows[fname] = row
            gl.addWidget(row)

            # 1px gap between rows (space-y-px equivalent)
            spacer = QWidget()
            spacer.setFixedHeight(1)
            spacer.setAutoFillBackground(True)
            sp = spacer.palette()
            sp.setColor(QPalette.Window, QColor(_BG))
            spacer.setPalette(sp)
            gl.addWidget(spacer)

        return gl

    def get_profile(self) -> ProfileConfig:
        return ProfileConfig(**{f: r.isChecked() for f, r in self._rows.items()})


class GlowButton(QPushButton):
    """Launch button with orange drop-shadow glow on hover."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self._effect = QGraphicsDropShadowEffect()
        self._effect.setColor(QColor(_ACC))
        self._effect.setBlurRadius(22)
        self._effect.setOffset(0, 0)
        self._effect.setEnabled(False)
        self.setGraphicsEffect(self._effect)

    def enterEvent(self, event):
        if self.isEnabled():
            self._effect.setEnabled(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._effect.setEnabled(False)
        super().leaveEvent(event)


# ── Main window ───────────────────────────────────────────────────────────────

class BrowserLauncherApp(QMainWindow):
    """Ember — main application window."""

    _VERSION = "V1.0.4"

    def __init__(self, launcher: BrowserLauncher):
        try:
            logger.info("Initializing Ember")
            super().__init__()

            self._launcher = launcher
            self._loop     = asyncio.new_event_loop()

            available = launcher.load_available_countries()
            self._countries = [_COUNTRIES[c] for c in available if c in _COUNTRIES]
            self._code_of   = {v: k for k, v in _COUNTRIES.items()}

            self.setWindowTitle("Ember")
            self.setFixedWidth(380)

            self._apply_palette()
            self._build_ui()
            self._apply_style()
            self.adjustSize()

            logger.info("Ember initialized")
        except Exception as e:
            logger.exception(e, "Failed to initialize Ember")
            raise

    # ── Palette & theme ───────────────────────────────────────────────────────

    def _apply_palette(self):
        app = QApplication.instance()
        app.setStyle("Fusion")
        pal = app.palette()
        pal.setColor(QPalette.Window,          QColor(_BG))
        pal.setColor(QPalette.WindowText,      QColor(_TXT))
        pal.setColor(QPalette.Base,            QColor(_SLO))
        pal.setColor(QPalette.AlternateBase,   QColor(_SC))
        pal.setColor(QPalette.Text,            QColor(_TXT))
        pal.setColor(QPalette.BrightText,      QColor(_TXT))
        pal.setColor(QPalette.Button,          QColor(_SCH))
        pal.setColor(QPalette.ButtonText,      QColor(_TXT))
        pal.setColor(QPalette.Highlight,       QColor(_ACC))
        pal.setColor(QPalette.HighlightedText, QColor("#541200"))
        pal.setColor(QPalette.ToolTipBase,     QColor(_SCX))
        pal.setColor(QPalette.ToolTipText,     QColor(_TXT))
        pal.setColor(QPalette.Mid,             QColor(_TXTO))
        pal.setColor(QPalette.Dark,            QColor(_SLO))
        pal.setColor(QPalette.Shadow,          QColor("#000000"))
        pal.setColor(QPalette.Disabled, QPalette.WindowText, QColor(_TXTS))
        pal.setColor(QPalette.Disabled, QPalette.Text,       QColor(_TXTS))
        pal.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(_TXTS))
        app.setPalette(pal)

    def _apply_style(self):
        mono  = "'JetBrains Mono','Fira Code','Source Code Pro','Consolas',monospace"
        heads = "'Space Grotesk','Ubuntu','Segoe UI',sans-serif"

        self.setStyleSheet(f"""
            /* ── ComboBox ── */
            QComboBox {{
                background:{_SLO};
                color:rgba(229,226,225,100);
                border:1px solid rgba(91,64,57,50);
                border-radius:0;
                padding:0 12px;
                font-family:{mono};
                font-size:11px;
                font-weight:500;
            }}
            QComboBox:focus {{
                border-bottom:1px solid {_ACC};
                color:{_TXT};
            }}
            QComboBox::drop-down {{
                subcontrol-origin:padding;
                subcontrol-position:right center;
                width:28px; border:none;
            }}
            QComboBox QAbstractItemView {{
                background:{_SLO};
                color:{_TXT};
                border:1px solid rgba(91,64,57,50);
                border-radius:0;
                selection-background-color:{_SCH};
                selection-color:{_ACC};
                font-family:{mono};
                font-size:11px;
                font-weight:600;
                padding:2px 0;
                outline:none;
            }}

            /* ── Launch button ── */
            QPushButton#launch {{
                background:{_ACC};
                color:#541200;
                border:none;
                border-radius:0;
                font-family:{heads};
                font-size:13px;
                font-weight:700;
            }}
            QPushButton#launch:hover   {{ background:{_ACCH}; }}
            QPushButton#launch:pressed {{ background:#cc3a00; }}
            QPushButton#launch:disabled {{
                background:rgba(91,64,57,50);
                color:rgba(229,226,225,50);
            }}

            /* ── MessageBox ── */
            QMessageBox {{ background:{_SC}; }}
            QMessageBox QLabel {{ color:{_TXT}; }}
            QMessageBox QPushButton {{
                background:{_SCH}; color:{_TXT};
                border:1px solid rgba(91,64,57,80);
                border-radius:0; min-width:64px;
                padding:6px 14px; font-size:11px;
            }}
            QMessageBox QPushButton:hover {{
                background:{_ACC}; color:#541200;
                border-color:{_ACC};
            }}

            /* ── ScrollBar ── */
            QScrollBar:vertical {{
                background:{_SLO}; width:4px; margin:0;
            }}
            QScrollBar::handle:vertical {{
                background:{_TXTO}; min-height:20px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{ height:0; }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{ background:none; }}
        """)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root_widget = QWidget()
        self.setCentralWidget(root_widget)

        root = QVBoxLayout(root_widget)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_header())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}")

        self._content = DotGridWidget()
        self._content_lo = QVBoxLayout(self._content)
        self._content_lo.setContentsMargins(20, 20, 20, 20)
        self._content_lo.setSpacing(20)

        # Hero (Stealth / Compat)
        self._hero_block = self._make_hero()
        self._content_lo.addWidget(self._hero_block, 0, Qt.AlignHCenter)

        # Country
        self._content_lo.addLayout(self._make_country_section())

        # Profile selector
        self._content_lo.addLayout(self._make_profile_section())

        # Debug panel (hidden by default)
        self._debug_header_lbl = QLabel("DEBUG_ENVIRONMENT_DETECTION")
        self._debug_header_lbl.setStyleSheet(
            f"color:{_ACC};font-size:9px;font-weight:700;"
            f"font-family:'JetBrains Mono','Consolas',monospace;"
            f"background:transparent;"
        )
        self._debug_header_lbl.setVisible(False)
        self._content_lo.addWidget(self._debug_header_lbl)

        self._debug_panel = DebugPanel()
        self._debug_panel.setVisible(False)
        self._content_lo.addWidget(self._debug_panel)

        self._content_lo.addStretch()

        scroll.setWidget(self._content)
        root.addWidget(scroll, 1)
        root.addWidget(self._make_footer())

    def _make_header(self) -> QWidget:
        w = QWidget()
        w.setFixedHeight(48)
        w.setAutoFillBackground(True)
        pal = w.palette()
        pal.setColor(QPalette.Window, QColor(_BG))
        w.setPalette(pal)

        lo = QHBoxLayout(w)
        lo.setContentsMargins(16, 0, 16, 0)
        lo.setSpacing(8)

        # Icon + title
        icon = QLabel("◈")
        icon.setStyleSheet(f"color:{_ACC};font-size:16px;background:transparent;")
        lo.addWidget(icon)

        title = QLabel("EMBER")
        title.setStyleSheet(
            f"color:{_ACC};font-size:16px;font-weight:700;"
            f"font-family:'Space Grotesk','Ubuntu',sans-serif;"
            f"background:transparent;"
        )
        lo.addWidget(title)
        lo.addStretch()

        # Status badge (updates with profile)
        self._status_badge = QLabel("STEALTH_ACTIVE")
        self._status_badge.setStyleSheet(
            f"color:{_ACC};font-size:9px;font-weight:700;"
            f"font-family:'JetBrains Mono','Consolas',monospace;"
            f"background:transparent;"
        )
        lo.addWidget(self._status_badge)

        # Version
        ver = QLabel(self._VERSION)
        ver.setStyleSheet(
            f"color:rgba(229,226,225,60);font-size:9px;"
            f"font-family:'JetBrains Mono','Consolas',monospace;"
            f"background:transparent;margin-left:10px;"
        )
        lo.addWidget(ver)

        # Left accent bar
        accent = QWidget(w)
        accent.setGeometry(0, 0, 2, 48)
        accent.setAutoFillBackground(True)
        apal = accent.palette()
        apal.setColor(QPalette.Window, QColor(_ACC))
        accent.setPalette(apal)

        return w

    def _make_hero(self) -> QWidget:
        """Shield icon + profile name block — shown in Stealth/Compat modes."""
        block = QWidget()
        block.setStyleSheet("background:transparent;")
        lo = QVBoxLayout(block)
        lo.setContentsMargins(0, 8, 0, 0)
        lo.setSpacing(10)
        lo.setAlignment(Qt.AlignHCenter)

        self._shield = ProfileHero()
        lo.addWidget(self._shield, 0, Qt.AlignHCenter)

        sub = QLabel("PROTECTION_PROFILE")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(
            f"color:{_TXTS};font-size:9px;letter-spacing:2px;"
            f"font-family:'JetBrains Mono','Consolas',monospace;"
            f"background:transparent;"
        )
        lo.addWidget(sub)

        self._profile_name_lbl = QLabel("STEALTH")
        self._profile_name_lbl.setAlignment(Qt.AlignCenter)
        self._profile_name_lbl.setStyleSheet(
            f"color:{_TXT};font-size:22px;font-weight:700;"
            f"font-family:'Space Grotesk','Ubuntu',sans-serif;"
            f"background:transparent;"
        )
        lo.addWidget(self._profile_name_lbl)

        return block

    def _make_country_section(self) -> QVBoxLayout:
        lo = QVBoxLayout()
        lo.setSpacing(6)

        lo.addWidget(self._dot_label("NETWORK_NODE"))

        self._country_combo = QComboBox()
        self._country_combo.setFixedHeight(40)
        self._country_combo.addItem("— SELECT COUNTRY —")
        for name in self._countries:
            self._country_combo.addItem(name)

        # Grey out placeholder
        model = self._country_combo.model()
        placeholder = model.item(0)
        placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsSelectable & ~Qt.ItemIsEnabled)

        display_font = QFont()
        display_font.setFamilies(["JetBrains Mono", "Fira Code", "Consolas", "monospace"])
        display_font.setPointSize(11)
        self._country_combo.setFont(display_font)

        # Delegate renders [XX] code in accent colour in the open dropdown
        self._country_combo.setItemDelegate(CountryDelegate(self._country_combo))

        self._country_combo.currentIndexChanged.connect(self._on_country)
        lo.addWidget(self._country_combo)

        return lo

    def _make_profile_section(self) -> QVBoxLayout:
        lo = QVBoxLayout()
        lo.setSpacing(6)

        lo.addWidget(self._dot_label("PROTECTION_PROFILE"))

        # Wrap segmented control in a slightly-elevated container
        container = QWidget()
        container.setAutoFillBackground(True)
        cp = container.palette()
        cp.setColor(QPalette.Window, QColor(_SLO))
        container.setPalette(cp)

        clo = QHBoxLayout(container)
        clo.setContentsMargins(1, 1, 1, 1)
        clo.setSpacing(0)

        self._profile_ctrl = SegmentedControl()
        self._profile_ctrl.selectionChanged.connect(self._on_profile)
        clo.addWidget(self._profile_ctrl)

        lo.addWidget(container)
        return lo

    def _make_footer(self) -> QWidget:
        footer = QWidget()
        footer.setAutoFillBackground(True)
        fp = footer.palette()
        fp.setColor(QPalette.Window, QColor(_SLO))
        footer.setPalette(fp)

        lo = QVBoxLayout(footer)
        lo.setContentsMargins(16, 12, 16, 12)
        lo.setSpacing(10)

        self._launch_btn = GlowButton("LAUNCH")
        self._launch_btn.setObjectName("launch")
        self._launch_btn.setFixedHeight(52)
        self._launch_btn.setEnabled(False)
        self._launch_btn.setCursor(Qt.PointingHandCursor)
        self._launch_btn.clicked.connect(self._on_launch)
        lo.addWidget(self._launch_btn)

        # Status row
        status_lo = QHBoxLayout()
        status_lo.setSpacing(6)

        self._status_dot = QLabel("●")
        self._status_dot.setStyleSheet(
            f"color:{_TXTO};font-size:8px;background:transparent;"
        )
        status_lo.addWidget(self._status_dot)

        self._status_lbl = QLabel("IDLE")
        self._status_lbl.setStyleSheet(
            f"color:rgba(229,226,225,60);font-size:9px;"
            f"font-family:'JetBrains Mono','Consolas',monospace;"
            f"background:transparent;"
        )
        status_lo.addWidget(self._status_lbl)
        status_lo.addStretch()

        self._session_id = QLabel("ID: EB-0000-X")
        self._session_id.setStyleSheet(
            f"color:rgba(229,226,225,30);font-size:9px;"
            f"font-family:'JetBrains Mono','Consolas',monospace;"
            f"background:transparent;"
        )
        status_lo.addWidget(self._session_id)

        lo.addLayout(status_lo)
        return footer

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _dot_label(self, text: str) -> QWidget:
        """Section label with small orange square dot prefix."""
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        lo = QHBoxLayout(w)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(6)

        dot = QLabel()
        dot.setFixedSize(6, 6)
        dot.setAutoFillBackground(True)
        dp = dot.palette()
        dp.setColor(QPalette.Window, QColor(_ACC))
        dot.setPalette(dp)
        lo.addWidget(dot, 0, Qt.AlignVCenter)

        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color:rgba(229,226,225,120);font-size:9px;font-weight:700;"
            f"font-family:'JetBrains Mono','Consolas',monospace;"
            f"background:transparent;"
        )
        lo.addWidget(lbl)
        lo.addStretch()
        return w

    # ── Event handlers ────────────────────────────────────────────────────────

    def _on_country(self, idx: int):
        self._launch_btn.setEnabled(idx > 0)

    def _on_profile(self, idx: int):
        names   = ["STEALTH", "COMPAT", "DEBUG"]
        badges  = ["STEALTH_ACTIVE", "COMPAT_ACTIVE", "DEBUG_MODE"]
        is_debug = idx == 2

        self._hero_block.setVisible(not is_debug)
        self._debug_header_lbl.setVisible(is_debug)
        self._debug_panel.setVisible(is_debug)

        if not is_debug:
            self._profile_name_lbl.setText(names[idx])

        self._status_badge.setText(badges[idx])
        self.adjustSize()

    def _get_profile(self) -> ProfileConfig:
        idx = self._profile_ctrl.currentIndex()
        if idx == 0:
            return STEALTH
        if idx == 1:
            return COMPATIBILITY
        return self._debug_panel.get_profile()

    def _on_launch(self):
        display = self._country_combo.currentText()
        code = self._code_of.get(display)
        if not code:
            return
        asyncio.run_coroutine_threadsafe(self._do_launch(code), self._loop)

    # ── Async ─────────────────────────────────────────────────────────────────

    async def _do_launch(self, country: str):
        try:
            self._status_lbl.setText("ESTABLISHING_TUNNEL...")
            self._status_dot.setStyleSheet(
                f"color:{_ACC};font-size:8px;background:transparent;"
            )
            logger.info(f"Launching session: country={country}")

            await self._launcher.close()
            browser, config = await self._launcher.start(
                country, profile=self._get_profile()
            )

            if not browser or not config:
                self._set_idle()
                QMessageBox.critical(self, "Ember", "Failed to start browser")
                return

            pi = config.get("proxy_info", {})
            country_up = pi.get("country", "").upper()
            city       = pi.get("city", "")
            os_name    = config.get("system", "")

            self._status_dot.setStyleSheet(
                f"color:{_GRN};font-size:8px;background:transparent;"
            )
            self._status_lbl.setText(f"SESSION_ACTIVE  {country_up} / {city} / {os_name}")
            self._status_lbl.setStyleSheet(
                f"color:{_GRND};font-size:9px;"
                f"font-family:'JetBrains Mono','Consolas',monospace;"
                f"background:transparent;"
            )
            self._shield.setStatusActive(True)
            self._launch_btn.setText("RELAUNCH")

        except Exception as e:
            logger.exception(e, "Launch failed")
            self._set_idle()
            QMessageBox.critical(self, "Ember — Error", str(e))

    def _set_idle(self):
        self._status_dot.setStyleSheet(
            f"color:{_TXTO};font-size:8px;background:transparent;"
        )
        self._status_lbl.setText("IDLE")
        self._status_lbl.setStyleSheet(
            f"color:rgba(229,226,225,60);font-size:9px;"
            f"font-family:'JetBrains Mono','Consolas',monospace;"
            f"background:transparent;"
        )
        self._shield.setStatusActive(False)
        self._launch_btn.setText("LAUNCH")

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        try:
            asyncio.run_coroutine_threadsafe(self._launcher.close(), self._loop)
        except Exception:
            pass
        event.accept()
