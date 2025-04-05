import threading
import discord
from discord.ext import commands
from src.application.routines.ranking_update_routine import schedule_ranking_updates
from src.application.commands.valorant_commands import ValorantCommands
from src.application.services.valorant_service import ValorantService
from src.infrastructure.database.mongodb.repositories.mongo_valorant_repository import MongoValorantRepository
import os
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
        # Inicializa o repositório
        valorant_repository = MongoValorantRepository()

        # Inicializa o serviço
        valorant_service = ValorantService(valorant_repository)

        # Adiciona os comandos
        await self.add_cog(ValorantCommands(self, valorant_service))

        # Sincroniza os comandos com o Discord
        if not self.synced:
            await self.tree.sync()
            self.synced = True

    async def on_ready(self):
        print(f"✅ Bot iniciado como {self.user}!")

def run_bot():
    # Inicia a rotina de atualização de rankings em uma thread separada
    ranking_thread = threading.Thread(target=schedule_ranking_updates)
    ranking_thread.start()

    bot = TebasBot()
    bot.run(os.getenv("DISCORD_TOKEN")) 

if __name__ == "__main__":
    run_bot()