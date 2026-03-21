import flet as ft
from theme import TEXT, THEMES, CENTER
from game_state import GameState


class TurnBar(ft.Container):
    """Center divider between player columns: turn number + Pass Turn button."""

    def __init__(self, game_state: GameState, on_pass_turn):
        super().__init__()
        self.game_state = game_state
        self.on_pass_turn = on_pass_turn

        self.turn_text = ft.Text(
            f"T{game_state.turn}",
            size=14, weight=ft.FontWeight.W_900,
            color=THEMES[game_state.active_player]["accent"],
            text_align=ft.TextAlign.CENTER,
        )

        self.pass_btn = ft.Container(
            content=ft.Text(
                "PASS\nTURN", size=10, weight=ft.FontWeight.W_900,
                color=TEXT, text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=THEMES[game_state.active_player]["accent"],
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=8, vertical=10),
            alignment=CENTER,
            on_click=lambda e: self.on_pass_turn(),
            ink=True,
        )

        self.content = ft.Column(
            [self.turn_text, self.pass_btn],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )
        self.width = 60
        self.alignment = CENTER

    def refresh(self):
        """Update display after turn change."""
        accent = THEMES[self.game_state.active_player]["accent"]
        self.turn_text.value = f"T{self.game_state.turn}"
        self.turn_text.color = accent
        self.pass_btn.bgcolor = accent
        self.turn_text.update()
        self.pass_btn.update()
