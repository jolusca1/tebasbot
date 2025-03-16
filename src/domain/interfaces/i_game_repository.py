from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.game import Game

class IGameRepository(ABC):
    @abstractmethod
    async def add_game(self, game: Game) -> bool:
        """Adiciona um novo jogo ao repositório"""
        pass

    @abstractmethod
    async def get_game_by_id(self, game_id: int) -> Optional[Game]:
        """Busca um jogo pelo ID"""
        pass

    @abstractmethod
    async def get_game_by_name(self, name: str) -> Optional[Game]:
        """Busca um jogo pelo nome (exato)"""
        pass

    @abstractmethod
    async def search_games_by_name(self, name: str) -> List[Game]:
        """Busca jogos que contenham o nome especificado"""
        pass

    @abstractmethod
    async def get_all_games(self) -> List[Game]:
        """Retorna todos os jogos cadastrados"""
        pass

    @abstractmethod
    async def delete_game(self, game_id: int) -> bool:
        """Deleta um jogo pelo ID"""
        pass

    @abstractmethod
    async def get_next_game_id(self) -> int:
        """Retorna o próximo ID disponível para um jogo"""
        pass 