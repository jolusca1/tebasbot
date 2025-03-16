import discord
from typing import List, Tuple
from ...domain.models.user import User

class RankingView(discord.ui.View):
    def __init__(self, users: List[User], games_ranking: List[Tuple[str, int]]):
        super().__init__(timeout=None)
        self.users = users
        self.games_ranking = games_ranking
        self.current_view = "users"  # Pode ser "users" ou "games"

    def get_users_ranking_embed(self) -> discord.Embed:
        """Cria um embed para o ranking de usuários"""
        embed = discord.Embed(
            title="🏆 Ranking de Pontos 🏆",
            description="Os jogadores mais dedicados do servidor!",
            color=discord.Color.gold()
        )

        # Emojis para as posições
        position_emojis = ["🥇", "🥈", "🥉"]
        
        # Formata o ranking em uma única mensagem
        ranking_text = ""
        for i, user in enumerate(self.users):
            position = i + 1
            emoji = position_emojis[i] if i < 3 else "👑"
            position_str = f"`#{position}`"
            
            ranking_text += f"{position_str} {emoji} <@{user.discord_id}> • **{user.points} pontos** • {len(user.games_completed)} jogos zerados\n"
            
            # Adiciona uma linha em branco após os três primeiros lugares
            if i == 2:
                ranking_text += "\n"

        embed.description = f"{embed.description}\n\n{ranking_text}"
        
        # Adiciona um footer com estatísticas
        total_points = sum(user.points for user in self.users)
        total_games = sum(len(user.games_completed) for user in self.users)
        embed.set_footer(text=f"Total: {total_points} pontos • {total_games} jogos zerados")

        return embed

    def get_games_ranking_embed(self) -> discord.Embed:
        """Cria um embed para o ranking de jogos mais zerados"""
        embed = discord.Embed(
            title="🎮 Jogos Mais Zerados 🎮",
            description="Os jogos mais populares do servidor!",
            color=discord.Color.blue()
        )

        # Emojis para as posições
        position_emojis = ["🥇", "🥈", "🥉"]
        
        # Formata o ranking em uma única mensagem
        ranking_text = ""
        total_completions = 0
        for i, (game_name, count) in enumerate(self.games_ranking):
            position = i + 1
            emoji = position_emojis[i] if i < 3 else "🎮"
            position_str = f"`#{position}`"
            
            ranking_text += f"{position_str} {emoji} **{game_name}** • Zerado {count} vezes\n"
            total_completions += count
            
            # Adiciona uma linha em branco após os três primeiros lugares
            if i == 2:
                ranking_text += "\n"

        embed.description = f"{embed.description}\n\n{ranking_text}"
        
        # Adiciona um footer com estatísticas
        embed.set_footer(text=f"Total: {total_completions} conclusões")

        return embed

    @discord.ui.button(label="👥 Ranking de Jogadores", style=discord.ButtonStyle.primary)
    async def show_users_ranking(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_view == "users":
            await interaction.response.defer()
            return
            
        self.current_view = "users"
        await interaction.response.edit_message(embed=self.get_users_ranking_embed())

    @discord.ui.button(label="🎮 Jogos Mais Zerados", style=discord.ButtonStyle.primary)
    async def show_games_ranking(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_view == "games":
            await interaction.response.defer()
            return
            
        self.current_view = "games"
        await interaction.response.edit_message(embed=self.get_games_ranking_embed()) 