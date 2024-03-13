import os
import asyncio
import discord
from src.client import Protocol


discord.utils.setup_logging()


async def main():
    protocol = Protocol(
        intents=discord.Intents.all(),
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="как горят миры"
        ),
        data_folder="./Data/",
        config="config.json",
    )

    protocol.remove_command("help")

    for f in os.listdir("./src/Cogs"):
        if f.endswith(".py"):
            await protocol.load_extension(f"src.Cogs.{f[:-3]}")
    await protocol.start(protocol.config.token)


asyncio.run(main())
