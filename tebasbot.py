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
    def __init__(self, game_id, game_name: str, author: discord.User, timeout=30):
        super().__init__(timeout=timeout)
        self.game_id = game_id
        self.game_name = game_name
        self.author = author

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("Você não pode confirmar essa ação.", ephemeral=True)
            return

        result = await games.delete_one({"_id": self.game_id})
        original_message = await interaction.original_response()
        if result.deleted_count > 0:
            await original_message.edit(content=f"O jogo **{self.game_name}** foi deletado com sucesso.", view=None)
        else:
            await original_message.edit(content=f"Não foi possível deletar o jogo **{self.game_name}**.", view=None)
        self.stop()

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("Você não pode cancelar essa ação.", ephemeral=True)
            return
        original_message = await interaction.original_response()
        await original_message.edit(content=f"A ação de deleção do jogo **{self.game_name}** foi cancelada.", view=None)
        self.stop()
        
class CriteriosView(discord.ui.View):
    def __init__(self, game_name: str, criterios: list, user: discord.User, timeout=180):
        super().__init__(timeout=timeout)
        self.game_name = game_name
        self.criterios = criterios
        self.user = user
        self.responses = {criterio: False for criterio in criterios}
        self.create_buttons()

    def truncate_text(self, text, max_length=50):
        """Trunca o texto para caber no botão"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    def create_buttons(self):
        for i, criterio in enumerate(self.criterios, 1):
            # Cria um label curto para o botão
            button_label = f"Critério {i}"
            
            button = discord.ui.Button(
                label=button_label,
                style=discord.ButtonStyle.secondary,
                custom_id=criterio  # Mantém o critério original como ID
            )
            button.callback = self.button_callback
            self.add_item(button)

        confirm_button = discord.ui.Button(
            label="✅ Confirmar",
            style=discord.ButtonStyle.success,
            custom_id="confirm"
        )
        confirm_button.callback = self.confirm_callback
        self.add_item(confirm_button)

    async def button_callback(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("Você não pode responder por outro usuário!", ephemeral=True)
            return

        criterio = interaction.data["custom_id"]
        if criterio in self.responses:
            self.responses[criterio] = not self.responses[criterio]
            button = [x for x in self.children if x.custom_id == criterio][0]
            button.style = discord.ButtonStyle.success if self.responses[criterio] else discord.ButtonStyle.secondary
            
            # Atualiza o embed com a lista completa de critérios e seu status
            embed = discord.Embed(
                title=f"🎮 Verificação de Conclusão: {self.game_name}",
                description="Clique nos critérios que você completou:",
                color=discord.Color.blue()
            )
            
            criterios_status = []
            for i, (crit, completed) in enumerate(self.responses.items(), 1):
                status = "✅" if completed else "⬜"
                criterios_status.append(f"{status} **Critério {i}:**\n{crit}")
            
            embed.add_field(
                name="Lista de Critérios:", 
                value="\n\n".join(criterios_status), 
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=self)

    async def confirm_callback(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("Você não pode confirmar por outro usuário!", ephemeral=True)
            return

        all_completed = all(self.responses.values())
        if all_completed:
            message = await completeGame(self.user, self.game_name)
            await interaction.response.edit_message(content=message, view=None)
        else:
            incomplete_criterios = []
            for i, (criterio, completed) in enumerate(self.responses.items(), 1):
                if not completed:
                    incomplete_criterios.append(f"**Critério {i}:**\n{criterio}")
            
            await interaction.response.edit_message(
                content=f"❌ Você ainda não completou todos os critérios para zerar **{self.game_name}**!\n\n**Critérios pendentes:**\n\n" + 
                "\n\n".join(incomplete_criterios),
                view=None
            )

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
    game = await is_game_exist(game_name)
    if not game:
        await interaction.response.send_message(f"❌ Nenhum jogo encontrado com o nome **{game_name}**!")
        return

    # Verifica se o usuário já zerou o jogo
    user_data = users.find_one({"discord_id": interaction.user.id})
    if user_data and "games_completed" in user_data:
        if any(g["game_id"] == game["game_id"] for g in user_data["games_completed"]):
            await interaction.response.send_message(f"❌ Você já zerou **{game['name']}**!")
            return

    criterios = await get_game_criterios(game_name)
    if not criterios:
        # Se não houver critérios cadastrados, usa o fluxo antigo
        message = await completeGame(interaction.user, game_name)
        await interaction.response.send_message(message)
        return

    embed = discord.Embed(
        title=f"🎮 Verificação de Conclusão: {game['name']}",
        description="Clique nos critérios que você completou:",
        color=discord.Color.blue()
    )

    # Adiciona os critérios iniciais ao embed
    criterios_status = []
    for i, criterio in enumerate(criterios, 1):
        criterios_status.append(f"⬜ **Critério {i}:**\n{criterio}")
    
    embed.add_field(
        name="Lista de Critérios:", 
        value="\n\n".join(criterios_status), 
        inline=False
    )

    view = CriteriosView(game['name'], criterios, interaction.user)
    await interaction.response.send_message(embed=embed, view=view)
    
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

    game = await is_game_exist(game_name)
    if game:
        await interaction.followup.send(f"⚠️ O jogo **{game['name']}** já está cadastrado com {game['score']} pontos.", ephemeral=True)
        return

    nota, avaliacao = await avaliar_dificuldade_jogo(game_name)

    if nota is None:
        await interaction.followup.send(f"⚠️ Não foi possível avaliar a dificuldade de **{game_name}**. Tente novamente.", ephemeral=True)
        return

    criterios = extract_criterios(avaliacao)
    message = await add_game(game_name, nota, criterios)

    embed = discord.Embed(
        title=f"🎮 {game_name} foi adicionado!",
        color=discord.Color.green()
    )
    
    embed.add_field(name="Status", value=message, inline=False)
    
    # Dividir a avaliação em seções
    sections = avaliacao.split('\n\n')
    for section in sections:
        if section.startswith('Nota:'):
            embed.add_field(name="📊 Nota", value=section.strip(), inline=False)
        elif section.startswith('Critérios para Zerar:'):
            embed.add_field(name="✅ Critérios para Zerar", value=section.replace('Critérios para Zerar:', '').strip(), inline=False)
        elif section.startswith('Justificativa da Nota:'):
            embed.add_field(name="📝 Justificativa", value=section.replace('Justificativa da Nota:', '').strip(), inline=False)

    await interaction.followup.send(embed=embed)

@tree.command(name="deletar_jogo", description="Deleta um jogo do sistema")
@app_commands.describe(game_name="Nome do jogo a ser deletado")
async def deletar_jogo(interaction: discord.Interaction, game_name: str):
    await interaction.response.defer(ephemeral=True)
    
    if not auth_manager.is_authorized(interaction.user.id):
        await interaction.followup.send("Você não tem permissão para deletar jogos.", ephemeral=True)
        return
    
    # game = await get_games_by_name(game_name, find_one=True)
    # if not game:
    #     await interaction.followup.send(f"Jogo **{game_name}** não encontrado.", ephemeral=True)
    #     return
    message = await delete_game(game_name)
    
    if not message:
        await interaction.followup.send(f"O jogo {game_name} não foi encontrado!")
        return
    
    # confirmacao_view = ConfirmView(game_id=game["_id"], game_name=found_game_name, author=interaction.user)
    
    await interaction.followup.send(
        f"O jogo **{message}** foi deletado com sucesso.",
        ephemeral=False
    )


acliente.run(os.getenv("DISCORD_TOKEN"))