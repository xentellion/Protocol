import discord
from src.data_control import *
from src.client import Protocol


class DeleteConfirm(discord.ui.View):
    def __init__(self, bot: Protocol, campaign: str) -> None:
        super().__init__(timeout=15)
        self.bot = bot
        self.campaign = campaign
        self.titles = ["YES", "NO"]
        self.add_buttons()

    async def page_yes(self, interaction: discord.Interaction):
        path = f"{self.bot.data_folder}Campaigns/{interaction.guild.id}.json"
        camp = await JsonDataControl.get_file(path)
        camp -= self.campaign
        JsonDataControl.save_update(path, camp)
        await interaction.response.edit_message(
            content="## Campaign Deleted", view=None
        )

    async def page_no(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Deletion cancelled", view=None)

    def add_buttons(self):
        colors = [discord.ButtonStyle.red, discord.ButtonStyle.green]
        methods = [self.page_yes, self.page_no]
        for i in range(len(methods)):
            button = discord.ui.Button(label=self.titles[i], style=colors[i])
            button.callback = methods[i]
            self.add_item(button)
