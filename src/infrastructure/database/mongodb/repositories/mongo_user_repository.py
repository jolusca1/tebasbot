from typing import List, Optional, Tuple
from src.domain.interfaces.i_user_repository import IUserRepository
from src.domain.models.user import User
from ..connection import MongoDBConnection

class MongoUserRepository(IUserRepository):
    def __init__(self):
        self.db = MongoDBConnection()
        self.collection = self.db.get_collection('users')

    async def get_user(self, discord_id: int) -> Optional[User]:
        """Busca um usuário pelo ID do Discord"""
        user_data = await self.collection.find_one({"discord_id": discord_id})
        return User.from_dict(user_data) if user_data else None

    async def create_user(self, user: User) -> bool:
        """Cria um novo usuário"""
        try:
            await self.collection.insert_one(user.to_dict())
            return True
        except Exception as e:
            return False

    async def update_user(self, user: User) -> bool:
        """Atualiza os dados de um usuário"""
        try:
            result = await self.collection.update_one(
                {"discord_id": user.discord_id},
                {"$set": user.to_dict()}
            )
            return result.modified_count > 0
        except Exception as e:
            return False

    async def get_ranking(self, limit: int = 10) -> List[User]:
        """Retorna o ranking de usuários por pontos"""
        cursor = self.collection.find().sort("points", -1).limit(limit)
        users_data = await cursor.to_list(length=None)
        return [User.from_dict(user_data) for user_data in users_data]

    async def get_games_ranking(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Retorna o ranking de jogos mais zerados"""
        pipeline = [
            {"$unwind": "$games_completed"},
            {"$group": {
                "_id": "$games_completed.name",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        return [(result["_id"], result["count"]) for result in results] 