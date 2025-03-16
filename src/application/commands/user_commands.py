import discord
from discord import app_commands
from discord.ext import commands
from ..services.user_service import UserService
from ..views.ranking_view import RankingView

class UserCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, user_service: UserService):
        self.bot = bot
        self.user_service = user_service

    @app_commands.command(name="score", description="Confira seu perfil e pontuação")
    async def score(self, interaction: discord.Interaction):
        # Obtém os dados do usuário
        user = await self.user_service.get_or_create_user(interaction.user.id)
        
        # Cria o embed do perfil
        embed = discord.Embed(
            title=f"📊 Perfil de {interaction.user.display_name}",
            color=discord.Color.purple()
        )
        
        # Adiciona a foto do usuário
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        # Estatísticas principais
        embed.add_field(
            name="🏆 Pontuação Total",
            value=f"**{user.points}** pontos",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Jogos Zerados",
            value=f"**{len(user.games_completed)}** jogos",
            inline=True
        )
        
        # Calcula a média de pontos por jogo
        avg_points = user.points / len(user.games_completed) if user.games_completed else 0
        embed.add_field(
            name="📈 Média",
            value=f"**{avg_points:.1f}** pontos/jogo",
            inline=True
        )
        
        # Lista os últimos jogos zerados (top 3)
        if user.games_completed:
            last_games = user.games_completed[-3:] if len(user.games_completed) > 3 else user.games_completed
            last_games_text = "\n".join([f"• {game.name} ({game.score} pts)" for game in reversed(last_games)])
            embed.add_field(
                name="🕹️ Últimos Jogos Zerados",
                value=last_games_text,
                inline=False
            )
        
        # Calcula estatísticas adicionais
        if user.games_completed:
            max_score_game = max(user.games_completed, key=lambda g: g.score)
            footer_text = f"🌟 Maior conquista: {max_score_game.name} ({max_score_game.score} pts)"
        else:
            footer_text = "🎯 Comece sua jornada zerando seu primeiro jogo!"
            
        embed.set_footer(text=footer_text)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ranking", description="Exibe o ranking dos usuários com mais pontos")
    async def ranking(self, interaction: discord.Interaction):
        users = await self.user_service.get_ranking()
        games_ranking = await self.user_service.get_games_ranking()

        if not users:
            await interaction.response.send_message("Ainda não há usuários no ranking.", ephemeral=True)
            return

        # Cria a view com os rankings
        view = RankingView(users, games_ranking)
        
        # Envia a mensagem inicial com o embed do ranking de usuários
        await interaction.response.send_message(
            embed=view.get_users_ranking_embed(),
            view=view
        )

    @app_commands.command(name="jogos_zerados", description="Veja a lista de jogos zerados e a pontuação total de um usuário")
    async def games_completed(self, interaction: discord.Interaction, user: discord.User):
        games, total_score = await self.user_service.get_completed_games(user.id)

        if not games:
            await interaction.response.send_message(f"🎮 {user.mention} ainda não zerou nenhum jogo!")
            return

        game_list = "\n".join([f"🔹 {game.name} - {game.score} pontos" for game in games])

        message = (
            f"🎮 **Jogos zerados por {user.mention}:**\n\n"
            f"{game_list}\n\n"
            f"🏅 **Pontuação total:** {total_score} pontos"
        )

        await interaction.response.send_message(message)

    @app_commands.command(name="comandos", description="Lista todos os comandos disponíveis e como usá-los")
    async def comandos(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📌 Comandos do Bot 🎮",
            description="Lista de todos os comandos disponíveis",
            color=discord.Color.blue()
        )

        # Comandos de Pontuação
        embed.add_field(
            name="🏆 Pontuação",
            value=(
                "• **/score** - Veja sua pontuação total\n"
                "• **/ranking** - Ranking dos usuários com mais pontos"
            ),
            inline=False
        )

        # Comandos de Jogos
        embed.add_field(
            name="🎮 Gerenciamento de Jogos",
            value=(
                "• **/adicionar_jogo [nome]** - Adiciona um novo jogo ao sistema\n"
                "• **/zerei [nome do jogo]** - Marca um jogo como zerado\n" 
                "• **/jogos [nome]** - Lista todos os jogos cadastrados"
            ),
            inline=False
        )

        # Comandos de Estatísticas
        embed.add_field(
            name="📊 Estatísticas",
            value=(
                "• **/jogos_zerados @usuário** - Lista jogos zerados do usuário\n"
                "• **/ranking_zerados** - Top 10 jogos mais zerados\n"
                "• **/perfil_steam [usuário]** - Exibe perfil da Steam"
            ),
            inline=False
        )

        # Como usar
        embed.add_field(
            name="❓ Como usar os comandos?",
            value=(
                "1. Digite `/` e selecione o comando desejado\n"
                "2. Preencha os campos solicitados\n" 
                "3. Para mencionar usuários, use `@` e selecione"
            ),
            inline=False
        )

        await interaction.response.send_message(embed=embed)