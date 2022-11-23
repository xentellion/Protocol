import os
import yaml
import discord
from discord.ext import commands


class EmptyConfig(Exception):
    def __init__(self, config_path: str):
        self.message = f'Please, set up variables in {config_path}'
        super().__init__(self.message)


class Protocol(commands.Bot):
    def __init__(self, intents, activity, data_folder, config):
        self.data_folder = data_folder
        os.makedirs(self.data_folder, exist_ok= True)
        self.config_path = self.data_folder + config
        with open(self.config_path, 'a+', encoding="utf8") as file:
            file.seek(0)
            self.config = yaml.safe_load(file)
            if type(self.config) is not dict:
                yaml.dump({"BOT_PREFIX": "", "DISCORD_TOKEN": ""}, file)
                raise EmptyConfig(self.config_path)
            elif self.config['BOT_PREFIX'] == "":
                raise EmptyConfig(self.config_path)
        super().__init__(
            command_prefix= self.config['BOT_PREFIX'], 
            intents= intents, 
            activity= activity
            )
        self.characters = None

    async def setup_hook(self):
        await self.tree.sync(guild = discord.Object(id=557589422372028416))

    async def on_command_error(self, ctx, error):
        print(error)