import discord
from typing import List
from ...domain.models.game import Game

class GameInfoView(discord.ui.View):
    def __init__(self, game: Game, all_games: List[Game], current_page: int):
        super().__init__(timeout=None)
        self.game = game
        self.all_games = all_games
        self.current_page = current_page

    def get_info_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=f"🎮 {self.game.name}",
            description=f"Informações detalhadas sobre o jogo",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📊 Pontuação",
            value=f"{self.game.score} pontos",
            inline=False
        )
        
        if self.game.criterios:
            criterios_formatados = "\n".join([f"• {criterio}" for criterio in self.game.criterios])
            embed.add_field(
                name="✅ Critérios para Zerar",
                value=criterios_formatados,
                inline=False
            )
        else:
            embed.add_field(
                name="✅ Critérios para Zerar",
                value="Nenhum critério específico definido.",
                inline=False
            )
        
        return embed

    @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.secondary)
    async def voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        games_view = GamesView(self.all_games)
        games_view.current_page = self.current_page
        await interaction.response.edit_message(embed=games_view.get_current_page_content(), view=games_view)

class GamesView(discord.ui.View):
    def __init__(self, games: List[Game], items_per_page: int = 10):
        super().__init__(timeout=None)
        self.games = games
        self.current_page = 0
        self.items_per_page = items_per_page
        self.total_pages = max(1, (len(self.games) - 1) // items_per_page + 1)
        
        # Adiciona o select menu
        self.add_item(self.get_games_select())
        # Adiciona os botões de navegação
        self.update_navigation_buttons()

    def get_current_page_content(self) -> discord.Embed:
        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        current_games = self.games[start_idx:end_idx]

        embed = discord.Embed(
            title="🎮 Lista de Jogos",
            description="Selecione um jogo para ver mais detalhes:",
            color=discord.Color.blue()
        )

        if not current_games:
            embed.add_field(
                name="Sem jogos",
                value="Nenhum jogo encontrado nesta página.",
                inline=False
            )
        else:
            for i, game in enumerate(current_games, start=1):
                embed.add_field(
                    name=f"{i}. {game.name}",
                    value=f"Pontuação: {game.score} pontos\nClique no menu abaixo para ver os critérios",
                    inline=False
                )

        total_jogos = len(self.games)
        embed.set_footer(text=f"Página {self.current_page + 1} de {self.total_pages} • Total: {total_jogos} jogos")
        return embed

    def get_games_select(self) -> discord.ui.Select:
        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        current_games = self.games[start_idx:end_idx]

        select = discord.ui.Select(
            placeholder="Escolha um jogo para ver os detalhes...",
            min_values=1,
            max_values=1,
            custom_id="games_select"
        )

        for i, game in enumerate(current_games):
            select.add_option(
                label=game.name[:100],  # Discord limit
                value=str(i),
                description=f"Pontuação: {game.score} pontos",
                emoji="🎮"
            )

        async def select_callback(interaction: discord.Interaction):
            selected_index = int(select.values[0])
            selected_game = current_games[selected_index]
            view = GameInfoView(selected_game, self.games, self.current_page)
            await interaction.response.edit_message(embed=view.get_info_embed(), view=view)

        select.callback = select_callback
        return select

    def update_navigation_buttons(self):
        # Remove botões antigos de navegação
        for item in self.children[:]:
            if isinstance(item, discord.ui.Button):
                self.remove_item(item)
        
        # Adiciona os novos botões
        self.add_item(self.get_previous_button())
        self.add_item(self.get_next_button())

    def get_previous_button(self):
        button = discord.ui.Button(
            label="◀️ Anterior",
            style=discord.ButtonStyle.primary,
            disabled=self.current_page == 0,
            custom_id="previous"
        )
        button.callback = self.previous_page_callback
        return button

    def get_next_button(self):
        button = discord.ui.Button(
            label="▶️ Próxima",
            style=discord.ButtonStyle.primary,
            disabled=self.current_page >= self.total_pages - 1,
            custom_id="next"
        )
        button.callback = self.next_page_callback
        return button

    async def previous_page_callback(self, interaction: discord.Interaction):
        self.current_page = max(0, self.current_page - 1)
        # Atualiza o select menu e os botões
        self.clear_items()
        self.add_item(self.get_games_select())
        self.update_navigation_buttons()
        await interaction.response.edit_message(embed=self.get_current_page_content(), view=self)

    async def next_page_callback(self, interaction: discord.Interaction):
        self.current_page = min(self.total_pages - 1, self.current_page + 1)
        # Atualiza o select menu e os botões
        self.clear_items()
        self.add_item(self.get_games_select())
        self.update_navigation_buttons()
        await interaction.response.edit_message(embed=self.get_current_page_content(), view=self) 