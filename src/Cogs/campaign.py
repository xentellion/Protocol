import json
import discord
from src.client import Protocol
from .Models.campaign import DeleteConfirm, CreateCampaign
from src.data_control import JsonDataControl
from src.character_data import DnDServer
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
        return [app_commands.Choice(name=x, value=x) for x in camp.campaigns.keys()]

    async def get_camp_data(self, interaction: discord.Interaction) -> DnDServer:
        try:
            path = self.path.format(interaction.guild.id)
            return await JsonDataControl.get_file(path)
        except json.decoder.JSONDecodeError:
            return await JsonDataControl.get_file(path)

    # CAMPAIGN START
    @group.command(name="start", description="Start new Campaign for new characters!")
    @app_commands.checks.has_permissions(administrator=True)
    async def campaign_start(self, interaction: discord.Interaction):
        camp = await self.get_camp_data(interaction)
        if camp is None:
            return
        await interaction.response.send_modal(
            CreateCampaign(self.bot, interaction.locale, camp)
        )

    # CAMPAIGN DELETE
    @group.command(name="delete", description="Delete finished campaign!")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.autocomplete(name=get_campaigns)
    async def campaign_delete(self, interaction: discord.Interaction, name: str):
        _ = self.bot.locale(interaction.locale)
        await interaction.response.send_message(
            _("## Are you sure you want to delete campaign {0}?").format(name),
            view=DeleteConfirm(self.bot, interaction.locale, name),
            ephemeral=True,
        )

    # CAMPAIGN VIEW
    @group.command(
        name="view",
        description="Check the list of all available campaigns on this server!",
    )
    async def campaign_view(self, interaction: discord.Interaction):
        camp = await self.get_camp_data(interaction)
        if camp is None:
            return
        text = "\n".join(
            f"{'# ' if i == camp.current_c else '  '}{i}" for i in camp.campaigns.keys()
        )
        _ = self.bot.locale(interaction.locale)
        if len(text) == 0:
            await interaction.response.send_message(
                _("THERE ARE NO CAMPAIGNS ON THIS SERVER")
            )
            return
        await interaction.response.send_message(
            _("```md\nCAMPAIGNS OF THIS SERVER \n========================\n{0}```").format(text)
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
        _ = self.bot.locale(interaction.locale)
        await interaction.response.send_message(
            _("## Campaign `{0}` has been set as Active!").format(name)
        )


async def setup(bot: Protocol):
    await bot.add_cog(Campaign(bot))
