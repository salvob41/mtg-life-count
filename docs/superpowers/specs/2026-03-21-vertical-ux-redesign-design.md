# MTG Life Counter — Vertical UX Redesign

## Overview

Full rewrite of the MTG life counter app from a vertically-stacked two-player layout to a side-by-side column layout (left = me, right = opponent), with reverse-chronological life logs, a center "Pass Turn" divider, and a shared notes area. Better SRP via module separation.

## Architecture — File Structure

```
src/
├── main.py              # App entry, page setup, two-column layout wiring
├── theme.py             # Colors, constants, player accent configs
├── game_state.py        # Turn, active player, notes — shared mutable state
├── player_panel.py      # PlayerPanel: life display, ±buttons, debounce logic
├── life_log.py          # Reverse-chronological life history widget
├── notes_panel.py       # Shared notes area with auto-context (turn + timestamp)
└── turn_bar.py          # Center divider: turn indicator + Pass Turn button
```

### Module Responsibilities

- **`theme.py`** — All colors, sizes, accent configs. Single source of truth for styling. Player 1 = gold (#FFB800), Player 2 = cyan (#00E5FF). Dark theme preserved.
- **`game_state.py`** — Holds `turn`, `active_player`, `player_names`, `notes`. Exposes callbacks (`get_turn`, `get_active`, `get_active_name`). Handles turn transitions and note storage.
- **`player_panel.py`** — Life total, ±buttons, pending delta display, debounce commit. Owns its `history` list but delegates rendering to `life_log.py`.
- **`life_log.py`** — Renders the reverse-chronological scrollable log entries. Pure display component.
- **`notes_panel.py`** — Text input with auto-prepended turn/timestamp. Shared between players.
- **`turn_bar.py`** — The center column divider with turn number and Pass Turn button.
- **`main.py`** — Wires everything together. Creates the two-column + center divider + notes layout. Handles reset, flip, wakelock.

## Layout

```
┌──────────────┬─────┬──────────────┐
│              │     │              │
│   ME (left)  │ CTR │  OPP (right) │
│              │     │              │
│  ┌────────┐  │     │  ┌────────┐  │
│  │ Name   │  │ T3  │  │ Name   │  │
│  │        │  │     │  │        │  │
│  │  18    │  │PASS │  │  17    │  │
│  │        │  │TURN │  │        │  │
│  │-5 -1+1+5│ │     │  │-5 -1+1+5│ │
│  └────────┘  │     │  └────────┘  │
│              │     │              │
│  LOG (↓new)  │     │  LOG (↓new)  │
│  20→18 T3    │     │  20→17 T3    │
│  20→20 T2    │     │  20→20 T2    │
│  ...         │     │  ...         │
│              │     │              │
├──────────────┴─────┴──────────────┤
│  📝 T3: Opponent played Sheoldred │
│  [type a note...]                 │
├───────────────────────────────────┤
│  [↻ Reset]  [↕ Flip]             │
└───────────────────────────────────┘
```

- **Active player** gets accent border (gold/cyan) — inactive gets subtle border
- **Center divider** is narrow — turn number + Pass Turn button stacked vertically
- **Life log** grows downward, newest on top, scrollable
- **Notes** span full width at the bottom, shared
- **Reset/Flip** are secondary actions in a small bottom bar

## Interaction Design

### Life Changes (Debounce — PRESERVE EXACTLY)

The current debounce implementation is the reference. Preserve it exactly:

1. Tap ±1, ±5 buttons (or left/right tap zones on life number)
2. `pending_delta` accumulates immediately, display updates optimistically
3. Pending indicator shows "+3" or "-2" near the life number
4. After 1.5s of no input → commit: history entry created, pending resets
5. Pattern: `_on_life_tap` → cancel existing task → start new `_debounce_commit` → `_commit_life`

### Life Log Entries (Reverse-Chronological)

Each entry shows: `old → new · delta · Turn N · HH:MM`
- Newest at top, scrollable downward for older entries
- Color-coded to the owning player's accent color (not the active player's)
- No strikethrough — the `old → new` format is clearer than the current pill design
- `_commit_life` stores `old`, `delta` (from `pending_delta`), and computes `new = old + delta`. All three stored for display convenience.

### Pass Turn

- Single button in center divider
- Tapping: swaps active player, increments turn counter
- Active panel border lights up with accent color
- To correct active player without advancing turn: tap the player's name

### Notes

- Text field at the bottom, placeholder: "T3: type a note..."
- On submit: note saved with auto-prepended turn + timestamp
- Notes display as scrollable list above input, newest on top
- Format: `T3 · 14:32 — Opponent played Sheoldred`
- Notes area has a fixed max height of 120px to avoid pushing player panels off screen

### Player Name

- **Long-press** name to rename (inline edit) — distinct from tap, which sets active player
- Short tap on name → sets that player as active (without advancing turn)

### Reset

- Small button in bottom bar
- `main.py` orchestrates reset: calls `game_state.reset()` (turn, active, notes) AND `player_panel.reset()` on both panels (life, history)

### Flip

- Small button in bottom bar (kept but not prominent)
- Rotates the opponent (right) column 180° — useful when sharing phone across a table
- Note: in side-by-side layout this is less natural than the old stacked layout; may feel awkward but kept per user request

## Data Flow

```
game_state.py (shared)
  ├── turn: int
  ├── active_player: int (1 or 2)
  ├── player_names: [str, str]
  ├── notes: list[dict]  — {text, turn, time}
  │
  ├── pass_turn()      → swaps active, increments turn
  ├── set_active(pn)   → sets active player (name tap)
  ├── add_note(text)   → auto-adds turn + timestamp
  └── reset()          → resets everything

player_panel.py (per player, owns its state)
  ├── life: int
  ├── pending_delta: int
  ├── history: list[dict]  — {old, new, delta, turn, time}
  ├── _debounce_task: Task
  │
  ├── _on_life_tap(delta)  → accumulate + start debounce
  ├── _debounce_commit()   → async wait 1.5s then commit
  ├── _commit_life()       → create history entry, reset pending
  └── reset()              → life=20, clear history

main.py (wiring)
  └── creates: game_state, p1_panel, p2_panel, turn_bar, notes_panel
      └── passes game_state callbacks to all components
```

**Key principle:** `PlayerPanel` doesn't know about the other player or the notes. It gets `get_turn` and `get_active` callbacks from `game_state`. The `turn_bar` calls `game_state.pass_turn()` and triggers highlight updates on both panels. Notes panel reads/writes through `game_state`.

## Removed Features

- **Land drop tracker** — removed to reduce clutter
- **Separate "End Turn" / "Back Turn" / "Swap Active" buttons** — consolidated into Pass Turn + tap-name-to-activate
- **History pill design with strikethrough** — replaced with cleaner `old → new` list format

## Kept Features

- **Flip/rotate** for opponent column (secondary, in bottom bar)
- **Screen wakelock** (Android)
- **1.5s debounce** for life changes (exact same implementation)
- **Player rename** via long-press
- **Dark theme** with gold/cyan player accents
- **Timestamps** on all log entries

## Defaults

- `STARTING_LIFE = 20`
- `DEBOUNCE_SECONDS = 1.5`
- Color palette preserved from current theme
- Player 1 (left, "Me") defaults to name "Me" — Player 2 (right) defaults to "Opponent"

## Infrastructure

- **Error boundary**: Preserved from current code. `main()` wraps `_main()` in try/except, displays errors on-screen as red text.
- **Wakelock**: Handled in `main.py` using `ft.Wakelock()` with `await wakelock.enable()`. No error handling needed (Flet silently ignores unsupported platforms).
- **Launch modes**: Both native (`uv run flet run src/main.py`) and web (`FLET_WEB=1`) modes preserved via the existing `if __name__` / `ft.app()` pattern.
