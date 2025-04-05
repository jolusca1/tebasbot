import discord
from discord import app_commands
from discord.ext import commands
from ....utils.translator_elo import translate_elo
from ...infrastructure.external.valorant_api import ValorantAPI

# from ..services.valorant_service import ValorantService


class ValorantCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="rank_valorant", description="Confira seu elo de VALORANT")
    async def ranking_valorant(self, interaction: discord.Interaction, name: str, tag: str, region: str = "na"):

        player_collection = db["players"]
        player_data = player_collection.find_one({"name": name, "tag": tag, "region": region})
        
        valorant_api = ValorantAPI()
        data = valorant_api.get_mmr_by_player(name, tag)

        await interaction.response.send_message(msg)