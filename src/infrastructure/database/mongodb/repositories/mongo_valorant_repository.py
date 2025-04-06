from typing import List, Optional
from src.domain.interfaces.i_valorant_repository import IValorantRepository
from src.domain.models.valorant import ValorantPlayer
from ..connection import MongoDBConnection


class MongoValorantRepository(IValorantRepository):
    def __init__(self):
        self.db = MongoDBConnection()
        self.collection = self.db.get_collection("players_valorant")
        self.ranking_collection = self.db.get_collection("valorant_rankings")

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

    async def get_all_players(self) -> List[ValorantPlayer]:
        """Retorna todos os players"""
        players_cursor = self.collection.find({})
        players_list = [ValorantPlayer.from_dict(player) async for player in players_cursor]
        return players_list

    async def update_user(self, player: ValorantPlayer) -> bool:
        """Atualiza os dados de um usuário"""
        try:
            player = await self.collection.find_one(
                {"name": player.name, "tag": player.tag, "region": player.region}
            )
            if player:
                await self.collection.update_one(
                    {"name": player.name, "tag": player.tag},
                    {"$set": player.to_dict()}
                )
            else:
                await self.collection.insert_one(
                    {"$set": player.to_dict()}
                )
            return True
        except Exception as e:
            print(f"Erro ao atualizar jogador: {e}")
            return False
            
    async def save_player_ranking(self, ranking: List[ValorantPlayer]) -> bool:
        """Salva o ranking completo no banco de dados"""
        try:
            await self.ranking_collection.replace_one(
                {"_id": "valorant_ranking"},
                {"ranking": [player.to_dict() for player in ranking]},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Erro ao salvar ranking: {e}")
            return False
            
    async def get_player_ranking(self) -> List[ValorantPlayer]:
        """Recupera o ranking de jogadores do banco de dados"""
        ranking_data = await self.ranking_collection.find_one({"_id": "valorant_ranking"})
        if not ranking_data or "ranking" not in ranking_data:
            return []
            
        return [ValorantPlayer.from_dict(player_data) for player_data in ranking_data["ranking"]]
        
    async def get_top_players(self, limit: int = 10) -> List[ValorantPlayer]:
        """Retorna os top jogadores do ranking"""
        players_cursor = self.collection.find({}).sort("elo", -1).limit(limit)
        top_players = [ValorantPlayer.from_dict(player) async for player in players_cursor]
        return top_players

    async def update_player_ranking(self, player_id: str, new_rank: int) -> bool:
        """Atualiza a posição de um jogador no ranking"""
        try:
            await self.collection.update_one(
                {"_id": player_id},
                {"$set": {"rank": new_rank}}
            )
            return True
        except Exception as e:
            print(f"Erro ao atualizar ranking do jogador: {e}")
            return False
