import flet as ft
from theme import (
    SURFACE, ELEVATED, BORDER_SUBTLE, BORDER,
    TEXT, TEXT_DIM, TEXT_FAINT,
)
from game_state import GameState


class NotesPanel(ft.Container):
    """Shared notes area with auto-context (turn + timestamp)."""

    def __init__(self, game_state: GameState):
        super().__init__()
        self.game_state = game_state

        self.notes_list = ft.Column(
            spacing=2,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self.notes_scroll = ft.Container(
            content=self.notes_list,
            max_height=120,
            expand=True,
        )

        self.input_field = ft.TextField(
            hint_text=self._placeholder(),
            text_size=12,
            color=TEXT,
            hint_style=ft.TextStyle(color=TEXT_FAINT, size=12),
            bgcolor=ELEVATED,
            border_color=BORDER_SUBTLE,
            focused_border_color=BORDER,
            content_padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            on_submit=self._on_submit,
            expand=True,
            height=36,
        )

        self.content = ft.Column(
            [
                self.notes_scroll,
                self.input_field,
            ],
            spacing=4,
        )
        self.bgcolor = SURFACE
        self.border = ft.Border.all(1, BORDER_SUBTLE)
        self.border_radius = 10
        self.padding = ft.Padding.symmetric(horizontal=10, vertical=6)

    def _placeholder(self) -> str:
        return f"T{self.game_state.turn}: type a note..."

    def _on_submit(self, e):
        text = (self.input_field.value or "").strip()
        if not text:
            return
        self.game_state.add_note(text)
        self.input_field.value = ""
        self.input_field.hint_text = self._placeholder()
        self._rebuild_notes()
        self.input_field.update()
        self.notes_list.update()

    def _rebuild_notes(self):
        self.notes_list.controls.clear()
        for note in reversed(self.game_state.notes):
            row = ft.Text(
                f"T{note['turn']} · {note['time']} — {note['text']}",
                size=11, color=TEXT_DIM,
            )
            self.notes_list.controls.append(row)

    def refresh(self):
        """Called after turn change or reset to update placeholder."""
        self.input_field.hint_text = self._placeholder()
        self._rebuild_notes()
        self.input_field.update()
        self.notes_list.update()
