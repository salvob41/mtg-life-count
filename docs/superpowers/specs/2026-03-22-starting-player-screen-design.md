# Starting Player Screen Design

## Overview

A full-screen overlay that appears on app launch (and after reset) to determine who goes first. Supports both D20 dice roll randomization and manual player selection.

## UX Flow

### Entry Points
- **App launch:** Overlay shown before game begins
- **After reset:** Reset button re-shows the overlay

### Screen States

1. **IDLE** — Initial state
   - Header: "Who goes first?"
   - Left side: Player 1 name in gold (#FFB800) with "tap to pick" hint
   - Center: D20 button with "tap to roll" hint
   - Right side: Player 2 name in cyan (#00E5FF) with "tap to pick" hint
   - Three tap targets: Player 1 name, Player 2 name, D20 button

2. **ROLLING** — Animation phase (~1s)
   - Random numbers (1-20) cycle on both sides every 100ms (10 frames)
   - Numbers displayed large in each player's accent color
   - Final values are pre-computed; cycling is purely visual

3. **RESULT** — Winner shown
   - Winner's side: highlighted background glow, dice result shown large, "WINNER" label, "tap to start" prompt
   - Loser's side: dice result shown, faded (reduced opacity)
   - Center: "VS" text
   - **Tap winner's side to dismiss overlay and start game**

4. **TIE** — Re-roll needed
   - Both results shown equal
   - Header changes to "Tie! Tap dice to re-roll"
   - D20 button reappears in center with pulsing border
   - Tap D20 to re-roll (returns to ROLLING state)

### Manual Pick Flow
- Tap a player name in IDLE state → skip directly to game with that player as active
- No animation, no dice — just immediate selection

## Architecture

### New File: `starting_screen.py`

A `StartingScreen` class extending `ft.Container` that acts as a full-screen overlay.

**Constructor args:**
- `game_state: GameState` — to read player names and set active player
- `on_start: Callable[[int], None]` — callback when a starting player is chosen

**Public methods:**
- `show()` — make overlay visible (called on app launch and after reset)
- `hide()` — make overlay invisible

**Internal state:**
- `state: str` — one of "idle", "rolling", "result", "tie"
- `roll_1: int`, `roll_2: int` — dice results
- Uses `page.run_task()` for the rolling animation (async sleep loop)

### Changes to `main.py`

- Wrap existing game layout + `StartingScreen` in `ft.Stack`
- `StartingScreen` is the top layer, game layout underneath
- Game layout loads normally but is visually hidden behind overlay
- `on_start` callback: sets `gs.set_active(winner)`, calls `update_active_highlight()`, hides overlay
- `on_reset`: calls `starting_screen.show()` in addition to existing reset logic

### No Changes to `game_state.py`

The overlay calls `gs.set_active(player_number)` — no new state needed.

## Visual Design

- Full dark background (#1a1a2e) matching app theme
- Player names use existing accent colors from `theme.py`
- D20 button: dark gradient background, rounded corners, bold "D20" text
- Winner highlight: subtle accent-colored background glow (rgba overlay)
- Tie state: D20 button border in accent color with CSS-style pulse animation
- Large dice result numbers (~48px equivalent) for readability

## Animation Details

- **Rolling:** `asyncio.sleep(0.1)` loop, 10 iterations, random numbers 1-20 displayed on each side
- **Landing:** Final numbers appear, ~300ms pause, then winner treatment fades in
- **No 3D rendering** — numbers only, keeps it simple and performant in Flet

## Edge Cases

- Player names may have been renamed (long-press feature) — overlay reads from `game_state.player_names`
- Reset during a game re-shows overlay with current player names
- Rapid taps during rolling animation are ignored (state guard)
