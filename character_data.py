import math
import json
import enum

class Conditions(enum.Enum):
        Alive = 0
        Middle_Wound = 1
        Heavy_Wound = 2
        Coma = 3
        Dead = 4

class Character: 
    @classmethod
    def fromdict(cls, d):
        df = {k : v for k, v in d.items()}
        return cls(**df)

    def __init__(self, name:str, author:int, 
                hp: int = 6, max_hp:int = 6,
                energy: int = 2, max_energy:int = 2,
                money:int = 0,
                inventory:str = '', notes:str = '',
                another:bool = False, status = Conditions.Alive):
        self.name = name
        self.author = author
        self.hp = hp
        self.max_hp = max_hp
        self.energy = energy
        self.max_energy = max_energy
        self.money = money
        self.inventory = inventory
        self.notes = notes
        self.another = another
        self.status = status

    def damage_hp(self, change: int):
        self.hp -= change
        self.status_change()

    def heal_hp(self, change: int):
        self.hp += change
        self.status_change()
    
    def resurrect(self):
        self.hp = math.ceil(self.max_hp / 2)
        self.status = Character.Conditions.Middle_Wound

    def set_hp(self, hp:int):
        self.max_hp = hp
        self.hp = hp

    def give_energy(self, energy: int):
        self.energy += energy
        if self.energy > self.max_energy:
            self.energy = self.max_energy

    def spend_energy(self, energy: int):
        self.energy -= energy
        if self.energy < 0:
            self.energy += energy

    def set_energy(self, energy:int):
        self.max_energy = energy
        self.energy = energy

    def change_money(self, money:int):
        self.money += money
        if self.money < 0:
            self.money -= money

    def small_rest(self):
        self.heal_hp(math.ceil(self.max_hp / 4))
        self.give_energy(math.ceil(self.max_hp / 2))
        self.status_change()
    
    def big_rest(self):
        self.heal_hp(math.ceil(self.max_hp / 2))
        self.give_energy(self.max_hp)
        self.status_change()

    def update_inventory(self, text):
        self.inventory = text

    def update_notes(self, text):
        self.notes = text

    def status_change(self):
        try:
            hp_prop = self.max_hp / self.hp
        except ZeroDivisionError:
            hp_prop = self.max_hp + 1
            
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        elif self.hp <= 0:
            if self.another:
                self.status = Character.Conditions.Dead
            elif hp_prop > -2:
                self.status = Character.Conditions.Dead
            else:
                self.status = Character.Conditions.Coma
            self.hp = 0
        else:
            if hp_prop > 1.5:
                if hp_prop < 3:
                    self.status = Character.Conditions.Heavy_Wound  
                else: 
                    self.status = Character.Conditions.Middle_Wound
            else:
                self.status = Character.Conditions.Alive


class Campaign:
    @classmethod
    def fromdict(cls, d):
        df = {k : v for k, v in d.items()}
        return cls(**df)

    def __init__(self, name:str, characters = []):
        self.name = name
        self.characters = characters

    def add_character(self, char:Character):
        self.characters.append(char)
        self.characters = sorted(self.characters, key=lambda x: x.name)

    def remove_character(self, char:Character):
        self.characters.remove(next((x for x in self.characters if x['name'] == char.name), None))


class DnDServer:
    def __init__(self, current_c = "", campaigns = []):
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

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        