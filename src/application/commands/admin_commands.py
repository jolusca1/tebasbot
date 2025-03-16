import discord
from discord import app_commands
from discord.ext import commands
from ...infrastructure.config.auth_manager import AuthorizedUsersManager
import os
from dotenv import load_dotenv

load_dotenv()

class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, auth_manager: AuthorizedUsersManager):
        self.bot = bot
        self.auth_manager = auth_manager
        self.bot_owner_id = int(os.getenv("BOT_OWNER_ID", "0"))

    # comando para autorizar um usuário a usar comandos administrativos
    @app_commands.command(name="autorizar", description="Autoriza um usuário a usar comandos administrativos")
    async def authorize_user(self, interaction: discord.Interaction, user: discord.User):
        # Apenas o dono do bot pode autorizar outros usuários
        if interaction.user.id != self.bot_owner_id:
            await interaction.response.send_message("❌ Apenas o dono do bot pode autorizar usuários.", ephemeral=True)
            return

        if self.auth_manager.is_authorized(user.id):
            embed = discord.Embed(
                title="⚠️ Usuário já Autorizado",
                description=f"{user.mention} já possui privilégios administrativos.",
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if self.auth_manager.add_user(user.id):
            embed = discord.Embed(
                title="✅ Usuário Autorizado com Sucesso",
                description=f"{user.mention} recebeu privilégios administrativos.",
                color=discord.Color.green()
            )
            
            # Adiciona campo explicando os privilégios
            embed.add_field(
                name="🛡️ Privilégios Concedidos",
                value=(
                    "O usuário agora pode:\n"
                    "• Deletar jogos do sistema\n"
                    "• Ver a lista de usuários autorizados\n"
                    "• Gerenciar permissões do bot\n"
                    "• Acessar comandos administrativos"
                ),
                inline=False
            )
            
            # Adiciona campo com observações importantes
            embed.add_field(
                name="⚠️ Observações Importantes",
                value=(
                    "• Use estes privilégios com responsabilidade\n"
                    "• Todas as ações administrativas são registradas\n"
                    "• Em caso de uso indevido, os privilégios podem ser revogados"
                ),
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Erro ao Autorizar",
                description="Ocorreu um erro ao tentar autorizar o usuário. Por favor, tente novamente.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="desautorizar", description="Remove a autorização de um usuário")
    async def unauthorize_user(self, interaction: discord.Interaction, user: discord.User):
        # Apenas o dono do bot pode remover autorizações
        if interaction.user.id != self.bot_owner_id:
            await interaction.response.send_message("❌ Apenas o dono do bot pode remover autorizações.", ephemeral=True)
            return

        if not self.auth_manager.is_authorized(user.id):
            await interaction.response.send_message(f"⚠️ {user.mention} não está autorizado.", ephemeral=True)
            return

        if self.auth_manager.remove_user(user.id):
            await interaction.response.send_message(f"✅ Autorização de {user.mention} foi removida com sucesso!")
        else:
            await interaction.response.send_message("❌ Erro ao remover autorização.", ephemeral=True)

    @app_commands.command(name="autorizados", description="Lista os usuários autorizados")
    async def list_authorized(self, interaction: discord.Interaction):
        """Lista todos os usuários autorizados."""
        if not self.auth_manager.is_authorized(interaction.user.id):
            await interaction.response.send_message("Você não tem permissão para ver a lista de usuários autorizados.", ephemeral=True)
            return

        authorized_ids = self.auth_manager.get_authorized_users()
        if not authorized_ids:
            await interaction.response.send_message("Não há usuários autorizados.", ephemeral=True)
            return

        # Prepara a mensagem com a lista de usuários
        message = "**Lista de Usuários Autorizados:**\n\n"
        for user_id in authorized_ids:
            try:
                # Tenta buscar o usuário no cache primeiro
                user = self.bot.get_user(user_id)
                if not user:
                    # Se não estiver no cache, busca via API
                    user = await self.bot.fetch_user(user_id)
                
                if user:
                    message += f"• {user.mention} (ID: {user_id})\n"
                else:
                    message += f"• Usuário não encontrado (ID: {user_id})\n"
            except Exception as e:
                message += f"• Erro ao buscar usuário (ID: {user_id})\n"

        await interaction.response.send_message(message) 