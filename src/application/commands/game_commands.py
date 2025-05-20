import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from ..services.game_service import GameService
from ..services.user_service import UserService
from ..views.criterios_view import CriteriosView
from ..views.games_view import GamesView
from ...infrastructure.config.auth_manager import AuthorizedUsersManager
from ...infrastructure.external.whatsapp_api import WhatsAppAPI
import re
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()


class GameCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, game_service: GameService, user_service: UserService, auth_manager: AuthorizedUsersManager):
        self.bot = bot
        self.game_service = game_service
        self.user_service = user_service
        self.auth_manager = auth_manager

    @app_commands.command(name="jogos", description="Lista dos jogos cadastrados.")
    async def list_games(self, interaction: discord.Interaction, game_name: Optional[str] = None):
        games = await self.game_service.search_games(game_name)

        if not games:
            await interaction.response.send_message("Ainda não há jogos cadastrados.", ephemeral=True)
            return

        # Cria a view com paginação e pesquisa
        view = GamesView(games)
        
        # Envia a mensagem inicial com o embed da primeira página
        await interaction.response.send_message(
            embed=view.get_current_page_content(),
            view=view
        )

    @app_commands.command(name="adicionar_jogo", description="Adicione um novo jogo")
    async def add_game(self, interaction: discord.Interaction, game_name: str):
        await interaction.response.defer(thinking=True)

        success, result = await self.game_service.add_game(game_name)
        if not success:
            await interaction.followup.send(result, ephemeral=True)
            return

        game, avaliacao = result
        embed = discord.Embed(
            title=f"🎮 {game.name} foi adicionado!",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Status", value=f"✅ Jogo adicionado com sucesso! (Pontuação: {game.score})", inline=False)
        
        # Procura cada seção usando regex para garantir que encontremos tudo
        nota_match = re.search(r'Nota:([^\n]+)', avaliacao)
        criterios_match = re.search(r'Critérios para Zerar:(.*?)(?=Justificativa da Nota:|$)', avaliacao, re.DOTALL)
        justificativa_match = re.search(r'Justificativa da Nota:(.*?)$', avaliacao, re.DOTALL)

        if nota_match:
            embed.add_field(name="📊 Nota", value=f"Nota:{nota_match.group(1).strip()}", inline=False)
        
        if game.criterios:
            criterios_formatados = '\n'.join([f"• {criterio}" for criterio in game.criterios])
            embed.add_field(name="✅ Critérios para Zerar", value=criterios_formatados, inline=False)
        
        if justificativa_match:
            justificativa = justificativa_match.group(1).strip()
            embed.add_field(name="📝 Justificativa", value=justificativa, inline=False)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="zerei", description="Marque um jogo como zerado e ganhe pontos")
    async def complete_game(self, interaction: discord.Interaction, game_name: str):
        await interaction.response.defer()  # <- avisa ao Discord que você está processando

        game = await self.game_service.get_game(game_name)
        if not game:
            await interaction.followup.send(f"❌ Nenhum jogo encontrado com o nome **{game_name}**!")
            return

        # Verifica se o usuário já zerou o jogo
        user = await self.user_service.get_or_create_user(interaction.user.id)
        if user.has_completed_game(game.game_id):
            await interaction.followup.send(f"❌ Você já zerou **{game.name}**!")
            return

        if game.criterios:
            embed = discord.Embed(
                title=f"🎮 Verificação de Conclusão: {game.name}",
                description="Clique nos critérios que você completou:",
                color=discord.Color.blue()
            )

            criterios_status = [
                f"⬜ **Critério {i}:**\n{crit}"
                for i, crit in enumerate(game.criterios, 1)
            ]
            embed.add_field(name="Lista de Critérios:", value="\n\n".join(criterios_status), inline=False)

            view = CriteriosView(game.name, game.criterios, interaction.user, self.user_service)

            await interaction.followup.send(embed=embed, view=view)

            # WhatsApp em background
            asyncio.create_task(self._send_whatsapp_message(interaction.user.display_name, game))
            return

        # Fluxo sem critérios
        success, message = await self.user_service.complete_game(interaction.user.id, game_name)
        await interaction.followup.send(message)

        if success:
            asyncio.create_task(self._send_whatsapp_message(interaction.user.display_name, game))


    async def _send_whatsapp_message(self, username: str, game):
        try:
            destino = os.getenv('JID_GRUPO_SLZF')
            texto = (
                "📣 *NOVO JOGO ZERADO!*\n\n"
                "🎮 Jogador: *{username}*\n"
                "🏆 Jogo: *{game.name}*\n"
                "✨ Pontuação: *{game.score}* pontos\n\n"
                "📥 ```TEBAS BOT``` registrou a conquista!"
            )

            whatsapp = WhatsAppAPI(texto, destino)
            resposta = whatsapp.send_message()
            print("Mensagem WhatsApp enviada:", resposta)
        except Exception as e:
            print(f"[Erro WhatsApp] {e}")


    @app_commands.command(name="deletar_jogo", description="Deleta um jogo do sistema")
    @app_commands.describe(game_name="Nome do jogo a ser deletado")
    async def deletar_jogo(self, interaction: discord.Interaction, game_name: str):
        """Deleta um jogo do sistema."""
        await interaction.response.defer(ephemeral=True)
        
        if not self.auth_manager.is_authorized(interaction.user.id):
            await interaction.followup.send("Você não tem permissão para deletar jogos.", ephemeral=True)
            return
        
        # Verifica se o jogo existe
        game = await self.game_service.get_game(game_name)
        if not game:
            await interaction.followup.send(f"O jogo **{game_name}** não foi encontrado!", ephemeral=True)
            return
            
        try:
            # Tenta deletar o jogo usando a nova implementação transacional
            deleted = await self.game_service.delete_game(game.game_id)
            
            if deleted:
                await interaction.followup.send(
                    f"O jogo **{game.name}** foi deletado com sucesso.",
                    ephemeral=False
                )
            else:
                await interaction.followup.send(
                    f"Erro ao tentar deletar o jogo **{game_name}**. Por favor, tente novamente.",
                    ephemeral=True
                )
                
        except Exception as e:
            await interaction.followup.send(
                f"Ocorreu um erro ao tentar deletar o jogo **{game_name}**. Por favor, tente novamente.",
                ephemeral=True
            )

    @app_commands.command(name="ranking_zerados", description="Lista os jogos mais zerados")
    async def games_ranking(self, interaction: discord.Interaction):
        ranking = await self.user_service.get_games_ranking()

        if not ranking:
            await interaction.response.send_message("Ainda não há registros de jogos zerados.", ephemeral=True)
            return

        ranking_message = "**🎮 Ranking de Jogos Zerados 🎮**\n"
        ranking_message += "\n".join(
            [f"{i+1}. **{game}** - {count} vezes zerado(s)" for i, (game, count) in enumerate(ranking)]
        )

        await interaction.response.send_message(ranking_message) 