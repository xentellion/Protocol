import os
import asyncio
import discord
from client import Protocol


discord.utils.setup_logging()

intents = discord.Intents.all()
intents.members = True
activity = discord.Activity(
    type=discord.ActivityType.watching, 
    name = "как горят миры"
)

protocol = Protocol(
    intents = intents,
    activity = activity,
    data_folder= './Data/',
    config= 'config.json'
)

protocol.remove_command('help')

async def main():
    for f in os.listdir('./Cogs'):
        if f.endswith('.py'):
            await protocol.load_extension(f'Cogs.{f[:-3]}')
    await protocol.start(protocol.config.token)

asyncio.run(main())