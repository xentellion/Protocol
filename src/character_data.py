import json


class Character:
    def __init__(
        self,
        author: int,
        hp: int = 10,
        max_hp: int = 10,
        energy: int = 2,
        max_energy: int = 2,
        reaction: int = 0,
        max_reaction: int = 0,
        style: int = 0,
        max_style: int = 0,
    ):
        self.author = author
        self.hp = hp
        self.max_hp = max_hp
        self.energy = energy
        self.max_energy = max_energy
        self.reaction = reaction
        self.max_reaction = max_reaction
        self.style = style
        self.max_style = max_style


class Campaign:
    def __init__(self, characters: dict[str, Character] = {}):
        self.characters = characters

    def __len__(self):
        return len(self.characters.keys())

    def __setitem__(self, key, value):
        self.characters[key] = value

    def __getitem__(self, key):
        return Character(**self.characters[key])

    def __delitem__(self, key):
        self.characters.pop(key)

    def __contains__(self, item):
        return item in self.characters

    def __iter__(self):
        for v in self.characters:
            yield (v, self.__getitem__(v))

    def __str__(self) -> str:
        return json.dumps(self.characters, default=lambda o: o.__dict__, indent=4)


class DnDServer:
    def __init__(self, current_c: str = "", campaigns: dict[str, Campaign] = {}):
        self.current_c = current_c
        self.campaigns = campaigns

    def __str__(self) -> str:
        return self.toJSON()

    def toJSON(self) -> str:
        return json.dumps(
            self, default=lambda o: o.__dict__, indent=4, ensure_ascii=False
        )
