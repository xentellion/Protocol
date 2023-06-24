import discord
from .Models.characters import *
from data_control import *
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

    async def get_characters(self, interaction: discord.Interaction, char: str
    ) -> List[app_commands.Choice[str]]:
        path = f'{self.bot.data_folder}Campaigns/{interaction.guild.id}.json'
        server = await JsonDataControl.get_file(path)
        campaign = server.get_campain(server.current_c)
        if campaign is None:
            return None
        return [
            app_commands.Choice(name= x.name, value= x.name )
            for x in campaign.characters if (char.lower() in x.name.lower() \
                and x.author == interaction.user.id)
        ]

    @group.command(name="create", description= "Create character for combat!")
    async def add_char(self, interaction: discord.Interaction):
        path = f'{self.bot.data_folder}Campaigns/{interaction.guild.id}.json'
        campaigns = await JsonDataControl.get_file(path)
        if campaigns.find_campain(campaigns.current_c):
            await interaction.response.send_modal(StartForm(self.bot))
        else:
            await interaction.response.send_message(
                'There is no active campaign!')
            
    @group.command(name="delete", description="Remove the unused character!")
    @app_commands.autocomplete(name=get_characters)
    async def remove_char(self, interaction: discord.Interaction, name: str):
        await interaction.response.send_message(
            f"## Are you sure you want to delete character {name}?", 
            view= DeleteConfirm(self.bot, name), 
            ephemeral= True
        )

async def setup(bot: Protocol):
    await bot.add_cog(Characters(bot))