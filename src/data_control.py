import os
import json
from src.character_data import DnDServer


class JsonDataControl:
    async def get_file(path) -> DnDServer:
        try:
            with open(path, "r") as file:
                data = file.read().replace("\n", "")
        except FileNotFoundError:
            print("New DnD server!")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as file:
                server = DnDServer()
                file.write(server.toJSON())
                return server
        return DnDServer(**json.loads(data))

    def save_update(path: str, data) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as file:
            file.write(data.toJSON())
