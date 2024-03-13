import os
import yaml
import json
import discord
from json import JSONDecodeError
from discord.ext import commands


class ConfigFile:
    def __init__(self, prefix: str = "", token: str = ""):
        self.prefix = prefix
        self.token = token


class EmptyConfig(Exception):
    def __init__(self, config_path: str):
        self.message = f"Please, set up variables in {config_path}"
        super().__init__(self.message)


class Protocol(commands.Bot):
    def __init__(self, intents, activity, data_folder, config):
        self.data_folder = data_folder
        os.makedirs(self.data_folder, exist_ok=True)
        self.config_path = self.data_folder + config

        with open(self.config_path, "a+", encoding="utf8") as file:
            file.seek(0)
            try:
                data = json.load(file)
                self.config = ConfigFile(**data)
                if self.config.token == "":
                    raise EmptyConfig(self.config_path)
            except JSONDecodeError:
                json.dump(ConfigFile().__dict__, file, sort_keys=False, indent=4)
                raise EmptyConfig(self.config_path)

        with open(f"{data_folder}help.yml", "r", encoding="utf8") as file:
            self.help = list(yaml.safe_load(file))
        super().__init__(
            command_prefix=self.config.prefix, intents=intents, activity=activity
        )
        self.characters = None

    async def setup_hook(self):
        await self.tree.sync(guild=discord.Object(id=557589422372028416))

    async def on_command_error(self, ctx, error):
        print(error)
