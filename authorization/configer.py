import json
import os
from dotenv import load_dotenv

load_dotenv()

class AuthorizedUsersManager:
    def __init__(self, filename=os.getenv("PATH_AUTH")):
        self.filename = filename
        self.authorized_ids = self.load_authorized_ids()

    def load_authorized_ids(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                data = json.load(f)
                return data.get("authorized_ids", [])
        return []

    def save_authorized_ids(self):
        with open(self.filename, "w") as f:
            json.dump({"authorized_ids": self.authorized_ids}, f, indent=4)

    def is_authorized(self, user_id: int) -> bool:
        return user_id in self.authorized_ids

    def add_user(self, user_id: int):
        if user_id not in self.authorized_ids:
            self.authorized_ids.append(user_id)
            self.save_authorized_ids()

    def remove_user(self, user_id: int):
        if user_id in self.authorized_ids:
            self.authorized_ids.remove(user_id)
            self.save_authorized_ids()
