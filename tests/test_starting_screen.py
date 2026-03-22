import random
from starting_screen import roll_d20_pair, determine_winner


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


def test_determine_winner_player1_wins():
    assert determine_winner(15, 8) == 1


def test_determine_winner_player2_wins():
    assert determine_winner(3, 17) == 2


def test_determine_winner_tie():
    assert determine_winner(10, 10) == 0
