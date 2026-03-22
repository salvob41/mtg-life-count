import asyncio
import random

import flet as ft
from game_state import GameState
from theme import BG, TEXT, TEXT_DIM, TEXT_FAINT, THEMES, CENTER, ELEVATED, BORDER


def roll_d20_pair() -> tuple[int, int]:
    """Roll two D20 dice. Returns (player1_roll, player2_roll)."""
    return random.randint(1, 20), random.randint(1, 20)


def determine_winner(roll_1: int, roll_2: int) -> int:
    """Return winner (1 or 2) or 0 for tie."""
    if roll_1 > roll_2:
        return 1
    elif roll_2 > roll_1:
        return 2
    return 0


class StartingScreen(ft.Container):
    """Full-screen overlay for choosing who goes first."""

    def __init__(self, game_state: GameState, on_start):
        super().__init__()
        self.game_state = game_state
        self.on_start = on_start
        self.state = "idle"
        self.roll_1 = 0
        self.roll_2 = 0
        self.winner = 0
        self._roll_task = None

        # UI refs
        self.header_text = ft.Text(
            "WHO GOES FIRST?", size=14, weight=ft.FontWeight.W_900,
            color=TEXT_DIM, text_align=ft.TextAlign.CENTER,
        )

        self.p1_name = ft.Text(
            game_state.player_names[0].upper(), size=16,
            weight=ft.FontWeight.W_900, color=THEMES[1]["accent"],
            text_align=ft.TextAlign.CENTER,
        )
        self.p1_roll_text = ft.Text(
            "", size=48, weight=ft.FontWeight.W_900,
            color=THEMES[1]["accent"], text_align=ft.TextAlign.CENTER,
        )
        self.p1_hint = ft.Text(
            "tap to pick", size=11, color=TEXT_FAINT,
            text_align=ft.TextAlign.CENTER,
        )
        self.p1_winner_label = ft.Text(
            "WINNER", size=12, weight=ft.FontWeight.W_700,
            color=THEMES[1]["accent"], text_align=ft.TextAlign.CENTER,
            visible=False,
        )

        self.p2_name = ft.Text(
            game_state.player_names[1].upper(), size=16,
            weight=ft.FontWeight.W_900, color=THEMES[2]["accent"],
            text_align=ft.TextAlign.CENTER,
        )
        self.p2_roll_text = ft.Text(
            "", size=48, weight=ft.FontWeight.W_900,
            color=THEMES[2]["accent"], text_align=ft.TextAlign.CENTER,
        )
        self.p2_hint = ft.Text(
            "tap to pick", size=11, color=TEXT_FAINT,
            text_align=ft.TextAlign.CENTER,
        )
        self.p2_winner_label = ft.Text(
            "WINNER", size=12, weight=ft.FontWeight.W_700,
            color=THEMES[2]["accent"], text_align=ft.TextAlign.CENTER,
            visible=False,
        )

        self.vs_text = ft.Text(
            "", size=16, weight=ft.FontWeight.W_900,
            color=TEXT_FAINT, text_align=ft.TextAlign.CENTER,
        )

        self.d20_btn = ft.Container(
            content=ft.Text(
                "D20", size=24, weight=ft.FontWeight.W_900,
                color=TEXT, text_align=ft.TextAlign.CENTER,
            ),
            width=72, height=72, bgcolor=ELEVATED,
            border=ft.Border.all(2, BORDER), border_radius=12,
            alignment=CENTER, on_click=lambda e: self._on_roll_tap(),
        )
        self.d20_hint = ft.Text(
            "tap to roll", size=11, color=TEXT_FAINT,
            text_align=ft.TextAlign.CENTER,
        )

        self._build_layout()

    def _build_layout(self):
        # Player 1 side
        self.p1_side = ft.Container(
            content=ft.Column(
                [self.p1_name, self.p1_roll_text, self.p1_winner_label, self.p1_hint],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER, spacing=8,
            ),
            expand=True, on_click=lambda e: self._on_player_tap(1),
            border=ft.Border(right=ft.BorderSide(1, BORDER)),
        )

        # Center
        self.center_col = ft.Container(
            content=ft.Column(
                [self.d20_btn, self.d20_hint, self.vs_text],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER, spacing=8,
            ),
            width=120,
        )

        # Player 2 side
        self.p2_side = ft.Container(
            content=ft.Column(
                [self.p2_name, self.p2_roll_text, self.p2_winner_label, self.p2_hint],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER, spacing=8,
            ),
            expand=True, on_click=lambda e: self._on_player_tap(2),
            border=ft.Border(left=ft.BorderSide(1, BORDER)),
        )

        main_row = ft.Row(
            [self.p1_side, self.center_col, self.p2_side],
            expand=True, spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.content = ft.Column(
            [
                ft.Container(height=24),
                self.header_text,
                ft.Container(expand=True, content=main_row),
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.bgcolor = BG
        self.expand = True

    def _on_player_tap(self, player_number: int):
        """Manual pick — only works in idle and result states."""
        if self.state == "idle":
            self.on_start(player_number)
        elif self.state == "result":
            if player_number == self.winner:
                self.on_start(self.winner)

    def _on_roll_tap(self):
        """D20 roll — only works in idle and tie states."""
        if self.state not in ("idle", "tie"):
            return
        self.state = "rolling"
        self.roll_1, self.roll_2 = roll_d20_pair()
        self._roll_task = self.page.run_task(self._animate_roll)

    async def _animate_roll(self):
        """Cycle random numbers for ~1s, then show result."""
        self.d20_btn.visible = False
        self.d20_hint.visible = False
        self.vs_text.value = "VS"
        self.vs_text.visible = True
        self.p1_hint.visible = False
        self.p2_hint.visible = False
        self.p1_winner_label.visible = False
        self.p2_winner_label.visible = False
        self.p1_side.bgcolor = None
        self.p2_side.bgcolor = None
        self.page.update()

        # Rolling animation: 10 frames at 100ms
        for _ in range(10):
            self.p1_roll_text.value = str(random.randint(1, 20))
            self.p2_roll_text.value = str(random.randint(1, 20))
            self.page.update()
            await asyncio.sleep(0.1)

        # Land on final values
        self.p1_roll_text.value = str(self.roll_1)
        self.p2_roll_text.value = str(self.roll_2)
        self.page.update()
        await asyncio.sleep(0.3)

        # Determine winner
        self.winner = determine_winner(self.roll_1, self.roll_2)
        if self.winner == 0:
            self._show_tie()
        else:
            self._show_winner(self.winner)

    def _show_winner(self, winner: int):
        self.state = "result"
        if winner == 1:
            self.p1_winner_label.visible = True
            self.p1_hint.value = "tap to start"
            self.p1_hint.visible = True
            self.p1_hint.color = THEMES[1]["accent"]
            self.p1_side.bgcolor = THEMES[1]["surface"]
            self.p2_side.opacity = 0.4
        else:
            self.p2_winner_label.visible = True
            self.p2_hint.value = "tap to start"
            self.p2_hint.visible = True
            self.p2_hint.color = THEMES[2]["accent"]
            self.p2_side.bgcolor = THEMES[2]["surface"]
            self.p1_side.opacity = 0.4
        self.page.update()

    def _show_tie(self):
        self.state = "tie"
        self.header_text.value = "TIE! TAP DICE TO RE-ROLL"
        self.header_text.color = THEMES[1]["accent"]
        self.d20_btn.visible = True
        self.d20_btn.border = ft.Border.all(2, THEMES[1]["accent"])
        self.d20_hint.visible = False
        self.vs_text.visible = False
        self.page.update()

    def show(self):
        """Reset overlay to idle and make visible."""
        if self._roll_task:
            self._roll_task.cancel()
            self._roll_task = None
        self.state = "idle"
        self.roll_1 = 0
        self.roll_2 = 0
        self.winner = 0
        self.header_text.value = "WHO GOES FIRST?"
        self.header_text.color = TEXT_DIM
        self.p1_name.value = self.game_state.player_names[0].upper()
        self.p2_name.value = self.game_state.player_names[1].upper()
        self.p1_roll_text.value = ""
        self.p2_roll_text.value = ""
        self.p1_hint.value = "tap to pick"
        self.p1_hint.color = TEXT_FAINT
        self.p1_hint.visible = True
        self.p2_hint.value = "tap to pick"
        self.p2_hint.color = TEXT_FAINT
        self.p2_hint.visible = True
        self.p1_winner_label.visible = False
        self.p2_winner_label.visible = False
        self.p1_side.bgcolor = None
        self.p1_side.opacity = 1
        self.p2_side.bgcolor = None
        self.p2_side.opacity = 1
        self.d20_btn.visible = True
        self.d20_btn.border = ft.Border.all(2, BORDER)
        self.d20_hint.visible = True
        self.vs_text.value = ""
        self.vs_text.visible = False
        self.visible = True
        if self.page:
            self.page.update()

    def hide(self):
        """Hide overlay."""
        self.visible = False
        if self.page:
            self.page.update()
