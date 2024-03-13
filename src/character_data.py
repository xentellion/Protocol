import math
import json


class Character:
    @classmethod
    def fromdict(cls, d):
        df = {k: v for k, v in d.items()}
        return cls(**df)

    def __init__(
        self,
        name: str,
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
        self.name = name
        self.author = author
        self.hp = hp
        self.max_hp = max_hp
        self.energy = energy
        self.max_energy = max_energy
        self.reaction = reaction
        self.max_reaction = max_reaction
        self.style = style
        self.max_style = max_style

    def small_rest(self):
        self.heal_hp(math.ceil(self.max_hp / 4))
        self.give_energy(math.ceil(self.max_hp / 2))

    def big_rest(self):
        self.heal_hp(math.ceil(self.max_hp / 2))
        self.give_energy(self.max_hp)


class Campaign:
    @classmethod
    def fromdict(cls, d):
        df = {k: v for k, v in d.items()}
        return cls(**df)

    def __init__(self, name: str, characters=[]):
        self.name = name
        self.characters = characters

    def add_character(self, char: Character):
        self.characters.append(char)
        self.characters = sorted(self.characters, key=lambda x: x.name)

    def remove_character(self, char: str):
        self.characters.remove(
            next((x for x in self.characters if x.name == char), None)
        )

    def check_character(self, char: str):
        return any((x for x in self.characters if x.name == char))

    def get_character(self, char: str):
        return next((x for x in self.characters if x.name == char), None)


class DnDServer:
    def __init__(self, current_c="", campaigns=[]):
        self.current_c = current_c
        self.campaigns = campaigns

    def add_campain(self, name):
        self.campaigns.append(Campaign(name))

    def remove_campain(self, name):
        self.campaigns.remove(next((x for x in self.campaigns if x.name == name), None))

    def find_campain(self, name):
        return any(x for x in self.campaigns if x.name == name)

    def get_campain(self, name) -> Campaign:
        return next(x for x in self.campaigns if x.name == name)

    def update_campaign(self, camp: Campaign):
        self.campaigns = [camp if x.name == camp.name else x for x in self.campaigns]

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
