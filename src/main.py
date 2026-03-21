import asyncio
import os
from datetime import datetime

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

# Player accents — blazing gold vs neon cyan
P1_ACCENT = "#FFB800"   # blazing gold
P1_SURFACE = "#1A1710"  # dark gold tint
P1_BTN = "#262010"      # warm gold button
P1_STRIKE = "#FF9500"   # orange-gold strikethrough

P2_ACCENT = "#00E5FF"   # neon cyan
P2_SURFACE = "#0C1520"  # dark cyan tint
P2_BTN = "#0E1E2C"      # cool cyan button
P2_STRIKE = "#00B8D4"   # deep cyan strikethrough

DANGER = "#FF4D6A"

THEMES = {
    1: {
        "accent": P1_ACCENT, "surface": P1_SURFACE,
        "btn": P1_BTN, "strike": P1_STRIKE,
    },
    2: {
        "accent": P2_ACCENT, "surface": P2_SURFACE,
        "btn": P2_BTN, "strike": P2_STRIKE,
    },
}

CENTER = ft.Alignment(0, 0)


class PlayerPanel(ft.Container):
    def __init__(self, player_number: int, get_turn, get_active,
                 default_name=None, flipped=False):
        super().__init__()
        self.player_number = player_number
        self.flipped = flipped
        self.t = THEMES[player_number]
        self.get_turn = get_turn
        self.get_active = get_active
        self.player_name = default_name or f"Player {player_number}"
        self.life = STARTING_LIFE
        self.pending_delta = 0
        self.history: list[dict] = []
        self.land_drops = 0
        self._debounce_task = None

        self.life_display = ft.Text(
            str(self.life), size=84, weight=ft.FontWeight.W_900,
            color=TEXT, text_align=ft.TextAlign.CENTER,
        )
        self.pending_display = ft.Text(
            "", size=20, weight=ft.FontWeight.BOLD,
            color=self.t["accent"], text_align=ft.TextAlign.LEFT, opacity=0,
            width=50,
        )
        self.history_row = ft.Row(
            alignment=ft.MainAxisAlignment.START,
            spacing=6, scroll=ft.ScrollMode.AUTO,
            auto_scroll=True,
        )
        self.land_display = ft.Text(
            "0", size=15, weight=ft.FontWeight.BOLD, color=TEXT,
            text_align=ft.TextAlign.CENTER,
        )
        self.player_label = ft.Text(
            self.player_name.upper(), size=11, weight=ft.FontWeight.BOLD,
            color=TEXT_DIM,
        )
        self.name_field = ft.TextField(
            value=self.player_name, text_size=12, color=TEXT,
            bgcolor=ELEVATED, border_color=self.t["accent"],
            content_padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            text_align=ft.TextAlign.CENTER,
            on_submit=lambda e: self._finish_rename(),
            on_blur=lambda e: self._finish_rename(),
            visible=False, width=140, height=34,
        )
        self._build()

    # ── Rename ───────────────────────────────────────────────────
    def _start_rename(self, e=None):
        self.name_field.value = self.player_name
        self.name_field.visible = True
        self.player_label.visible = False
        self.name_field.update()
        self.player_label.update()
        self.name_field.focus()

    def _finish_rename(self):
        new_name = (self.name_field.value or "").strip()
        if new_name:
            self.player_name = new_name
        self.player_label.value = self.player_name.upper()
        self.name_field.visible = False
        self.player_label.visible = True
        self.player_label.update()
        self.name_field.update()

    def get_short_name(self) -> str:
        return self.player_name

    # ── Layout ───────────────────────────────────────────────────
    def _build(self):
        minus5 = self._make_life_btn("-5", -5, small=True)
        minus1 = self._make_life_btn("-1", -1, small=False)
        plus1 = self._make_life_btn("+1", +1, small=False)
        plus5 = self._make_life_btn("+5", +5, small=True)

        life_buttons = ft.Row(
            [minus5, minus1, plus1, plus5],
            alignment=ft.MainAxisAlignment.CENTER, spacing=10,
        )

        life_row = ft.Row(
            [ft.Container(width=50), self.life_display, self.pending_display],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.END, spacing=2,
        )
        life_area = ft.Stack(
            [
                ft.Container(content=life_row, alignment=CENTER, expand=True),
                ft.Row(
                    [
                        ft.Container(expand=True, on_click=lambda e: self._on_life_tap(-1)),
                        ft.Container(expand=True, on_click=lambda e: self._on_life_tap(+1)),
                    ],
                    expand=True, spacing=0,
                ),
            ],
            expand=True,
        )

        # Land drops
        land_label = ft.Text("LANDS", size=9, color=TEXT_FAINT)
        land_row = ft.Row(
            [
                land_label,
                self._make_small_btn("-", self._land_minus),
                self.land_display,
                self._make_small_btn("+", self._land_plus),
                ft.Container(width=6),
                self._make_small_btn("↺", self._land_reset),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=5,
        )

        # Centered name header
        label_btn = ft.Container(
            content=self.player_label,
            on_click=self._start_rename, ink=True, border_radius=6,
            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
        )
        # Thin accent line under name
        accent_bar = ft.Container(
            width=24, height=2, bgcolor=self.t["accent"], border_radius=1,
        )
        header = ft.Column(
            [
                ft.Row([label_btn, self.name_field],
                       alignment=ft.MainAxisAlignment.CENTER, spacing=0),
                accent_bar,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3,
        )

        history_container = ft.Container(
            content=self.history_row, height=46,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        elements = [
            header,
            history_container,
            life_area,
            life_buttons,
            ft.Container(height=4),
            land_row,
        ]
        if self.flipped:
            elements = list(reversed(elements))

        inner = ft.Column(
            elements, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True, spacing=4,
        )

        if self.flipped:
            self.content = ft.Container(
                content=inner, rotate=ft.Rotate(angle=3.14159), expand=True,
            )
        else:
            self.content = inner

        self.bgcolor = self.t["surface"]
        self.border_radius = 20
        self.border = ft.Border.all(1, BORDER_SUBTLE)
        self.padding = ft.Padding.symmetric(horizontal=14, vertical=10)
        self.expand = True

    def set_flipped(self, flipped: bool):
        self.flipped = flipped
        self._build()
        self.update()

    def set_active(self, is_active: bool):
        if is_active:
            self.border = ft.Border.all(1.5, self.t["accent"])
        else:
            self.border = ft.Border.all(1, BORDER_SUBTLE)
        self.update()

    def _make_life_btn(self, label: str, delta: int, small: bool) -> ft.Container:
        w = 52 if small else 70
        h = 40 if small else 46
        sz = 14 if small else 18
        return ft.Container(
            content=ft.Text(
                label, size=sz, weight=ft.FontWeight.W_600,
                color=TEXT if not small else TEXT_DIM,
                text_align=ft.TextAlign.CENTER,
            ),
            width=w, height=h, bgcolor=self.t["btn"], border_radius=12,
            border=ft.Border.all(1, BORDER),
            alignment=CENTER,
            on_click=lambda e, d=delta: self._on_life_tap(d), ink=True,
        )

    def _make_small_btn(self, label: str, handler) -> ft.Container:
        return ft.Container(
            content=ft.Text(
                label, size=12, weight=ft.FontWeight.BOLD,
                color=TEXT_DIM, text_align=ft.TextAlign.CENTER,
            ),
            width=26, height=24, bgcolor=ELEVATED, border_radius=6,
            border=ft.Border.all(1, BORDER_SUBTLE),
            alignment=CENTER, on_click=lambda e: handler(), ink=True,
        )

    # ── Life logic ───────────────────────────────────────────────
    def _on_life_tap(self, delta: int):
        self.pending_delta += delta
        sign = "+" if self.pending_delta > 0 else ""
        self.pending_display.value = (
            f"{sign}{self.pending_delta}" if self.pending_delta != 0 else ""
        )
        self.pending_display.opacity = 1 if self.pending_delta != 0 else 0
        self.life_display.value = str(self.life + self.pending_delta)
        self.life_display.update()
        self.pending_display.update()

        if self._debounce_task:
            self._debounce_task.cancel()
        self._debounce_task = self.page.run_task(self._debounce_commit)

    async def _debounce_commit(self):
        await asyncio.sleep(DEBOUNCE_SECONDS)
        self._commit_life()

    def _commit_life(self):
        if self.pending_delta == 0:
            return
        now = datetime.now()
        active_pn = self.get_active()
        self.history.append({
            "life": self.life,
            "turn": self.get_turn(),
            "active": self.player_name,
            "active_pn": active_pn,
            "active_short": f"P{active_pn}",
            "time": now.strftime("%H:%M"),
        })
        self.life += self.pending_delta
        self.pending_delta = 0
        self.pending_display.value = ""
        self.pending_display.opacity = 0
        self.life_display.value = str(self.life)
        self._rebuild_history()
        self.life_display.update()
        self.pending_display.update()
        self.history_row.update()

    def _rebuild_history(self):
        self.history_row.controls.clear()
        for entry in self.history:
            active_theme = THEMES.get(entry.get("active_pn", 1), self.t)
            # Diagonal strikethrough via rotated line over text
            life_text = ft.Text(
                str(entry["life"]), size=14,
                weight=ft.FontWeight.W_600, color=TEXT_DIM,
                text_align=ft.TextAlign.CENTER,
            )
            strike_line = ft.Container(
                width=28, height=2, bgcolor=self.t["strike"],
                border_radius=1,
                rotate=ft.Rotate(angle=-0.45),
            )
            life_stack = ft.Stack(
                [
                    ft.Container(content=life_text, alignment=CENTER),
                    ft.Container(content=strike_line, alignment=CENTER),
                ],
                width=30, height=20,
            )
            pill = ft.Container(
                content=ft.Column(
                    [
                        life_stack,
                        ft.Text(
                            f"{entry.get('active_short', '')} T{entry['turn']} {entry['time']}",
                            size=8, color=active_theme["accent"],
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
                bgcolor=SURFACE,
                border=ft.Border.all(1, BORDER_SUBTLE),
                border_radius=14,
                padding=ft.Padding.symmetric(horizontal=10, vertical=3),
            )
            self.history_row.controls.append(pill)

    # ── Land drops ───────────────────────────────────────────────
    def _land_plus(self):
        self.land_drops += 1
        self.land_display.value = str(self.land_drops)
        self.land_display.update()

    def _land_minus(self):
        if self.land_drops > 0:
            self.land_drops -= 1
            self.land_display.value = str(self.land_drops)
            self.land_display.update()

    def _land_reset(self):
        self.land_drops = 0
        self.land_display.value = "0"
        self.land_display.update()

    # ── Reset ────────────────────────────────────────────────────
    def reset(self):
        if self._debounce_task:
            self._debounce_task.cancel()
        self.life = STARTING_LIFE
        self.pending_delta = 0
        self.history.clear()
        self.land_drops = 0
        self.life_display.value = str(self.life)
        self.pending_display.value = ""
        self.pending_display.opacity = 0
        self.land_display.value = "0"
        self.history_row.controls.clear()
        self.life_display.update()
        self.pending_display.update()
        self.land_display.update()
        self.history_row.update()


def main(page: ft.Page):
    try:
        _main(page)
    except Exception as e:
        import traceback
        page.add(ft.Text(f"Error: {e}\n{traceback.format_exc()}", color="red", size=12))


def _main(page: ft.Page):
    page.title = "MTG Life Counter"
    page.bgcolor = BG
    page.padding = 10
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK
    
    async def enable_wakelock():
        wakelock = ft.Wakelock()
        await wakelock.enable()

    page.run_task(enable_wakelock)

    turn = [1]
    active_player = [1]

    def get_turn():
        return turn[0]

    def get_active():
        return active_player[0]

    p1 = PlayerPanel(1, get_turn, get_active, default_name="Player 1", flipped=False)
    p2 = PlayerPanel(2, get_turn, get_active, default_name="Me", flipped=False)

    def get_active_name():
        return (p1 if active_player[0] == 1 else p2).get_short_name()

    def update_active_highlight():
        p1.set_active(active_player[0] == 1)
        p2.set_active(active_player[0] == 2)
        ap = active_player[0]
        name = get_active_name()
        turn_label.value = f"{name} · Turn {turn[0]}"
        turn_label.color = THEMES[ap]["accent"]
        turn_label.update()

    def on_swap_active(e=None):
        active_player[0] = 2 if active_player[0] == 1 else 1
        update_active_highlight()

    def on_end_turn(e=None):
        active_player[0] = 2 if active_player[0] == 1 else 1
        turn[0] += 1
        update_active_highlight()

    def on_prev_turn(e=None):
        if active_player[0] == 2:
            active_player[0] = 1
        elif turn[0] > 1:
            active_player[0] = 2
            turn[0] -= 1
        update_active_highlight()

    def on_reset(e=None):
        p1.reset()
        p2.reset()
        turn[0] = 1
        active_player[0] = 1
        update_active_highlight()

    def on_swap_layout(e=None):
        """Toggle the top player's orientation (facing you vs facing opponent)."""
        top_panel = layout_column.controls[0]
        top_panel.set_flipped(not top_panel.flipped)

    # ── Center bar ───────────────────────────────────────────────
    turn_label = ft.Text(
        "Player 1 · Turn 1", size=12, weight=ft.FontWeight.W_900,
        color=P1_ACCENT, text_align=ft.TextAlign.CENTER,
    )

    turn_label_btn = ft.Container(
        content=turn_label, on_click=on_swap_active, ink=True,
        border_radius=8, padding=ft.Padding.symmetric(horizontal=8, vertical=4),
    )

    prev_turn_btn = ft.Container(
        content=ft.Text("◀", size=12, color=TEXT_FAINT, text_align=ft.TextAlign.CENTER),
        width=28, height=30, border_radius=8, bgcolor=ELEVATED,
        border=ft.Border.all(1, BORDER_SUBTLE),
        alignment=CENTER, on_click=on_prev_turn, ink=True,
    )

    end_turn_btn = ft.Container(
        content=ft.Text(
            "END TURN", size=11, weight=ft.FontWeight.W_900,
            color=TEXT_DIM, text_align=ft.TextAlign.CENTER,
        ),
        bgcolor=ELEVATED, border_radius=10,
        border=ft.Border.all(1, BORDER),
        padding=ft.Padding.symmetric(horizontal=14, vertical=7),
        alignment=CENTER, on_click=on_end_turn, ink=True,
    )

    reset_btn = ft.Container(
        content=ft.Icon(ft.Icons.RESTART_ALT_ROUNDED, color=DANGER, size=16),
        on_click=on_reset, border_radius=8,
        width=30, height=30, alignment=CENTER,
        bgcolor=ELEVATED, border=ft.Border.all(1, "#3d2020"),
    )

    swap_btn = ft.Container(
        content=ft.Text("↕", size=14, color=TEXT_DIM, text_align=ft.TextAlign.CENTER),
        on_click=on_swap_layout, border_radius=8,
        width=30, height=30, alignment=CENTER,
        bgcolor=ELEVATED, border=ft.Border.all(1, BORDER_SUBTLE),
        ink=True,
    )

    center_bar = ft.Container(
        content=ft.Row(
            [
                ft.Row([reset_btn, swap_btn], spacing=6),
                turn_label_btn,
                ft.Row([prev_turn_btn, end_turn_btn], spacing=6),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER_SUBTLE),
        border_radius=14,
        padding=ft.Padding.symmetric(horizontal=10, vertical=5),
    )

    layout_column = ft.Column(
        [p1, center_bar, p2],
        expand=True, spacing=8,
    )
    page.add(ft.SafeArea(content=layout_column, expand=True))

    page.update()

    update_active_highlight()


if os.environ.get("FLET_WEB"):
    ft.run(main, view=ft.AppView.WEB_BROWSER, port=8550)
else:
    ft.run(main)
