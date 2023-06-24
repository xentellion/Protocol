import os
import json
import character_data


class JsonDataControl:
    async def get_file(path) -> character_data.DnDServer:
        try:
            with open(path, 'r') as file:
                data = file.read().replace('\n', '')
        except FileNotFoundError:
            print('New DnD server!')
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'a+') as file:
                file.write(character_data.DnDServer().toJSON())
                data = file.read().replace('\n', '')
            
        current_c = character_data.DnDServer(**json.loads(data))
        current_c.campaigns = [character_data.Campaign.fromdict(x) for x in current_c.campaigns]
        for camp in current_c.campaigns:
            camp.characters = [character_data.Character.fromdict(x) for x in camp.characters]
        return current_c

    def save_update(path, data) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as file:
            file.write(data.toJSON())