from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Game:
    game_id: int
    name: str
    score: int
    criterios: Optional[List[str]] = None

    def to_dict(self) -> dict:
        return {
            "game_id": self.game_id,
            "name": self.name,
            "score": self.score,
            "criterios": self.criterios if self.criterios else []
        }

    @staticmethod
    def from_dict(data: dict) -> 'Game':
        return Game(
            game_id=data["game_id"],
            name=data["name"],
            score=data["score"],
            criterios=data.get("criterios", [])
        ) 