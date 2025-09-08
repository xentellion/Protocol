import json


class Characteristic:
    def __init__(self, value: int = -1, max_value: int = -1, has_max: bool = False):
        self.value = value
        self.max_value = max_value
        self.has_max = has_max

    def __str__(self) -> str:
        return json.dumps(self.__dict__, indent=4)


class Character:
    def __init__(self, author: int, stats: dict[str, Characteristic] = {}):
        self.author = author
        self.stats = {k: Characteristic(**v) for k, v in stats.items()}

    def __str__(self) -> str:
        return json.dumps(self.__dict__, indent=4)


class Campaign:
    def __init__(self, stats: dict[str, Characteristic] = {}, characters: dict[str, Character] = {}):
        self.characters = {k: Character(**v) for k, v in characters.items()}
        self.stats = {k: Characteristic(**v) for k, v in stats.items()}

    def __len__(self):
        return len(self.characters.keys())

    def __setitem__(self, key, value):
        self.characters[key] = value

    def __getitem__(self, key):
        return self.characters[key]

    def __delitem__(self, key):
        self.characters.pop(key)

    def __contains__(self, item):
        return item in self.characters

    def __iter__(self):
        for v in self.characters:
            yield (v, self.__getitem__(v))

    def __str__(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)


class DnDServer:
    def __init__(self, current_c: str = "", campaigns: dict[str, Campaign] = {}):
        self.current_c = current_c
        self.campaigns = {k: Campaign(**v) for k, v in campaigns.items()}

    def __str__(self) -> str:
        return self.toJSON()

    def toJSON(self) -> str:
        return json.dumps(
            self, default=lambda o: o.__dict__, indent=4, ensure_ascii=False
        )
