import discord
from discord import app_commands
from discord.ext import commands
from ..services.valorant_service import ValorantService
from ...domain.models.valorant import ValorantPlayer
from ...utils.translator_elo import translate_elo


class ValorantCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, valorant_service: ValorantService):
        self.bot = bot
        self.valorant_service = valorant_service

    @app_commands.command(name="buscar_conta_valorant", description="Cadastrar sua conta VALORANT no ranking")
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

        player_valorant = ValorantPlayer(
            name=name,
            tag=tag,
            region=region.value,
            elo="",
            mmr_last_match=0,
            current_mmr=0,
            image="",
            highest_rank=""
        )

        player_valorant_data = await self.valorant_service.get_player_valorant(player_valorant)

        if not player_valorant_data:
            embed = discord.Embed(
                title="❌ Erro ao cadastrar",
                description="Não conseguimos encontrar essa conta na API da Riot. Verifique se o `nome#tag` e a região estão corretos.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed)
            return
        
        player_valorant = ValorantPlayer(
            name=player_valorant_data.get('name'),
            tag=player_valorant_data.get('tag'),
            region=region.value,
            elo=player_valorant_data.get('elo'),
            mmr_last_match=player_valorant_data.get('mmr_last_match'),
            current_mmr=player_valorant_data.get('current_mmr'),
            image=player_valorant_data.get('image'),
            highest_rank=player_valorant_data.get('highest_rank')
        )
        
        # Update the database with API data only
        await self.valorant_service.update_player_ranking(player_valorant)


        embed = discord.Embed(
            title=f"🎖️ Perfil VALORANT",
            description=(
                f"**Jogador:** `{player_valorant.name}#{player_valorant.tag}`\n"
                f"**Região:** `{region.name}`\n"
            ),
            color=discord.Color.from_rgb(255, 0, 128)
        )

        embed.set_footer(text="tebasbot • Valorant Ranking", icon_url=self.bot.user.display_avatar.url)
        embed.timestamp = interaction.created_at

        embed.add_field(name="🏆 Elo atual", value=f"**{translate_elo(player_valorant.elo)}**", inline=False)
        embed.add_field(name="📈 Última partida", value=f"**{player_valorant.mmr_last_match}** RR", inline=False)
        embed.add_field(name="🔝 Elo mais alto", value=f"**{player_valorant.highest_rank}**", inline=False)

        await interaction.edit_original_response(embed=embed)

    @app_commands.command(name="ranking_valorant", description="Veja o ranking dos jogadores com maior elo do servidor!")
    async def ranking_valorant(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        ELO_ORDER = {
            "Iron 1": 1, "Iron 2": 2, "Iron 3": 3,
            "Bronze 1": 4, "Bronze 2": 5, "Bronze 3": 6,
            "Silver 1": 7, "Silver 2": 8, "Silver 3": 9,
            "Gold 1": 10, "Gold 2": 11, "Gold 3": 12,
            "Platinum 1": 13, "Platinum 2": 14, "Platinum 3": 15,
            "Diamond 1": 16, "Diamond 2": 17, "Diamond 3": 18,
            "Ascendant 1": 19, "Ascendant 2": 20, "Ascendant 3": 21,
            "Immortal 1": 22, "Immortal 2": 23, "Immortal 3": 24,
            "Radiant": 25
        }
            
        # Busca todos os jogadores do banco de dados
        players = await self.valorant_service.get_all_players()
        ranking = []

        for player in players:
            ranking.append({
                "name": player.name,
                "tag": player.tag,
                "elo": player.elo,
                "current_mmr": player.current_mmr,
                "image": player.image
            })

        # Ordena o ranking com base no elo e current_mmr
        ranking.sort(key=lambda x: (ELO_ORDER.get(x["elo"], 0), x.get("current_mmr", 0)), reverse=True)

        embed = discord.Embed(
            title="🏆 Ranking Valorant (Elo)",
            description="Confira os jogadores mais bem ranqueados!",
            color=discord.Color.gold()
        )

        for i, player in enumerate(ranking, start=1):
            embed.add_field(
                name=f"{i}. {player['name']}#{player['tag']}",
                value=f"**Elo:** {translate_elo(player['elo'])} - {player['current_mmr']} pontos",
                inline=False
            )
        
        if ranking:
            embed.set_thumbnail(url=ranking[0]["image"])

        await interaction.edit_original_response(embed=embed)

    @staticmethod
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
