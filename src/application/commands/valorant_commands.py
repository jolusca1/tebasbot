import discord
from discord import app_commands
from discord.ext import commands
from ..services.valorant_service import ValorantService


class ValorantCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, valorant_service: ValorantService):
        self.bot = bot
        self.valorant_service = valorant_service

    @app_commands.command(name="cadastrar_conta_valorant", description="Cadastrar sua conta VALORANT no ranking")
    @app_commands.choices(region=[
        app_commands.Choice(name="Brasil", value="br"),
        app_commands.Choice(name="América do Norte", value="na"),
        app_commands.Choice(name="Europa", value="eu"),
        app_commands.Choice(name="Ásia", value="ap"),
        app_commands.Choice(name="LATAM", value="latam"),
        app_commands.Choice(name="Coreia do Sul", value="kr")
    ])
    async def cadastrar_player(self, interaction: discord.Interaction, name: str, tag: str, region: app_commands.Choice[str]):
        await interaction.response.defer(thinking=True)

        result = await self.valorant_service.get_or_create_player(
            name, tag, region.value
        )

        if result:
            player_valorant = await self.valorant_service.get_player_valorant(result);

            print(player_valorant)

            if not player_valorant:
                embed = discord.Embed(
                    title="❌ Erro ao cadastrar",
                    description="Não conseguimos encontrar essa conta na API da Riot. Verifique se o `nome#tag` e a região estão corretos.",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed)
                return


        embed = discord.Embed(
            title=f"🎖️ Perfil VALORANT",
            description=(
                f"**Jogador:** `{player_valorant.get('name')}#{player_valorant.get('tag')}`\n"
                f"**Região:** `{region.name}`\n"
            ),
            color=discord.Color.from_rgb(255, 0, 128)
        )

        embed.set_thumbnail(url=player_valorant.get("image"))
        embed.set_footer(text="tebasbot • Valorant Ranking", icon_url=self.bot.user.display_avatar.url)
        embed.timestamp = interaction.created_at

        embed.add_field(name="🏆 Elo atual", value=f"**{player_valorant.get('elo')}**", inline=False)
        embed.add_field(name="📈 Última partida", value=f"**{player_valorant.get('mmr_last_match')}** RR", inline=False)
        embed.add_field(name="🔝 Elo mais alto", value=f"**{player_valorant.get('highest_rank')}**", inline=False)

        await interaction.edit_original_response(embed=embed)

    def elo_to_emoji(elo: str) -> str:
        emojis = {
            "Iron": "🔩", "Bronze": "🥉", "Silver": "🥈", "Gold": "🥇",
            "Platinum": "💎", "Diamond": "🔷", "Ascendant": "🌟",
            "Immortal": "🔥", "Radiant": "🌈"
        }
        for key, emoji in emojis.items():
            if key.lower() in elo.lower():
                return emoji
        return "❔"
