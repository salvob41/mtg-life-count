import pytest
from datetime import datetime
from game_state import GameState


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
    assert gs.turn == 1


def test_add_note_auto_context():
    gs = GameState()
    gs.turn = 3
    gs.add_note("Opponent played Sheoldred")
    assert len(gs.notes) == 1
    note = gs.notes[0]
    assert note["text"] == "Opponent played Sheoldred"
    assert note["turn"] == 3
    assert "time" in note


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


def test_set_active_invalid_player_number():
    gs = GameState()
    with pytest.raises(ValueError):
        gs.set_active(0)
    with pytest.raises(ValueError):
        gs.set_active(3)
