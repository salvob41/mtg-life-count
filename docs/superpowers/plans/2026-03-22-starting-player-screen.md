# Starting Player Screen Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a D20 dice roll overlay screen that determines who goes first, shown on app launch and after reset.

**Architecture:** New `starting_screen.py` module containing a `StartingScreen` overlay widget. Integrated into `main.py` via `ft.Stack` layering. No changes to `game_state.py`. The overlay manages its own state machine (idle → rolling → result/tie) and calls back to `main.py` when a starting player is chosen.

**Tech Stack:** Python, Flet, asyncio

**Spec:** `docs/superpowers/specs/2026-03-22-starting-player-screen-design.md`

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `src/starting_screen.py` | Create | Full-screen overlay with D20 roll logic, state machine, and manual pick |
| `src/main.py` | Modify | Wrap layout in `ft.Stack`, wire `StartingScreen`, update reset flow |
| `tests/test_starting_screen.py` | Create | Unit tests for dice roll logic and state transitions |

---

## Chunk 1: Core Logic and Tests

### Task 1: Dice roll helper — test first

**Files:**
- Create: `tests/test_starting_screen.py`
- Create: `src/starting_screen.py`

- [ ] **Step 1: Write failing tests for roll logic**

```python
# tests/test_starting_screen.py
import random
from starting_screen import roll_d20_pair


def test_roll_d20_pair_returns_two_ints():
    r1, r2 = roll_d20_pair()
    assert isinstance(r1, int)
    assert isinstance(r2, int)


def test_roll_d20_pair_range():
    for _ in range(100):
        r1, r2 = roll_d20_pair()
        assert 1 <= r1 <= 20
        assert 1 <= r2 <= 20


def test_roll_d20_pair_deterministic_with_seed():
    random.seed(42)
    a1, a2 = roll_d20_pair()
    random.seed(42)
    b1, b2 = roll_d20_pair()
    assert (a1, a2) == (b1, b2)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && python -m pytest tests/test_starting_screen.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'starting_screen'`

- [ ] **Step 3: Implement roll_d20_pair**

```python
# src/starting_screen.py (initial — just the helper)
import random


def roll_d20_pair() -> tuple[int, int]:
    """Roll two D20 dice. Returns (player1_roll, player2_roll)."""
    return random.randint(1, 20), random.randint(1, 20)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && python -m pytest tests/test_starting_screen.py -v`
Expected: All 3 PASS

- [ ] **Step 5: Commit**

```bash
git add src/starting_screen.py tests/test_starting_screen.py
git commit -m "feat: add roll_d20_pair helper with tests"
```

---

### Task 2: State machine logic — test first

**Files:**
- Modify: `tests/test_starting_screen.py`
- Modify: `src/starting_screen.py`

- [ ] **Step 1: Write failing tests for determine_winner**

Append to `tests/test_starting_screen.py`:

```python
from starting_screen import determine_winner


def test_determine_winner_player1_wins():
    assert determine_winner(15, 8) == 1


def test_determine_winner_player2_wins():
    assert determine_winner(3, 17) == 2


def test_determine_winner_tie():
    assert determine_winner(10, 10) == 0
```

- [ ] **Step 2: Run tests to verify new tests fail**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && python -m pytest tests/test_starting_screen.py -v`
Expected: 3 new FAIL — `ImportError: cannot import name 'determine_winner'`

- [ ] **Step 3: Implement determine_winner**

Add to `src/starting_screen.py`:

```python
def determine_winner(roll_1: int, roll_2: int) -> int:
    """Return winner (1 or 2) or 0 for tie."""
    if roll_1 > roll_2:
        return 1
    elif roll_2 > roll_1:
        return 2
    return 0
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && python -m pytest tests/test_starting_screen.py -v`
Expected: All 6 PASS

- [ ] **Step 5: Commit**

```bash
git add src/starting_screen.py tests/test_starting_screen.py
git commit -m "feat: add determine_winner helper with tests"
```

---

## Chunk 2: StartingScreen Widget

### Task 3: Build the StartingScreen overlay widget

**Files:**
- Modify: `src/starting_screen.py`

This is the main UI widget. It cannot be unit-tested easily (Flet widgets require a running page), so we build it using the tested helpers from Tasks 1-2 and verify manually in Task 5.

- [ ] **Step 1: Write the full StartingScreen class**

Replace `src/starting_screen.py` with the complete module. Keep `roll_d20_pair` and `determine_winner` at module level, add the class below them:

```python
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
            letter_spacing=2,
        )

        self.p1_name = ft.Text(
            game_state.player_names[0].upper(), size=16,
            weight=ft.FontWeight.W_900, color=THEMES[1]["accent"],
            text_align=ft.TextAlign.CENTER, letter_spacing=1,
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
            letter_spacing=1, visible=False,
        )

        self.p2_name = ft.Text(
            game_state.player_names[1].upper(), size=16,
            weight=ft.FontWeight.W_900, color=THEMES[2]["accent"],
            text_align=ft.TextAlign.CENTER, letter_spacing=1,
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
            letter_spacing=1, visible=False,
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
```

- [ ] **Step 2: Run existing tests to make sure nothing broke**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && python -m pytest tests/ -v`
Expected: All tests PASS (6 from test_starting_screen + 8 from test_game_state)

- [ ] **Step 3: Commit**

```bash
git add src/starting_screen.py
git commit -m "feat: add StartingScreen overlay widget with D20 roll and manual pick"
```

---

## Chunk 3: Integration with main.py

### Task 4: Wire StartingScreen into main.py

**Files:**
- Modify: `src/main.py:1-116`

- [ ] **Step 1: Add import**

Add to imports in `main.py`:

```python
from starting_screen import StartingScreen
```

- [ ] **Step 2: Create StartingScreen and wire on_start callback**

After the `turn_bar = TurnBar(...)` line (line 60), add:

```python
    # Starting screen overlay
    def on_start(player_number: int):
        gs.set_active(player_number)
        update_active_highlight()
        starting_screen.hide()

    starting_screen = StartingScreen(gs, on_start=on_start)
```

- [ ] **Step 3: Update on_reset to re-show overlay**

Change the `on_reset` function to also show the starting screen:

```python
    def on_reset(e=None):
        gs.reset()
        p1.reset()
        p2.reset()
        update_active_highlight()
        starting_screen.show()
```

- [ ] **Step 4: Wrap layout in ft.Stack with overlay on top**

Replace the current `page.add(...)` block (lines 102-108):

```python
    layout = ft.Column(
        [columns_row, notes, bottom_bar],
        expand=True, spacing=8,
    )

    page.add(ft.SafeArea(
        content=ft.Stack(
            [layout, starting_screen],
            expand=True,
        ),
        expand=True,
    ))
    page.update()
    update_active_highlight()
```

- [ ] **Step 5: Run all tests**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 6: Manual smoke test**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && uv run flet run src/main.py`

Verify:
1. App launches with "WHO GOES FIRST?" overlay
2. Tapping a player name starts the game with that player active
3. Tapping D20 shows rolling animation, then result
4. Winner can tap their side to start
5. Tie shows re-roll prompt
6. Reset button re-shows the overlay

- [ ] **Step 7: Commit**

```bash
git add src/main.py
git commit -m "feat: integrate StartingScreen overlay into main layout and reset flow"
```
