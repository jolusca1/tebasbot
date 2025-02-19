import discord
import os
from dotenv import load_dotenv
from discord import app_commands

from database import *

load_dotenv()

#teste deploy

class Client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False
        
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
            
        print(f"Entramos como {self.user}!")
        
acliente = Client()
tree = app_commands.CommandTree(acliente)

@tree.command(name="score", description="Confira seu score")
async def score(interaction: discord.Interaction):
    points = await check_points(interaction.user)
    await interaction.response.send_message(f"<@{interaction.user.id}> possui {points} pontos!")
    
# Ranking de usuários com mention
@tree.command(name="ranking", description="Exibe o ranking dos usuários com mais pontos")
async def ranking(interaction: discord.Interaction):
    ranking_list = await getRanking()  # Obtém o ranking

    if not ranking_list:
        await interaction.response.send_message("Ainda não há usuários no ranking.", ephemeral=True)
        return

    ranking_message = "**🏆 Ranking de Pontos 🏆**\n" + "\n".join(ranking_list)
    await interaction.response.send_message(ranking_message)
    
acliente.run(os.getenv("DISCORD_TOKEN"))