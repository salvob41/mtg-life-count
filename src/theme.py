import flet as ft

STARTING_LIFE = 20
DEBOUNCE_SECONDS = 1.5

# ── Palette ──────────────────────────────────────────────────────
BG = "#0B1120"
SURFACE = "#131C2E"
ELEVATED = "#1C2A42"
BORDER = "#2E3F5C"
BORDER_SUBTLE = "#1E2D48"

TEXT = "#F0F4FF"
TEXT_DIM = "#8B9DC3"
TEXT_FAINT = "#5A6B8A"

# Player accents
P1_ACCENT = "#FFB800"
P1_SURFACE = "#1A1710"
P1_BTN = "#262010"

P2_ACCENT = "#00E5FF"
P2_SURFACE = "#0C1520"
P2_BTN = "#0E1E2C"

DANGER = "#FF4D6A"

THEMES = {
    1: {"accent": P1_ACCENT, "surface": P1_SURFACE, "btn": P1_BTN},
    2: {"accent": P2_ACCENT, "surface": P2_SURFACE, "btn": P2_BTN},
}

CENTER = ft.Alignment(0, 0)
