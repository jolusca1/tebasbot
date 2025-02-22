import os
from dotenv import load_dotenv
import requests
from steam_web_api import Steam

load_dotenv()

STEAM_TOKEN = os.getenv("STEAM_API_KEY")
steam = Steam(STEAM_TOKEN)

def get_steam_profile(name):
    user = steam.users.search_user(name)

    return user

def get_games_played_recently(steam_id):
    games_played = steam.users.get_user_recently_played_games(steam_id=steam_id)
    return games_played