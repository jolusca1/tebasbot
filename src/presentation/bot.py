import threading
import os
import schedule
import time
import discord
from discord.ext import commands
from ..application.routines.player_update_routine import schedule_updates as schedule_player_updates
from ..application.routines.ranking_update_routine import schedule_ranking_updates
from ..application.commands.game_commands import GameCommands
from ..application.commands.user_commands import UserCommands
from ..application.commands.steam_commands import SteamCommands
from ..application.commands.admin_commands import AdminCommands
from ..application.commands.valorant_commands import ValorantCommands
from ..application.services.game_service import GameService
from ..application.services.user_service import UserService
from ..application.services.valorant_service import ValorantService
from ..infrastructure.database.mongodb.repositories.mongo_game_repository import MongoGameRepository
from ..infrastructure.database.mongodb.repositories.mongo_user_repository import MongoUserRepository
from ..infrastructure.database.mongodb.repositories.mongo_valorant_repository import MongoValorantRepository
from ..infrastructure.config.auth_manager import AuthorizedUsersManager
from dotenv import load_dotenv

load_dotenv()

class TebasBot(commands.Bot):
    def __init__(self):
        # Configura todas as intents necessárias
        intents = discord.Intents.default()
        intents.message_content = True  # Habilita o intent de conteúdo de mensagem
        intents.members = True          # Habilita o intent de membros
        intents.guilds = True           # Habilita o intent de servidores
        intents.guild_messages = True   # Habilita o intent de mensagens do servidor
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        self.synced = False

    async def setup_hook(self):
        # Inicializa os repositórios
        game_repository = MongoGameRepository()
        user_repository = MongoUserRepository()
        valorant_repository = MongoValorantRepository()

        # Inicializa os serviços
        game_service = GameService(game_repository)
        user_service = UserService(user_repository, game_repository)
        valorant_service = ValorantService(valorant_repository)

        # Inicializa o gerenciador de autorização
        auth_manager = AuthorizedUsersManager()

        # Adiciona os comandos
        await self.add_cog(GameCommands(self, game_service, user_service, auth_manager))
        await self.add_cog(UserCommands(self, user_service))
        await self.add_cog(SteamCommands(self))
        await self.add_cog(AdminCommands(self, auth_manager))
        await self.add_cog(ValorantCommands(self, valorant_service))

        # Sincroniza os comandos com o Discord
        if not self.synced:
            await self.tree.sync()
            self.synced = True

        # Inicia as rotinas de atualização em threads separadas
        self.start_update_routines()

    def start_update_routines(self):
        # Inicia a rotina de atualização de jogadores em uma thread separada
        player_update_thread = threading.Thread(target=schedule_player_updates)
        player_update_thread.start()
        
        # Inicia a rotina de atualização de rankings em uma thread separada
        ranking_thread = threading.Thread(target=schedule_ranking_updates, args=(1,))
        ranking_thread.start()

    async def on_ready(self):
        print(f"✅ Bot iniciado como {self.user}!")

def run_bot():
    bot = TebasBot()
    bot.run(os.getenv("DISCORD_TOKEN"))