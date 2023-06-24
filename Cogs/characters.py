import json
import discord
import character_data
from typing import List
from client import Protocol
from discord import app_commands
from discord.ext import commands


class Characters(commands.Cog):
    group = app_commands.Group(
        name="char", 
        description="Set of commands for handling caracters")
    
    def __init__(self, bot: Protocol):
        self.bot = bot
        super().__init__()

    @group.command(name="create", description= "Create character for combat!")
    async def add_char(self, interaction: discord.Interaction):
        await interaction.response.send_modal(StartForm(self.bot))