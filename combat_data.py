import math
import json
import enum
import itertools

class Actor:
    @classmethod
    def fromdict(cls, d):
        df = {k : v for k, v in d.items()}
        return cls(**df)

    def __init__(self, name: str, author, initiative: int):
        self.name = name
        self.author = author
        self.initiative = initiative

class Combat:
    def __init__(self, channel, message, round:int=0, turn:int=0,  actors=[]):
        self.channel = channel
        self.message = message
        self.round = round
        self.turn = turn
        self.actors = actors  
        
    def add_actors(self, actor):
        self.actors.append(actor)
        self.actors = sorted(self.actors, key=lambda x: x.initiative, reverse=True)

    def remove_actors(self, actor: str):
        self.actors.remove(next((x for x in self.actors if x.name == actor), None))

    def next_turn(self):
        if self.round == 0:
            self.round = 1
            self.turn = 0
        else:
            self.turn += 1
            if self.turn == len(self.actors):
                self.round += 1
                self.turn = 0

    def get_current(self):
        return self.actors[self.turn]

    def get_actor(self, name):
        return next((x for x in self.actors if x.name == name), None)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class Character: 
    def __init__(self, name:str, author:int):
        self.name = name
        self.author = author
        self.hp = 6
        self.max_hp = 6
        self.energy = 2
        self.max_energy = 2
        self.money = 0
        self.inventory = ''
        self.notes = ''
        self.another = False
        self.status = Character.Conditions.Alive

    class Conditions(enum.Enum):
        Alive = 0
        Middle_Wound = 1
        Heavy_Wound = 2
        Coma = 3
        Dead = 4

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


class Campain:
    def __init__(self, name:str):
        self.name = name
        self.characters = []

    def add_character(self, char:Character):
        self.characters.append(char)
        self.characters = sorted(self.characters, key=lambda x: x['name'])

    def remove_character(self, char:Character):
        self.characters.remove(next((x for x in self.characters if x['name'] == char.name), None))

class DnDServer:
    def __init__(self):
        self.current_c = 0
        self.companies = []
        