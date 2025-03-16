import discord
from discord import app_commands
from discord.ext import commands
from ...infrastructure.external.steam_api import get_steam_profile, get_games_played_recently

class SteamCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="perfil_steam", description="Pesquisar perfil na Steam")
    async def steam_profile(self, interaction: discord.Interaction, name: str):
        player = get_steam_profile(name)

        if player == "No match":
            await interaction.response.send_message("Perfil não encontrado. Talvez o nome possa estar errado.", ephemeral=True)
            return

        embed = discord.Embed(
            title=player["player"]["personaname"],
            url=player["player"]["profileurl"],
            description="Perfil da Steam",
            color=discord.Color.blue()
        )
        
        last_played = get_games_played_recently(player["player"]["steamid"])
            
        embed.set_thumbnail(url=player["player"]["avatarfull"])
        
        embed.add_field(name="Nome real", value=player["player"].get("realname", "Não disponível"), inline=True)
        embed.add_field(name="SteamID", value=player["player"]["steamid"], inline=True)
        embed.add_field(name="Status", value="Online" if player["player"]["personastate"] == 1 else "Offline", inline=True)
        embed.add_field(name="Criado em", value=f"<t:{player['player']['timecreated']}:D>", inline=True)
        
        for data in last_played['games']:
            embed.add_field(name="Últimos jogos jogados", value=f"{data['name']}", inline=True)
        
        await interaction.response.send_message(embed=embed) 