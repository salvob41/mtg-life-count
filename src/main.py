import os

import flet as ft
from src.theme import (
    BG, SURFACE, ELEVATED, BORDER_SUBTLE,
    TEXT_DIM, TEXT_FAINT, DANGER, THEMES, CENTER,
)
from src.game_state import GameState
from src.player_panel import PlayerPanel
from src.turn_bar import TurnBar
from src.notes_panel import NotesPanel


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

    # Wakelock
    async def enable_wakelock():
        wakelock = ft.Wakelock()
        await wakelock.enable()
    page.run_task(enable_wakelock)

    # Game state
    gs = GameState()

    def on_set_active(player_number: int):
        gs.set_active(player_number)
        update_active_highlight()

    # Player panels
    p1 = PlayerPanel(1, gs, on_set_active=on_set_active)
    p2 = PlayerPanel(2, gs, on_set_active=on_set_active)

    # Notes panel
    notes = NotesPanel(gs)

    def update_active_highlight():
        p1.set_active(gs.active_player == 1)
        p2.set_active(gs.active_player == 2)
        turn_bar.refresh()
        notes.refresh()

    def on_pass_turn():
        gs.pass_turn()
        update_active_highlight()

    # Turn bar
    turn_bar = TurnBar(gs, on_pass_turn=on_pass_turn)

    # Reset
    def on_reset(e=None):
        gs.reset()
        p1.reset()
        p2.reset()
        update_active_highlight()

    # Flip opponent
    def on_flip(e=None):
        p2.set_flipped(not p2.flipped)

    reset_btn = ft.Container(
        content=ft.Icon(ft.Icons.RESTART_ALT_ROUNDED, color=DANGER, size=16),
        on_click=on_reset, border_radius=8,
        width=30, height=30, alignment=CENTER,
        bgcolor=ELEVATED, border=ft.Border.all(1, "#3d2020"),
    )
    flip_btn = ft.Container(
        content=ft.Text("↕", size=14, color=TEXT_DIM, text_align=ft.TextAlign.CENTER),
        on_click=on_flip, border_radius=8,
        width=30, height=30, alignment=CENTER,
        bgcolor=ELEVATED, border=ft.Border.all(1, BORDER_SUBTLE),
        ink=True,
    )
    bottom_bar = ft.Container(
        content=ft.Row(
            [reset_btn, flip_btn],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        ),
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
    )

    # Main layout: two columns with center turn bar
    columns_row = ft.Row(
        [p1, turn_bar, p2],
        expand=True, spacing=6,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    layout = ft.Column(
        [columns_row, notes, bottom_bar],
        expand=True, spacing=8,
    )

    page.add(ft.SafeArea(content=layout, expand=True))
    page.update()
    update_active_highlight()


if os.environ.get("FLET_WEB"):
    ft.run(main, view=ft.AppView.WEB_BROWSER, port=8550)
else:
    ft.run(main)
