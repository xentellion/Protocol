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
    config= 'config.yml'
)

protocol.remove_command('help')

@protocol.event
async def on_thread_update(thread):
    thread.join()

async def main():
    for f in os.listdir('./Cogs'):
        if f.endswith('.py'):
            await protocol.load_extension(f'Cogs.{f[:-3]}')
    await protocol.start(protocol.config['DISCORD_TOKEN'])

asyncio.run(main())