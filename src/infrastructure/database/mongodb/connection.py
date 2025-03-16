import os
from typing import Optional
import motor.motor_asyncio
from pymongo.collection import Collection
from pymongo.database import Database
from dotenv import load_dotenv

load_dotenv()

class MongoDBConnection:
    _instance = None
    _client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
    _db: Optional[Database] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializa a conexão com o MongoDB."""
        self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_TOKEN"))
        self.db = self.client['tebasBot']

    def get_collection(self, collection_name: str):
        """Retorna uma coleção específica do banco de dados."""
        return self.db[collection_name]

    def get_client(self):
        """Retorna o cliente MongoDB."""
        return self.client

    async def close(self):
        if self.client:
            await self.client.close()
            self.client = None
            self.db = None 