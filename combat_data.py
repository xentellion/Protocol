import json

class Actor:
    def __init__(self, name: str, author, initiative: int):
        self.name = name
        self.author = author
        self.initiative = initiative

class Combat:
    def __init__(self, *args):
        if len(args) == 1:
            self.__dict__ = args[0]
        else:
            self.channel = args[0]
            self.message = args[1]
            self.round = 0
            self.turn = 0
            self.actors = []
        
    def add_actors(self, actor):
        self.actors.append(actor)
        self.actors = sorted(self.actors, key=lambda x: x['initiative'], reverse=True)

    def remove_actors(self, actor: str):
        self.actors.remove(next((x for x in self.actors if x['name'] == actor), None))

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
        return next((x for x in self.actors if x['name'] == name), None)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
                