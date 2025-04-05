import os 
import re
import requests
from dotenv import load_dotenv


load_dotenv()


class ValorantAPI:
    def __init__(self):
        self.access_token = os.getenv('VALORANT_API_TOKEN')
        self.url: str = 'https://api.henrikdev.xyz/valorant'
        self.version: str = 'v2'

    def get_mmr_by_player(self, name: str, tag: str, region: str):
        endpoint = 'mmr'
        try:

            headers = {
                "accept": "application/json",
                "Authorization": "HDEV-72ec20fa-f1a7-4e17-9616-df21e1131134"
            }

            response = requests.get(f'{self.url}/{self.version}/{endpoint}/{region}/{name}/{tag}', headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ocorreu um erro ao processar: {e}")
            return