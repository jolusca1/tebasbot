import json
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class AuthorizedUsersManager:
    def __init__(self, filename: str = None):
        """
        Inicializa o gerenciador de usuários autorizados.
        
        Args:
            filename: Caminho para o arquivo JSON que armazena os IDs autorizados.
                     Se não fornecido, usa o valor de PATH_AUTH do .env
        """
        self.filename = filename or os.getenv("PATH_AUTH")
        if not self.filename:
            raise ValueError("PATH_AUTH não definido no arquivo .env")
        
        self.authorized_ids = self.load_authorized_ids()

    def load_authorized_ids(self) -> List[int]:
        """Carrega a lista de IDs autorizados do arquivo JSON"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("authorized_ids", [])
            return []
        except Exception as e:
            print(f"Erro ao carregar IDs autorizados: {e}")
            return []

    def save_authorized_ids(self) -> bool:
        """Salva a lista de IDs autorizados no arquivo JSON"""
        try:
            with open(self.filename, "w", encoding='utf-8') as f:
                json.dump({"authorized_ids": self.authorized_ids}, f, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar IDs autorizados: {e}")
            return False

    def is_authorized(self, user_id: int) -> bool:
        """Verifica se um usuário está autorizado"""
        return user_id in self.authorized_ids

    def add_user(self, user_id: int) -> bool:
        """Adiciona um usuário à lista de autorizados"""
        if user_id not in self.authorized_ids:
            self.authorized_ids.append(user_id)
            return self.save_authorized_ids()
        return True

    def remove_user(self, user_id: int) -> bool:
        """Remove um usuário da lista de autorizados"""
        if user_id in self.authorized_ids:
            self.authorized_ids.remove(user_id)
            return self.save_authorized_ids()
        return True

    def get_authorized_users(self) -> List[int]:
        """Retorna a lista de usuários autorizados"""
        return self.authorized_ids.copy() 