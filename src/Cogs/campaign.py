import discord
from typing import List
from src.client import Protocol
from .Models.campaign import DeleteConfirm
from src.data_control import *
from discord import app_commands
from discord.ext import commands


class Campaign(commands.Cog):
    group = app_commands.Group(
        name="campaign", description="Set of comands for handling campaigns"
    )

    def __init__(self, bot: Protocol):
        self.bot = bot
        super().__init__()

    async def get_campaigns(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        path = f"{self.bot.data_folder}Campaigns/{interaction.guild.id}.json"
        camp = await JsonDataControl.get_file(path)
        return [
            app_commands.Choice(name=x.name, value=x.name)
            for x in camp.campaigns
            if current.lower() in x.name.lower()
        ]

    @group.command(name="start", description="Start new Campaign for new characters!")
    @app_commands.checks.has_permissions(administrator=True)
    async def capaign_start(self, interaction: discord.Interaction, name: str):
        path = f"{self.bot.data_folder}Campaigns/{interaction.guild.id}.json"
        camp = await JsonDataControl.get_file(path)
        if camp.find_campain(name):
            await interaction.response.send_message(
                "There is already a campaign with that name!"
            )
            return
        camp.add_campain(name.strip())
        JsonDataControl.save_update(path, camp)
        await interaction.response.send_message(f"Campaign `{name}` has been created!")

    @group.command(name="delete", description="Delete finished campaign!")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.autocomplete(name=get_campaigns)
    async def campaign_delete(self, interaction: discord.Interaction, name: str):
        await interaction.response.send_message(
            f"## Are you sure you want to delete campaign {name}?",
            view=DeleteConfirm(self.bot, name),
            ephemeral=True,
        )

    @group.command(
        name="view",
        description="Check the list of all available campaigns on this server!",
    )
    async def campaign_view(self, interaction: discord.Interaction):
        path = f"{self.bot.data_folder}Campaigns/{interaction.guild.id}.json"
        camp = await JsonDataControl.get_file(path)
        text = ""
        for i in camp.campaigns:
            text += ("# " if i.name == camp.current_c else " ") + i.name + "\n"
        await interaction.response.send_message(
            f"```md\nCAMPAIGNS OF THIS SERVER \n========================\n{text}```"
        )

    @group.command(name="set", description="Set campain and characters to be active!")
    @app_commands.autocomplete(name=get_campaigns)
    @app_commands.checks.has_permissions(administrator=True)
    async def campaign_set(self, interaction: discord.Interaction, name: str):
        path = f"{self.bot.data_folder}Campaigns/{interaction.guild.id}.json"
        camp = await JsonDataControl.get_file(path)
        camp.current_c = name
        JsonDataControl.save_update(path, camp)
        await interaction.response.send_message(
            f"## Campaign `{name}` has been set as Active!"
        )


async def setup(bot: Protocol):
    await bot.add_cog(Campaign(bot))
