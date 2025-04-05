from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.valorant import ValorantPlayer

class IValorantRepository(ABC):
    @abstractmethod
    async def get_user(self, name: str, tag: str, region: str) -> Optional[ValorantPlayer]:
        """Busca um usuário pelo ID do Discord"""
        pass

    @abstractmethod
    async def create_user(self, ValorantPlayer: ValorantPlayer) -> bool:
        """Cria um novo usuário"""
        pass

    @abstractmethod
    async def update_user(self, ValorantPlayer: ValorantPlayer) -> bool:
        """Atualiza os dados de um usuário"""
        pass

    @abstractmethod
    async def get_all_players(self) -> List[ValorantPlayer]:
        """Retorna todos os players"""
        pass
    
    @abstractmethod
    async def save_player_ranking(self, ranking: List[ValorantPlayer]) -> None:
        """Salva o ranking completo no banco de dados"""
        pass
    
    @abstractmethod
    async def update_player_ranking(self, player_id: str, new_rank: int) -> bool:
        """Atualiza a posição de um jogador no ranking"""
        pass
    
    @abstractmethod
    async def get_top_players(self, limit: int = 10) -> List[ValorantPlayer]:
        """Retorna os top jogadores do ranking"""
        pass
