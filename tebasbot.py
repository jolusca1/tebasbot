import discord
import os
import re
from dotenv import load_dotenv
from discord import app_commands
from steam_service.api_service import get_steam_profile, get_games_played_recently
from authorization.configer import AuthorizedUsersManager

from database import *

load_dotenv()

auth_manager = AuthorizedUsersManager()

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
        
class ConfirmView(discord.ui.View):
    def __init__(self, game_name: str, author: discord.User, timeout=30):
        super().__init__(timeout=timeout)
        self.game_name = game_name
        self.author = author

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Verifica se quem clicou é o mesmo que iniciou a ação
        if interaction.user != self.author:
            await interaction.response.send_message("Você não pode confirmar essa ação.", ephemeral=True)
            return

        success = await delete_game(self.game_name)
        if success:
            await interaction.response.edit_message(content=f"O jogo **{self.game_name}** foi deletado com sucesso.", view=None)
        else:
            await interaction.response.edit_message(content=f"Não foi possível encontrar ou deletar o jogo **{self.game_name}**.", view=None)
        self.stop()

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("Você não pode cancelar essa ação.", ephemeral=True)
            return
        await interaction.response.edit_message(content=f"A ação de deleção do jogo **{self.game_name}** foi cancelada.", view=None)
        self.stop()
        
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
    
# # Comando para adicionar um jogo ao banco
# @tree.command(name="adicionar_jogo", description="Adicione um novo jogo ao sistema")
# @app_commands.describe(game_name="Nome do jogo", score="Pontuação atribuída ao jogo")
# async def add_game_command(interaction: discord.Interaction, game_name: str, score: int):
    
#     if score <= 0:
#         await interaction.response.send_message("A pontuação deve ser maior que zero!", ephemeral=True)
#         return
    
#     message = await add_game(game_name, score)
#     await interaction.response.send_message(message)


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
    
@tree.command(name="jogos_zerados", description="Veja a lista de jogos zerados e a pontuação total de um usuário")
@app_commands.describe(user="Mencione o usuário que deseja consultar")
async def games_completed(interaction: discord.Interaction, user: discord.User):
    games, total_score = await get_completed_games(user)

    if not games:
        await interaction.response.send_message(f"🎮 {user.mention} ainda não zerou nenhum jogo!")
        return

    game_list = "\n".join([f"🔹 {game['name']} - {game['score']} pontos" for game in games])

    message = (
        f"🎮 **Jogos zerados por {user.mention}:**\n\n"
        f"{game_list}\n\n"
        f"🏅 **Pontuação total:** {total_score} pontos"
    )

    await interaction.response.send_message(message)
    
@tree.command(name="jogos", description="Lista dos jogos cadastrados.")
async def jogos(interaction: discord.Interaction, game_name:str=None):
    
    if not game_name:
        games = await get_all_games()
    else:
        games = await get_games_by_name(game_name)

    if not games:
        await interaction.response.send_message("Ainda não há jogos cadastrados.", ephemeral=True)
        return

    game_list = "\n".join([f"🔹 {game['name']} - {game['score']} pontos" for game in games])
    if not game_name:
        message = f"🎮 **Jogos cadastrados:**\n\n{game_list}"
    else:
        message = f"""🎮 **Jogos cadastrados com "{game_name}":**\n\n{game_list}"""

    await interaction.response.send_message(message)
    
@tree.command(name="perfil_steam", description="Pesquisar perfil na Steam")
async def steam(interaction: discord.Interaction, name: str):
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

@tree.command(name="ranking_zerados", description="Lista os jogos mais zerados")
async def ranking_zerados(interaction: discord.Interaction):
    ranking_list = await getRankingJogosZerados()

    if not ranking_list:
        await interaction.response.send_message("Ainda não há registros de jogos zerados.", ephemeral=True)
        return

    ranking_message = "**🎮 Ranking de Jogos Zerados 🎮**\n"
    ranking_message += "\n".join(
        [f"{i+1}. **{game}** - {count} vezes zerado(s)" for i, (game, count) in enumerate(ranking_list)]
    )

    await interaction.response.send_message(ranking_message)

@tree.command(name="comandos", description="Lista todos os comandos disponíveis e como usá-los")
async def comandos(interaction: discord.Interaction):
    command_list = """📌 **Comandos do Bot** 🎮🤖  

✅ **/score** – Veja sua pontuação total.  
✅ **/ranking** – Exibe o ranking dos usuários com mais pontos.  
✅ **/adicionar_jogo [nome] [pontuação]** – Adiciona um novo jogo ao sistema.  
✅ **/zerei [nome do jogo]** – Marca um jogo como zerado e ganha pontos.  
✅ **/jogos_zerados @usuário** – Lista todos os jogos zerados e a pontuação total do usuário mencionado. 
✅ **/jogos [nome]** – Lista todos os jogos cadastrados juntamente com os pontos de equivalência.
✅ **/ranking_zerados** – Exibe um ranking com os 10 jogos mais zerados.
✅ **/perfil_steam [usuário steam]** – Exibe perfil da Steam


🔹 **Como usar os comandos?**  
- Digite `/` e selecione o comando desejado.  
- Se o comando pedir um valor (ex: nome do jogo), digite conforme solicitado.  
- No caso de menção a outro usuário, use `@` e selecione o usuário.""" 

    # interacao
    await interaction.response.send_message(command_list, ephemeral=False)

@tree.command(name="adicionar_jogo", description="Adicione um novo jogo")
@app_commands.describe(game_name="Nome do jogo")
async def add_game_command(interaction: discord.Interaction, game_name: str):
    await interaction.response.defer(thinking=True)

    nota, justificativa = await avaliar_dificuldade_jogo(game_name)

    if nota is None:
        await interaction.followup.send(f"⚠️ Não foi possível avaliar a dificuldade de **{game_name}**. Tente novamente.", ephemeral=True)
        return

    message = await add_game(game_name, nota)

    await interaction.followup.send(f"{message}\n\n📋 **Justificativa da IA:** {justificativa}")

@tree.command(name="deletar_jogo", description="Deleta um jogo do sistema (Apenas Admin)")
@app_commands.describe(game_name="Nome do jogo a ser deletado")
async def deletar_jogo(interaction: discord.Interaction, game_name: str):
    if not auth_manager.is_authorized(interaction.user.id):
        await interaction.response.send_message("Você não tem permissão para deletar jogos.", ephemeral=True)
        return
    
    confirmacao_view = ConfirmView(game_name, interaction.user)
    
    await interaction.response.send_message(f"Você realmente quer deletar o jogo **{game_name}**? Confirme:", view=confirmacao_view, ephemeral=True)

acliente.run(os.getenv("DISCORD_TOKEN"))