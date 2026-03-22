import random


def roll_d20_pair() -> tuple[int, int]:
    """Roll two D20 dice. Returns (player1_roll, player2_roll)."""
    return random.randint(1, 20), random.randint(1, 20)
