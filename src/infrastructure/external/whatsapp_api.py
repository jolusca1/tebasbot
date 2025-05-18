import os 
import re
import requests
from dotenv import load_dotenv

load_dotenv()


class WhatsAppAPI:
    def __init__(self, mensagem, contato):
        self.url = os.getenv('URL_WHATSAPP')
        self.mensagem = mensagem
        self.contato = contato
        self.instance = os.getenv('INSTANCE_WHATSAPP')
        self.api_key = os.getenv('API_KEY_WHATSAPP')

    def send_message(self):
        endpoint = 'message/sendText'

        headers = {
            "accept": "application/json",
            "apikey": self.api_key
        }

        payload = {
            "number": self.contato,
            "options": {
                "delay": 10,
                "presence": "composing",
                "linkPreview": True,
                "quoted": {
                    "key": {
                        "remoteJid": "123",
                        "fromMe": True,
                        "id": "1",
                        "participant": "<string>"
                    },
                    "message": {
                        "conversation": "E aí!"
                    }
                },
                "mentions": {
                    "everyOne": False,
                    "mentioned": []
                }
            },
            "text": self.mensagem
        }

        try:
            uri = f"{self.url}/{endpoint}/{self.instance}"
            response = requests.post(uri, headers=headers, json=payload)
            print(response)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as ex:
            raise Exception(f"Ocorreu um erro ao processar: {ex}")
            return