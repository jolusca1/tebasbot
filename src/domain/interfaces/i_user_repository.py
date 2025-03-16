from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from ..models.user import User

class IUserRepository(ABC):
    @abstractmethod
    async def get_user(self, discord_id: int) -> Optional[User]:
        """Busca um usuário pelo ID do Discord"""
        pass

    @abstractmethod
    async def create_user(self, user: User) -> bool:
        """Cria um novo usuário"""
        pass

    @abstractmethod
    async def update_user(self, user: User) -> bool:
        """Atualiza os dados de um usuário"""
        pass

    @abstractmethod
    async def get_ranking(self, limit: int = 10) -> List[User]:
        """Retorna o ranking de usuários por pontos"""
        pass

    @abstractmethod
    async def get_games_ranking(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Retorna o ranking de jogos mais zerados"""
        pass 