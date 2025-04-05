from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ValorantPlayer:
    name: str
    tag: str
    region: str
    elo: str = ""
    current_mmr: int = 0
    mmr_last_match: Optional[int] = None
    image: str = ""
    highest_rank: str = ""

    def to_dict(self) -> Dict:
        """Converts the player instance to a dictionary for MongoDB storage"""
        return {
            "name": self.name,
            "tag": self.tag,
            "region": self.region,
            "elo": self.elo,
            "current_mmr": self.current_mmr,
            "mmr_last_match": self.mmr_last_match,
            "image": self.image,
            "highest_rank": self.highest_rank
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ValorantPlayer':
        """Creates a ValorantPlayer instance from a dictionary retrieved from MongoDB"""
        return cls(
            name=data.get("name", ""),
            tag=data.get("tag", ""),
            region=data.get("region", ""),
            elo=data.get("elo", ""),
            current_mmr=data.get("current_mmr", 0),
            mmr_last_match=data.get("mmr_last_match", None),
            image=data.get("image", ""),
            highest_rank=data.get("highest_rank", "")
        )
    
    def to_mongo(self) -> Dict:
        """Converts the player instance to a format suitable for MongoDB operations"""
        return self.to_dict()
    
    @classmethod
    def from_mongo(cls, data: Dict) -> 'ValorantPlayer':
        """Creates a ValorantPlayer instance from MongoDB data"""
        if not data:
            return None
        return cls.from_dict(data)
