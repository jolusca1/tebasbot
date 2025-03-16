import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

STEAM_API_KEY = os.getenv("STEAM_API_KEY")

def get_steam_profile(name: str) -> Dict[str, Any]:
    """Busca um perfil da Steam pelo nome"""
    try:
        # Primeiro, busca o ID da Steam pelo nome
        vanity_url = f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={STEAM_API_KEY}&vanityurl={name}"
        response = requests.get(vanity_url)
        data = response.json()

        if data["response"]["success"] == 1:
            steamid = data["response"]["steamid"]
        else:
            return "No match"

        # Depois, busca os detalhes do perfil usando o ID
        profile_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steamid}"
        response = requests.get(profile_url)
        data = response.json()

        if data["response"]["players"]:
            return {"player": data["response"]["players"][0]}
        return "No match"

    except Exception as e:
        print(f"Erro ao buscar perfil da Steam: {e}")
        return "No match"

def get_games_played_recently(steamid: str) -> Dict[str, Any]:
    """Busca os jogos recentemente jogados por um usuário"""
    try:
        url = f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={STEAM_API_KEY}&steamid={steamid}&format=json"
        response = requests.get(url)
        data = response.json()

        if "response" in data and "games" in data["response"]:
            return data["response"]
        return {"games": []}

    except Exception as e:
        print(f"Erro ao buscar jogos recentes: {e}")
        return {"games": []} 