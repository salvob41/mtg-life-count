import random


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
