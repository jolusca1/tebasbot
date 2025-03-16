from dataclasses import dataclass
from typing import List, Optional
from .game import Game

@dataclass
class CompletedGame:
    game_id: int
    name: str
    score: int

    @staticmethod
    def from_dict(data: dict) -> 'CompletedGame':
        return CompletedGame(
            game_id=data["game_id"],
            name=data["name"],
            score=data["score"]
        )

    def to_dict(self) -> dict:
        return {
            "game_id": self.game_id,
            "name": self.name,
            "score": self.score
        }

@dataclass
class User:
    discord_id: int
    points: int = 0
    games_completed: List[CompletedGame] = None

    def __post_init__(self):
        if self.games_completed is None:
            self.games_completed = []

    def add_completed_game(self, game: Game) -> None:
        completed_game = CompletedGame(
            game_id=game.game_id,
            name=game.name,
            score=game.score
        )
        self.games_completed.append(completed_game)
        self.points += game.score

    def has_completed_game(self, game_id: int) -> bool:
        return any(g.game_id == game_id for g in self.games_completed)

    def to_dict(self) -> dict:
        return {
            "discord_id": self.discord_id,
            "points": self.points,
            "games_completed": [game.to_dict() for game in self.games_completed]
        }

    @staticmethod
    def from_dict(data: dict) -> 'User':
        games_completed = [
            CompletedGame.from_dict(game_data)
            for game_data in data.get("games_completed", [])
        ]
        return User(
            discord_id=data["discord_id"],
            points=data.get("points", 0),
            games_completed=games_completed
        ) 