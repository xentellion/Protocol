import discord
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
        self.path = "{0}Campaigns/{1}.json".format(self.bot.data_folder, "{0}")

    # SUPPORTING METHODS
    async def get_campaigns(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        camp = await self.get_camp_data(interaction)
        if camp is None:
            return
        return [
            app_commands.Choice(name=x.name, value=x.name)
            for x in camp.campaigns
            if current.lower() in x.name.lower()
        ]

    async def get_camp_data(self, interaction):
        try:
            path = self.path.format(interaction.guild.id)
            return await JsonDataControl.get_file(path)
        except json.decoder.JSONDecodeError:
            await interaction.response.send_message(
                "THERE ARE NO CAMPAIGNS ON THIS SERVER"
            )
            return

    # CAMPAIGN START
    @group.command(name="start", description="Start new Campaign for new characters!")
    @app_commands.checks.has_permissions(administrator=True)
    #  ->
    async def campaign_start(self, interaction: discord.Interaction, name: str):
        camp = await self.get_camp_data(interaction)
        if camp is None:
            return

        if camp.find_campain(name):
            await interaction.response.send_message(
                "There is already a campaign with that name!"
            )
            return
        camp += name.strip()
        camp.current_c = name
        JsonDataControl.save_update(self.path.format(interaction.guild.id), camp)
        await interaction.response.send_message(
            f"## Campaign `{name}` has been created and is set as active!"
        )

    # CAMPAIGN DELETE
    @group.command(name="delete", description="Delete finished campaign!")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.autocomplete(name=get_campaigns)
    #  ->
    async def campaign_delete(self, interaction: discord.Interaction, name: str):
        await interaction.response.send_message(
            f"## Are you sure you want to delete campaign {name}?",
            view=DeleteConfirm(self.bot, name),
            ephemeral=True,
        )

    # CAMPAIGN VIEW
    @group.command(
        name="view",
        description="Check the list of all available campaigns on this server!",
    )
    #  ->
    async def campaign_view(self, interaction: discord.Interaction):
        camp = await self.get_camp_data(interaction)
        if camp is None:
            return
        text = "\n".join(
            f"{'# ' if i.name == camp.current_c else '  '}{i.name}"
            for i in camp.campaigns
        )
        if len(text) == 0:
            await interaction.response.send_message(
                "THERE ARE NO CAMPAIGNS ON THIS SERVER"
            )
            return
        await interaction.response.send_message(
            f"```md\nCAMPAIGNS OF THIS SERVER \n========================\n{text}```"
        )

    # CAMPAIGN SET
    @group.command(name="set", description="Set campain and characters to be active!")
    @app_commands.autocomplete(name=get_campaigns)
    @app_commands.checks.has_permissions(administrator=True)
    #  ->
    async def campaign_set(self, interaction: discord.Interaction, name: str):
        camp = await self.get_camp_data(interaction)
        if camp is None:
            return
        camp.current_c = name
        JsonDataControl.save_update(self.path.format(interaction.guild.id), camp)
        await interaction.response.send_message(
            f"## Campaign `{name}` has been set as Active!"
        )


async def setup(bot: Protocol):
    await bot.add_cog(Campaign(bot))
