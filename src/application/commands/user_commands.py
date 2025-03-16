import discord
from discord import app_commands
from discord.ext import commands
from ..services.user_service import UserService

class UserCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, user_service: UserService):
        self.bot = bot
        self.user_service = user_service

    @app_commands.command(name="score", description="Confira seu score")
    async def score(self, interaction: discord.Interaction):
        points = await self.user_service.get_user_points(interaction.user.id)
        await interaction.response.send_message(f"<@{interaction.user.id}> possui {points} pontos!")

    @app_commands.command(name="ranking", description="Exibe o ranking dos usuários com mais pontos")
    async def ranking(self, interaction: discord.Interaction):
        users = await self.user_service.get_ranking()

        if not users:
            await interaction.response.send_message("Ainda não há usuários no ranking.", ephemeral=True)
            return

        ranking_list = []
        for i, user in enumerate(users, start=1):
            ranking_list.append(f"{i}. <@{user.discord_id}> - {user.points} pontos")

        ranking_message = "**🏆 Ranking de Pontos 🏆**\n" + "\n".join(ranking_list)
        await interaction.response.send_message(ranking_message)

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