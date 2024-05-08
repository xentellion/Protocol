import os
import json
import src.character_data as char_data


class JsonDataControl:
    async def get_file(path) -> char_data.DnDServer:
        try:
            with open(path, "r") as file:
                data = file.read().replace("\n", "")
        except FileNotFoundError:
            print("New DnD server!")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "a+") as file:
                file.write(char_data.DnDServer().toJSON())
                data = file.read().replace("\n", "")

        c_camp = char_data.DnDServer(**json.loads(data))
        c_camp.campaigns = list(map(char_data.Campaign.fromdict, c_camp.campaigns))
        for camp in c_camp.campaigns:
            camp.characters = list(map(char_data.Character.fromdict, camp.characters))
        return c_camp

    def save_update(path, data) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as file:
            file.write(data.toJSON())
