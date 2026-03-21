import flet as ft
from theme import SURFACE, BORDER_SUBTLE, TEXT_FAINT, THEMES


class LifeLog(ft.Column):
    """Reverse-chronological scrollable life history for one player."""

    def __init__(self, player_number: int):
        super().__init__()
        self.player_number = player_number
        self.accent = THEMES[player_number]["accent"]
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = 2
        self.expand = True

    def rebuild(self, history: list[dict]):
        """Rebuild the log from a player's history list. Newest first."""
        self.controls.clear()
        for entry in reversed(history):
            old = entry["old"]
            new = entry["new"]
            delta = entry["delta"]
            turn = entry["turn"]
            time = entry["time"]
            sign = "+" if delta > 0 else ""
            row = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(
                            f"{old}→{new}",
                            size=12, weight=ft.FontWeight.W_600,
                            color=self.accent,
                        ),
                        ft.Text(
                            f"{sign}{delta} · T{turn} · {time}",
                            size=10, color=TEXT_FAINT,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=SURFACE,
                border=ft.Border.all(1, BORDER_SUBTLE),
                border_radius=8,
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            )
            self.controls.append(row)
