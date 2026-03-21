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
