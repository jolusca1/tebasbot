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

    async def get_all_players(self):
        players = await self.valorant_repository.get_all_players()

        print(f"O que está retornando no get_all_players{players}")
        
        return players

    async def get_player_valorant(self, player_valorant: ValorantPlayer):
        valorant_api = ValorantAPI()
        player = player_valorant.to_dict()

        player_data = valorant_api.get_mmr_by_player(
            player["name"],
            player["tag"],
            player["region"]
        )

        print(player_data.get("status"))

        if player_data.get("status") == 200:

            return {
                "name": player_data.get("data").get("name"),
                "tag": player_data.get("data").get("tag"),
                "elo": player_data.get("data").get("current_data").get("currenttierpatched"),
                "mmr_last_match": player_data.get("data").get("current_data").get("mmr_change_to_last_game"),
                "current_mmr": player_data.get("data").get("current_data").get("ranking_in_tier"),
                "image": player_data.get("data").get("current_data").get("images").get("large"),
                "highest_rank": player_data.get("data").get("highest_rank").get("patched_tier")
            }
            
    async def update_player_ranking(self, player_valorant: ValorantPlayer):
        """Atualiza o ranking do jogador no banco de dados"""
        try:
            # Update the player's ranking in the repository
            await self.valorant_repository.update_user(player_valorant)
            print(f"Ranking atualizado: {player_valorant.name}#{player_valorant.tag}")
            return True
        except Exception as e:
            print(f"Erro ao atualizar ranking: {e}")
            return False
