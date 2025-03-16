import re
from typing import List, Optional
from src.domain.interfaces.i_game_repository import IGameRepository
from src.domain.models.game import Game
from ..connection import MongoDBConnection

class MongoGameRepository(IGameRepository):
    def __init__(self):
        self.db = MongoDBConnection()
        self.collection = self.db.get_collection('games')
        self.counters = self.db.get_collection('counters')

    async def add_game(self, game: Game) -> bool:
        """Adiciona um novo jogo ao banco de dados"""
        try:
            await self.collection.insert_one(game.to_dict())
            return True
        except Exception as e:
            return False

    async def get_game_by_id(self, game_id: int) -> Optional[Game]:
        game_data = await self.collection.find_one({"game_id": game_id})
        return Game.from_dict(game_data) if game_data else None

    async def get_game_by_name(self, name: str) -> Optional[Game]:
        """Busca um jogo pelo nome exato"""
        game_data = await self.collection.find_one(
            {"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}}
        )
        return Game.from_dict(game_data) if game_data else None

    async def search_games_by_name(self, name: str) -> List[Game]:
        cursor = self.collection.find(
            {"name": {"$regex": re.escape(name), "$options": "i"}}
        ).sort("score", -1)
        games_data = await cursor.to_list(length=None)
        return [Game.from_dict(game) for game in games_data]

    async def get_all_games(self) -> List[Game]:
        cursor = self.collection.find().sort("name", 1)
        games_data = await cursor.to_list(length=None)
        return [Game.from_dict(game) for game in games_data]

    async def delete_game(self, game_id: int) -> bool:
        """Deleta um jogo do banco de dados"""
        try:
            result = await self.collection.delete_one({"game_id": game_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Erro ao deletar jogo: {e}")
            return False

    async def get_next_game_id(self) -> int:
        result = await self.counters.find_one_and_update(
            {"_id": "game_id"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        return result["seq"] 
        return result["seq"] 