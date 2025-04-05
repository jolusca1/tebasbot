from ...domain.models.valorant import ValorantPlayer
from ...domain.interfaces.i_user_repository import IUserRepository
from ...infrastructure.external.valorant_api import ValorantAPI


class ValorantService:
    def __init__(self, valorant_repository: IUserRepository):
        self.valorant_repository = valorant_repository

    async def get_or_create_player(self, name: str, tag:str, region: str):
        """Busca um jogador ou cria um novo caso não exista"""
        
        player = await self.valorant_repository.get_user(name, tag, region)

        if not player:
            player = ValorantPlayer(name, tag, region)

            await self.valorant_repository.create_user(player)

        return player

    async def get_player_valorant(self, player_valorant: ValorantPlayer):
        valorant_api = ValorantAPI()
        player = player_valorant.to_dict()
        print(player)

        player_data = valorant_api.get_mmr_by_player(
            player["name"],
            player["tag"],
            player["region"]
        )

        if player_data.get("status") == 200:

            return {
                "name": player_data.get("data").get("name"),
                "tag": player_data.get("data").get("tag"),
                "elo": player_data.get("data").get("current_data").get("currenttierpatched"),
                "mmr_last_match": player_data.get("data").get("current_data").get("mmr_change_to_last_game"),
                "image": player_data.get("data").get("current_data").get("images").get("large"),
                "highest_rank": player_data.get("data").get("highest_rank").get("patched_tier")
            }