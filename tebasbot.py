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
    await interaction.response.send_message(f"{interaction.user.display_name} possui {points} pontos!")
    
acliente.run(os.getenv("DISCORD_TOKEN"))