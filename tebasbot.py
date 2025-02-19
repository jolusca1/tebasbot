import discord
import os
import re
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
    
# Comando para adicionar um jogo ao banco
@tree.command(name="adicionar_jogo", description="Adicione um novo jogo ao sistema")
@app_commands.describe(game_name="Nome do jogo", score="Pontuação atribuída ao jogo")
async def add_game_command(interaction: discord.Interaction, game_name: str, score: int):
    
    if score <= 0:
        await interaction.response.send_message("A pontuação deve ser maior que zero!", ephemeral=True)
        return
    
    message = await add_game(game_name, score)
    await interaction.response.send_message(message)


# Comando para marcar um jogo como zerado
async def completeGame(user, game_name):
    """Marca um jogo como zerado por um usuário, buscando pelo nome aproximado."""
    
    game = games.find_one({"name": {"$regex": re.escape(game_name), "$options": "i"}})

    if not game:
        return f"Nenhum jogo encontrado com '{game_name}'!"

    await newUser(user)

    user_data = users.find_one({"discord_id": user.id})
    
    if any(g["game_id"] == game["game_id"] for g in user_data.get("games_completed", [])):
        return f"Você já zerou **{game['name']}**!"

    users.update_one(
        {"discord_id": user.id},
        {
            "$inc": {"points": game["score"]},
            "$push": {"games_completed": {
                "game_id": game["game_id"],
                "name": game["name"],
                "score": game["score"]
            }}
        }
    )

    return f"🏆 {user.display_name} zerou **{game['name']}** e ganhou **{game['score']} pontos**!"

@tree.command(name="zerei", description="Marque um jogo como zerado e ganhe pontos")
@app_commands.describe(game_name="Nome (ou parte do nome) do jogo")
async def complete_game_command(interaction: discord.Interaction, game_name: str):
    message = await completeGame(interaction.user, game_name)
    await interaction.response.send_message(message)
    
@tree.command(name="games_completed", description="Veja a lista de jogos zerados e a pontuação total de um usuário")
@app_commands.describe(user="Mencione o usuário que deseja consultar")
async def games_completed(interaction: discord.Interaction, user: discord.User):
    games, total_score = await get_completed_games(user)

    if not games:
        await interaction.response.send_message(f"🎮 {user.mention} ainda não zerou nenhum jogo!")
        return

    # Formata a resposta com os jogos e pontos
    game_list = "\n".join([f"🔹 {game['name']} - {game['score']} pontos" for game in games])

    message = (
        f"🎮 **Jogos zerados por {user.mention}:**\n\n"
        f"{game_list}\n\n"
        f"🏅 **Pontuação total:** {total_score} pontos"
    )

    await interaction.response.send_message(message)
    
acliente.run(os.getenv("DISCORD_TOKEN"))