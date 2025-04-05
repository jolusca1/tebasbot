from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ValorantPlayer:
    name: str
    tag: str
    region: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "tag": self.tag,
            "region": self.region
        }

    @staticmethod
    def from_dict(data: str) -> 'Valorant':
        return ValorantPlayer(
            name=data["name"],
            tag=data["tag"],
            region=data["region"]
        )