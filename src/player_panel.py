import asyncio
from datetime import datetime

import flet as ft
from src.theme import (
    STARTING_LIFE, DEBOUNCE_SECONDS,
    SURFACE, ELEVATED, BORDER, BORDER_SUBTLE,
    TEXT, TEXT_DIM, TEXT_FAINT, THEMES, CENTER,
)
from src.game_state import GameState
from src.life_log import LifeLog


class PlayerPanel(ft.Container):
    def __init__(self, player_number: int, game_state: GameState,
                 on_set_active=None):
        super().__init__()
        self.player_number = player_number
        self.game_state = game_state
        self.on_set_active = on_set_active
        self.t = THEMES[player_number]

        self.life: int = STARTING_LIFE
        self.pending_delta: int = 0
        self.history: list[dict] = []
        self._debounce_task = None
        self.flipped: bool = False

        # UI elements
        self.life_display = ft.Text(
            str(self.life), size=48, weight=ft.FontWeight.W_900,
            color=TEXT, text_align=ft.TextAlign.CENTER,
        )
        self.pending_display = ft.Text(
            "", size=16, weight=ft.FontWeight.BOLD,
            color=self.t["accent"], text_align=ft.TextAlign.LEFT,
            opacity=0, width=40,
        )
        self.player_label = ft.Text(
            self.game_state.player_names[player_number - 1].upper(),
            size=11, weight=ft.FontWeight.BOLD, color=TEXT_DIM,
        )
        self.name_field = ft.TextField(
            value=self.game_state.player_names[player_number - 1],
            text_size=12, color=TEXT,
            bgcolor=ELEVATED, border_color=self.t["accent"],
            content_padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            text_align=ft.TextAlign.CENTER,
            on_submit=lambda e: self._finish_rename(),
            on_blur=lambda e: self._finish_rename(),
            visible=False, width=120, height=34,
        )
        self.life_log = LifeLog(player_number)

        self._build()

    # ── Rename (long-press) ─────────────────────────────────────
    def _start_rename(self, e=None):
        self.name_field.value = self.game_state.player_names[self.player_number - 1]
        self.name_field.visible = True
        self.player_label.visible = False
        self.name_field.update()
        self.player_label.update()
        self.name_field.focus()

    def _finish_rename(self):
        new_name = (self.name_field.value or "").strip()
        if new_name:
            self.game_state.player_names[self.player_number - 1] = new_name
        self.player_label.value = self.game_state.player_names[self.player_number - 1].upper()
        self.name_field.visible = False
        self.player_label.visible = True
        self.player_label.update()
        self.name_field.update()

    def _on_name_tap(self, e=None):
        """Short tap on name → set this player as active."""
        if self.on_set_active:
            self.on_set_active(self.player_number)

    # ── Layout ──────────────────────────────────────────────────
    def _build(self):
        minus5 = self._make_life_btn("-5", -5, small=True)
        minus1 = self._make_life_btn("-1", -1, small=False)
        plus1 = self._make_life_btn("+1", +1, small=False)
        plus5 = self._make_life_btn("+5", +5, small=True)

        life_buttons = ft.Row(
            [minus5, minus1, plus1, plus5],
            alignment=ft.MainAxisAlignment.CENTER, spacing=6,
        )

        life_row = ft.Row(
            [ft.Container(width=40), self.life_display, self.pending_display],
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
            expand=False,
            height=70,
        )

        # Name header: tap to set active, long-press to rename
        label_btn = ft.GestureDetector(
            content=ft.Container(
                content=self.player_label,
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
            ),
            on_tap=self._on_name_tap,
            on_long_press_start=self._start_rename,
        )
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

        # Wrap life_log in a container with expand=True so it fills remaining space
        # but is bounded by the parent Column's expand behavior (scrollable within)
        log_container = ft.Container(
            content=self.life_log,
            expand=True,
        )

        elements = [
            header,
            life_area,
            life_buttons,
            ft.Container(height=2),
            log_container,
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
        self.border_radius = 16
        self.border = ft.Border.all(1, BORDER_SUBTLE)
        self.padding = ft.Padding.symmetric(horizontal=10, vertical=8)
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
        w = 42 if small else 56
        h = 34 if small else 40
        sz = 13 if small else 16
        return ft.Container(
            content=ft.Text(
                label, size=sz, weight=ft.FontWeight.W_600,
                color=TEXT if not small else TEXT_DIM,
                text_align=ft.TextAlign.CENTER,
            ),
            width=w, height=h, bgcolor=self.t["btn"], border_radius=10,
            border=ft.Border.all(1, BORDER),
            alignment=CENTER,
            on_click=lambda e, d=delta: self._on_life_tap(d), ink=True,
        )

    # ── Life logic ──────────────────────────────────────────────
    # DEBOUNCE MECHANISM preserved exactly from current code:
    #   _on_life_tap → cancel existing task → page.run_task(_debounce_commit) → sleep → _commit_life
    # The history entry SCHEMA is intentionally redesigned (old/new/delta instead of
    # just "life") to support the new "old → new" log format per spec.
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
        old = self.life
        new = old + self.pending_delta
        self.history.append({
            "old": old,
            "new": new,
            "delta": self.pending_delta,
            "turn": self.game_state.get_turn(),
            "time": now.strftime("%H:%M"),
        })
        self.life = new
        self.pending_delta = 0
        self.pending_display.value = ""
        self.pending_display.opacity = 0
        self.life_display.value = str(self.life)
        self.life_log.rebuild(self.history)
        self.life_display.update()
        self.pending_display.update()
        self.life_log.update()

    # ── Reset ───────────────────────────────────────────────────
    def reset(self):
        if self._debounce_task:
            self._debounce_task.cancel()
        self.life = STARTING_LIFE
        self.pending_delta = 0
        self.history.clear()
        self.life_display.value = str(self.life)
        self.pending_display.value = ""
        self.pending_display.opacity = 0
        self.life_log.rebuild(self.history)
        self.life_display.update()
        self.pending_display.update()
        self.life_log.update()
