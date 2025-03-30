from typing import List, Optional, Tuple
from ...domain.models.game import Game
from ...domain.interfaces.i_game_repository import IGameRepository
from ...infrastructure.external.groq_api import avaliar_dificuldade_jogo, extract_criterios

class GameService:
    def __init__(self, game_repository: IGameRepository):
        self.game_repository = game_repository

    async def add_game(self, name: str) -> Tuple[bool, str]:
        """Adiciona um novo jogo ao sistema"""
        # Verifica se o jogo já existe
        existing_game = await self.game_repository.get_game_by_name(name)
        if existing_game:
            return False, f"⚠️ O jogo **{existing_game.name}** já está cadastrado com {existing_game.score} pontos."

        # Avalia a dificuldade do jogo
        nota, avaliacao = await avaliar_dificuldade_jogo(name)
        if nota is None:
            return False, f"⚠️ Não foi possível avaliar a dificuldade de **{name}**. Tente novamente."

        # Extrai os critérios da avaliação
        criterios = extract_criterios(avaliacao)

        # Cria o novo jogo
        game_id = await self.game_repository.get_next_game_id()
        new_game = Game(
            game_id=game_id,
            name=name,
            score=nota,
            criterios=criterios
        )

        # Adiciona o jogo ao repositório
        success = await self.game_repository.add_game(new_game)
        if success:
            return True, (new_game, avaliacao)
        return False, "Erro ao adicionar o jogo ao banco de dados."

    async def get_game(self, name: str) -> Optional[Game]:
        """Busca um jogo pelo nome"""
        # Primeiro tenta buscar pelo nome exato
        game = await self.game_repository.get_game_by_name(name)
        if game:
            return game

        # Se não encontrar, busca por nome similar
        games = await self.game_repository.search_games_by_name(name)
        return games[0] if games else None

    async def search_games(self, name: str = None) -> List[Game]:
        """Busca jogos pelo nome ou retorna todos"""
        if name:
            return await self.game_repository.search_games_by_name(name)
        return await self.game_repository.get_all_games()

    async def delete_game(self, game_id: int) -> bool:
        """Deleta um jogo do sistema"""
        try:
            return await self.game_repository.delete_game(game_id)
        except Exception as e:
            return False 