import asyncio
import schedule
import time
import logging
from src.infrastructure.external.valorant_api import ValorantAPI
from src.infrastructure.database.mongodb.repositories.mongo_valorant_repository import MongoValorantRepository
from src.domain.models.valorant import ValorantPlayer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('player_update_routine')

async def update_player_data():
    valorant_api = ValorantAPI()
    repository = MongoValorantRepository()

    logger.info("Fetching all players from the database")
    players = await repository.get_all_players()
    logger.info(f"Retrieved {len(players)} players from the database")

    for player in players:
        logger.info(f"Fetching MMR data for player: {player.name}#{player.tag}")
        player_data = valorant_api.get_mmr_by_player(player.name, player.tag, player.region)
        
        if player_data.get("status") == 200:
            logger.info(f"Successfully retrieved data for player: {player.name}#{player.tag}")
            updated_player = ValorantPlayer(
                name=player_data.get("data").get("name"),
                tag=player_data.get("data").get("tag"),
                region=player.region,
                elo=player_data.get("data").get("current_data").get("currenttierpatched"),
                mmr_last_match=player_data.get("data").get("current_data").get("mmr_change_to_last_game"),
                current_mmr=player_data.get("data").get("current_data").get("ranking_in_tier"),
                image=player_data.get("data").get("current_data").get("images").get("large"),
                highest_rank=player_data.get("data").get("highest_rank").get("patched_tier")
            )
            logger.info(f"Current MMR for {player.name}#{player.tag}: {updated_player.current_mmr}")
            await repository.update_user(updated_player)
            logger.info(f"Updated player data for: {player.name}#{player.tag}")
        else:
            logger.warning(f"Failed to retrieve data for player: {player.name}#{player.tag}, status: {player_data.get('status')}")
            pass
            
        logger.info(f"Waiting 5 seconds before processing the next player")
        await asyncio.sleep(5)

def schedule_updates():
    logger.info("Running initial player data update")
    asyncio.run(update_player_data())  # Run the update immediately

    logger.info("Scheduling player data updates every 10 minutes")
    schedule.every(10).minutes.do(lambda: asyncio.run(update_player_data()))

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    logger.info("Starting Valorant players update service")
    schedule_updates()
