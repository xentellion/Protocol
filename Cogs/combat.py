import discord
from typing import List
from client import Protocol
from discord import app_commands
from discord.ext import commands

class Combat(commands.Cog):
    group = app_commands.Group(
        name="init", 
        description="Set of commands for handling combat")
    
    def __init__(self, bot: Protocol):
        self.bot = bot
        super().__init__()


async def setup(bot: Protocol):
    await bot.add_cog(Combat(bot))