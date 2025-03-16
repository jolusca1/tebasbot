import discord
from ..services.user_service import UserService

class CriteriosView(discord.ui.View):
    def __init__(self, game_name: str, criterios: list, user: discord.User, user_service: UserService, timeout=180):
        super().__init__(timeout=timeout)
        self.game_name = game_name
        self.criterios = criterios
        self.user = user
        self.user_service = user_service
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
            success, message = await self.user_service.complete_game(self.user.id, self.game_name)
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