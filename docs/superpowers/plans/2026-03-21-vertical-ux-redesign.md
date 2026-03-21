# Vertical UX Redesign Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the MTG life counter as a side-by-side column layout with reverse-chronological life logs, center Pass Turn divider, shared notes, and modular file structure.

**Architecture:** Full rewrite of the single 526-line `main.py` into 7 focused modules. Bottom-up build order: theme → game_state → life_log → player_panel → notes_panel → turn_bar → main. The debounce logic from the current `PlayerPanel._on_life_tap` / `_debounce_commit` / `_commit_life` chain is the reference implementation and must be preserved exactly.

**Tech Stack:** Python 3.13+, Flet 0.80.5+

**Spec:** `docs/superpowers/specs/2026-03-21-vertical-ux-redesign-design.md`

**Current code reference:** `src/main.py` (will be replaced entirely)

---

## Chunk 0: Bootstrap

### Task 0: Create `__init__.py` files for module imports

**Files:**
- Create: `src/__init__.py` (empty)
- Create: `tests/__init__.py` (empty)

These must exist before any cross-module imports or pytest runs.

- [ ] **Step 1: Create init files**

```python
# src/__init__.py — empty
# tests/__init__.py — empty
```

- [ ] **Step 2: Commit**

```bash
git add src/__init__.py tests/__init__.py
git commit -m "chore: add __init__.py files for module imports"
```

---

## Chunk 1: Foundation (theme + game_state)

### Task 1: Create `src/theme.py`

**Files:**
- Create: `src/theme.py`

- [ ] **Step 1: Write theme module**

```python
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
```

Note: `P1_STRIKE` / `P2_STRIKE` are removed — the new design uses `old → new` text format instead of strikethrough.

- [ ] **Step 2: Verify import works**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && uv run python -c "from src.theme import *; print(THEMES)"`
Expected: prints the THEMES dict without errors.

- [ ] **Step 3: Commit**

```bash
git add src/theme.py
git commit -m "feat: add theme module with colors and constants"
```

---

### Task 2: Create `src/game_state.py`

**Files:**
- Create: `src/game_state.py`
- Create: `tests/test_game_state.py`

- [ ] **Step 1: Write failing tests for game_state**

```python
from datetime import datetime
from src.game_state import GameState


def test_initial_state():
    gs = GameState()
    assert gs.turn == 1
    assert gs.active_player == 1
    assert gs.player_names == ["Me", "Opponent"]
    assert gs.notes == []


def test_pass_turn_swaps_active_and_increments():
    gs = GameState()
    gs.pass_turn()
    assert gs.active_player == 2
    assert gs.turn == 2
    gs.pass_turn()
    assert gs.active_player == 1
    assert gs.turn == 3


def test_set_active_without_advancing_turn():
    gs = GameState()
    gs.set_active(2)
    assert gs.active_player == 2
    assert gs.turn == 1  # turn unchanged


def test_add_note_auto_context():
    gs = GameState()
    gs.turn = 3
    gs.add_note("Opponent played Sheoldred")
    assert len(gs.notes) == 1
    note = gs.notes[0]
    assert note["text"] == "Opponent played Sheoldred"
    assert note["turn"] == 3
    assert "time" in note  # HH:MM string


def test_reset():
    gs = GameState()
    gs.turn = 5
    gs.active_player = 2
    gs.add_note("some note")
    gs.reset()
    assert gs.turn == 1
    assert gs.active_player == 1
    assert gs.notes == []
    assert gs.player_names == ["Me", "Opponent"]


def test_get_active_name():
    gs = GameState()
    assert gs.get_active_name() == "Me"
    gs.set_active(2)
    assert gs.get_active_name() == "Opponent"


def test_rename_player():
    gs = GameState()
    gs.player_names[0] = "Alice"
    assert gs.get_active_name() == "Alice"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && uv run python -m pytest tests/test_game_state.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.game_state'`

- [ ] **Step 3: Write game_state implementation**

```python
from datetime import datetime


class GameState:
    def __init__(self):
        self.turn: int = 1
        self.active_player: int = 1
        self.player_names: list[str] = ["Me", "Opponent"]
        self.notes: list[dict] = []

    def get_turn(self) -> int:
        return self.turn

    def get_active(self) -> int:
        return self.active_player

    def get_active_name(self) -> str:
        return self.player_names[self.active_player - 1]

    def pass_turn(self):
        self.active_player = 2 if self.active_player == 1 else 1
        self.turn += 1

    def set_active(self, player_number: int):
        self.active_player = player_number

    def add_note(self, text: str):
        now = datetime.now()
        self.notes.append({
            "text": text,
            "turn": self.turn,
            "time": now.strftime("%H:%M"),
        })

    def reset(self):
        self.turn = 1
        self.active_player = 1
        self.notes.clear()
        self.player_names = ["Me", "Opponent"]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && uv run python -m pytest tests/test_game_state.py -v`
Expected: All 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/game_state.py tests/test_game_state.py
git commit -m "feat: add game_state module with turn, notes, and active player logic"
```

---

## Chunk 2: Display Components (life_log + notes_panel + turn_bar)

### Task 3: Create `src/life_log.py`

**Files:**
- Create: `src/life_log.py`

This is a pure Flet display component — no unit tests (would require mocking the Flet page). Verified visually during integration.

- [ ] **Step 1: Write life_log module**

```python
import flet as ft
from src.theme import SURFACE, BORDER_SUBTLE, TEXT_DIM, TEXT_FAINT, THEMES


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
```

- [ ] **Step 2: Verify import works**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && uv run python -c "from src.life_log import LifeLog; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/life_log.py
git commit -m "feat: add life_log reverse-chronological display component"
```

---

### Task 4: Create `src/notes_panel.py`

**Files:**
- Create: `src/notes_panel.py`

- [ ] **Step 1: Write notes_panel module**

```python
import flet as ft
from src.theme import (
    SURFACE, ELEVATED, BORDER_SUBTLE, BORDER,
    TEXT, TEXT_DIM, TEXT_FAINT,
)
from src.game_state import GameState


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
```

- [ ] **Step 2: Verify import works**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && uv run python -c "from src.notes_panel import NotesPanel; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/notes_panel.py
git commit -m "feat: add shared notes panel with auto turn/timestamp context"
```

---

### Task 5: Create `src/turn_bar.py`

**Files:**
- Create: `src/turn_bar.py`

- [ ] **Step 1: Write turn_bar module**

```python
import flet as ft
from src.theme import (
    SURFACE, ELEVATED, BORDER, BORDER_SUBTLE,
    TEXT, TEXT_DIM, TEXT_FAINT, THEMES, CENTER,
)
from src.game_state import GameState


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
```

- [ ] **Step 2: Verify import works**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && uv run python -c "from src.turn_bar import TurnBar; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/turn_bar.py
git commit -m "feat: add center turn bar with Pass Turn button"
```

---

## Chunk 3: Player Panel (core component with debounce)

### Task 6: Create `src/player_panel.py`

**Files:**
- Create: `src/player_panel.py`

This is the largest module. It contains the debounce logic preserved exactly from the current implementation, plus delegates to `LifeLog` for history display.

- [ ] **Step 1: Write player_panel module**

```python
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
```

- [ ] **Step 2: Verify import works**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && uv run python -c "from src.player_panel import PlayerPanel; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/player_panel.py
git commit -m "feat: add player_panel with preserved debounce logic and life_log integration"
```

---

## Chunk 4: Main wiring + replace old code

### Task 7: Rewrite `src/main.py`

**Files:**
- Replace: `src/main.py`

- [ ] **Step 1: Write the new main.py**

```python
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
```

- [ ] **Step 2: Run the app to verify it launches**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && FLET_WEB=1 uv run flet run src/main.py`
Expected: App opens in browser with side-by-side columns, center turn bar, notes at bottom.

- [ ] **Step 3: Manual verification checklist**

Verify each interaction:
- [ ] Life ±1 and ±5 buttons work on both players
- [ ] Debounce: rapid taps accumulate, commit after 1.5s pause
- [ ] Life log shows entries in reverse-chronological order (newest top)
- [ ] Pass Turn button swaps active player and increments turn
- [ ] Active player has accent border, inactive has subtle border
- [ ] Tap player name → sets active player (no turn advance)
- [ ] Long-press player name → opens rename field
- [ ] Notes: type and submit → appears with turn + timestamp
- [ ] Reset button → everything resets to initial state
- [ ] Flip button → opponent column rotates 180°

- [ ] **Step 4: Run existing tests still pass**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && uv run python -m pytest tests/ -v`
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/main.py
git commit -m "feat: rewrite main.py with side-by-side column layout and modular wiring"
```

---

### Task 8: Final integration test and polish

**Files:**
- Modify: any file that needs visual tweaking after testing

- [ ] **Step 1: Run full test suite**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && uv run python -m pytest tests/ -v`
Expected: All tests pass.

- [ ] **Step 2: Launch app and do a full play-through**

Run: `cd /Users/totolasso/repos/personal/mtg-life-count && FLET_WEB=1 uv run flet run src/main.py`

Simulate a 3-turn game:
1. T1: Tap +1 on "Me" → wait for commit → log shows "20→21"
2. Pass Turn → active switches to Opponent, turn becomes T2
3. T2: Tap -3 on Opponent (three -1 taps) → wait → log shows "20→17"
4. Add note: "Opponent played Sheoldred" → appears with T2 context
5. Pass Turn → back to Me, T3
6. T3: Tap -5 on "Me" → wait → log shows "21→16"
7. Tap Opponent name to correct active → border switches without turn change
8. Reset → everything back to starting state

- [ ] **Step 3: Adjust sizing if needed**

If buttons are too cramped or life number too small in the side-by-side layout, adjust sizes in `src/player_panel.py` (life_display size, button dimensions) and `src/theme.py`. The key constraint is that two columns + center bar must fit on a phone screen (~375px wide).

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "polish: adjust sizing and layout after visual testing"
```

Only commit if changes were made in Step 3.
