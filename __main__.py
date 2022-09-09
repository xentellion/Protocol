import os
import asyncio
import discord.errors
from dotenv import load_dotenv
from discord.ext import commands

# Get loading data
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('BOT_PREFIX')

intents = discord.Intents.all()
intents.members = True
   
folder = './Data/'
server_folder = 'Server/'
if not os.path.exists(folder + server_folder):
    os.makedirs(folder + server_folder)

activity = discord.Activity(type=discord.ActivityType.watching, name = "как горят миры")
status = discord.Status.online
bot = commands.Bot(command_prefix=PREFIX, intents=intents, activity = activity)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord')

async def main():
    for f in os.listdir('./Cogs'):
        if f.endswith('.py'):
            await bot.load_extension(f'Cogs.{f[:-3]}')
    await bot.start(TOKEN)

asyncio.run(main())

bot.run(TOKEN, bot=True, reconnect=True)