import asyncio
import schedule
import time
import logging
from src.infrastructure.database.mongodb.repositories.mongo_valorant_repository import MongoValorantRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ranking_update_routine')

async def update_rankings():
    """
    Updates player rankings based on their ELO scores.
    Fetches all players from the database, sorts them by ELO,
    and saves the updated ranking back to the database.
    """
    try:
        logger.info("Starting ranking update process")
        repository = MongoValorantRepository()

        # Fetch all players from the database
        players = await repository.get_all_players()
        logger.info(f"Retrieved {len(players)} players from database")
        
        # Calculate player rankings based on ELO score (descending order)
        ranking = sorted(players, key=lambda p: p.elo, reverse=True)

        # Assign rank positions to players
        for i, player in enumerate(ranking):
            player.rank = i + 1

        # Save the updated ranking to the database
        await repository.save_player_ranking(ranking)
        logger.info("Ranking update completed successfully")
    except Exception as e:
        logger.error(f"Error updating rankings: {str(e)}")

def schedule_ranking_updates(interval_minutes=1):
    """
    Schedules periodic ranking updates at specified intervals.
    
    Args:
        interval_hours (int): How often to update rankings, in hours. Default is 1.
    """
    logger.info(f"Setting up ranking updates every {interval_minutes} minute(s)")
    
    # Run an initial update immediately
    asyncio.run(update_rankings())
    
    # Schedule recurring updates
    schedule.every(interval_minutes).minutes.do(lambda: asyncio.run(update_rankings()))
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check for pending tasks every minute
    except KeyboardInterrupt:
        logger.info("Ranking update service stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error in ranking update scheduler: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting Valorant ranking update service")
    schedule_ranking_updates()
