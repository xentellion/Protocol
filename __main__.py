import os
import yaml
import asyncio
import discord.errors
from discord.ext import commands

class EmptyConfig(Exception):
    def __init__(self, config_path: str):
        self.message = f'Please, set up variables in {config_path}'
        super().__init__(self.message)

intents = discord.Intents.all()
intents.members = True
   
folder = './Data/'
server_folder = 'Server/'
config_path = folder + 'config.yml'
os.makedirs(folder, exist_ok= True)
os.makedirs(folder + server_folder, exist_ok= True)
with open(config_path, 'a+', encoding="utf8") as file:
    file.seek(0)
    config = yaml.safe_load(file)
    if type(config) is not dict:
        yaml.dump({"BOT_PREFIX": "", "DISCORD_TOKEN": ""}, file)
        raise EmptyConfig(config_path)
    elif config['BOT_PREFIX'] == "":
        raise EmptyConfig(config_path)

if not os.path.exists(folder + server_folder):
    os.makedirs(folder + server_folder)

activity = discord.Activity(type=discord.ActivityType.watching, name = "как горят миры")
status = discord.Status.online
bot = commands.Bot(command_prefix=config['BOT_PREFIX'], intents=intents, activity = activity)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord')

async def main():
    for f in os.listdir('./Cogs'):
        if f.endswith('.py'):
            await bot.load_extension(f'Cogs.{f[:-3]}')
    await bot.start(config['DISCORD_TOKEN'])

asyncio.run(main())