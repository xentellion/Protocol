import discord
from src.client import Protocol


class HelpView(discord.ui.View):
    def __init__(self, bot: Protocol) -> None:
        super().__init__()
        self.bot = bot
        self.titles = ["⬅️", "↩️", "➡️"]
        self.page = 0
        self.add_buttons()

    async def page_next(self, interaction: discord.Interaction):
        if self.page < len(self.bot.help_locale(interaction.locale)) - 1:
            self.page += 1
            await interaction.response.edit_message(
                embed=self.set_embed(self.bot.help_locale(interaction.locale)[self.page])
            )
        else:
            await interaction.response.defer()

    async def page_home(self, interaction: discord.Interaction):
        self.page = 0
        await interaction.response.edit_message(
            embed=self.set_embed(self.bot.help_locale(interaction.locale)[self.page])
        )

    async def page_back(self, interaction: discord.Interaction):
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(
                embed=self.set_embed(self.bot.help_locale(interaction.locale)[self.page])
            )
        else:
            await interaction.response.defer()

    def add_buttons(self):
        colors = [
            discord.ButtonStyle.blurple,
            discord.ButtonStyle.blurple,
            discord.ButtonStyle.blurple,
        ]
        methods = [self.page_back, self.page_home, self.page_next]
        for i in range(len(methods)):
            button = discord.ui.Button(label=self.titles[i], style=colors[i])
            button.callback = methods[i]
            self.add_item(button)

    def set_embed(self, data: dict):
        title = next(iter(data))
        text = [f"**{item}** - {data[title][item]}" for item in data[title]]
        return discord.Embed(
            title=title,
            description="\n".join(text),
            color=discord.Colour.gold(),
        )
