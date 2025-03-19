from typing import List, Optional, Tuple
from ...domain.models.user import User
from ...domain.models.game import Game
from ...domain.interfaces.i_user_repository import IUserRepository
from ...domain.interfaces.i_game_repository import IGameRepository

class UserService:
    def __init__(self, user_repository: IUserRepository, game_repository: IGameRepository):
        self.user_repository = user_repository
        self.game_repository = game_repository

    async def get_or_create_user(self, discord_id: int) -> User:
        """Busca um usuário ou cria um novo se não existir"""
        user = await self.user_repository.get_user(discord_id)
        if not user:
            user = User(discord_id=discord_id)
            await self.user_repository.create_user(user)
        return user

    async def get_user_points(self, discord_id: int) -> int:
        """Retorna a pontuação de um usuário"""
        user = await self.get_or_create_user(discord_id)
        return user.points

    async def complete_game(self, discord_id: int, game_name: str) -> Tuple[bool, str]:
        """Marca um jogo como zerado para um usuário"""
        # Busca o jogo
        game = await self.game_repository.get_game_by_name(game_name)
        if not game:
            return False, f"Nenhum jogo encontrado com '{game_name}'!"

        # Busca ou cria o usuário
        user = await self.get_or_create_user(discord_id)

        # Verifica se o usuário já zerou o jogo
        if user.has_completed_game(game.game_id):
            return False, f"Você já zerou **{game.name}**!"

        # Adiciona o jogo à lista de jogos zerados do usuário
        user.add_completed_game(game)

        # Atualiza o usuário no banco
        success = await self.user_repository.update_user(user)
        if success:
            return True, f"🏆 <@{user.discord_id}> zerou **{game.name}** e ganhou **{game.score} pontos**!"
        return False, "Erro ao atualizar os dados do usuário."

    async def get_ranking(self, limit: int = 10) -> List[User]:
        """Retorna o ranking de usuários"""
        return await self.user_repository.get_ranking(limit)

    async def get_games_ranking(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Retorna o ranking de jogos mais zerados"""
        return await self.user_repository.get_games_ranking(limit)

    async def get_completed_games(self, discord_id: int) -> Tuple[List[Game], int]:
        """Retorna a lista de jogos zerados por um usuário e sua pontuação total"""
        user = await self.get_or_create_user(discord_id)
        return user.games_completed, user.points 