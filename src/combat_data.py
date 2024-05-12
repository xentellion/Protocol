import json


class Actor:
    def __init__(self, name: str, author, initiative: int):
        self.name = name
        self.author = author
        self.initiative = initiative

    def __str__(self) -> str:
        return json.dumps(self.__dict__, indent=4)


class Combat:
    def __init__(
        self,
        channel,
        message,
        round: int = 0,
        turn: int = 0,
        actors: list[Actor] = [],
        temp_chars: list[str] = [],
    ):
        self.channel = channel
        self.message = message
        self.round = round
        self.turn = turn
        self.actors = actors
        self.temp_chars = temp_chars

    def add_actors(self, actor):
        self.actors.append(actor)
        self.actors = sorted(self.actors, key=lambda x: x.initiative, reverse=True)

    def remove_actors(self, actor: str):
        self.actors.remove(next((x for x in self.actors if x.name == actor), None))

    def check_actor(self, actor: str) -> bool:
        return any((x for x in self.actors if x.name == actor))

    def get_current(self) -> Actor:
        return self.actors[self.turn]

    def get_actor(self, name) -> Actor:
        return next((x for x in self.actors if x.name == name), None)

    def next_turn(self):
        if self.round == 0:
            self.round = 1
            self.turn = 0
        else:
            self.turn += 1
            if self.turn >= len(self.actors):
                self.round += 1
                self.turn = 0

    def __str__(self) -> str:
        return self.toJSON()

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4,
            ensure_ascii=False,
        )
