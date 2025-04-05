from typing import List, Optional, Tuple
from src.domain.interfaces.i_user_repository import IUserRepository
from src.domain.models.valorant import ValorantPlayer
from ..connection import MongoDBConnection


class MongoValorantRepository(IUserRepository):
    def __init__(self):
        self.db = MongoDBConnection()
        self.collection = self.db.get_collection("players_valorant")

    async def get_user(self, name: str, tag: str, region: str) -> Optional[ValorantPlayer]:
        """Busca um player de valorant na base"""
        player_data = await self.collection.find_one(
            {"name": name, "tag": tag}
        )

        return ValorantPlayer.from_dict(player_data) if player_data else None

    async def create_user(self, player: ValorantPlayer) -> bool:
        """Crio player novo"""
        try:
            await self.collection.insert_one(player.to_dict())
            return True
        except Exception as e:
            print(f"Ocorreu um erro na transação de inserção: {e}")
            return False

    async def get_games_ranking(self):
        pass

    async def get_ranking(self):
        pass

    async def update_user(self):
        pass