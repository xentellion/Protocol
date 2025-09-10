import discord
from src.character_data import Character, Characteristic
from src.client import Protocol
from src.data_control import JsonDataControl


class StartForm(discord.ui.Modal):
    def __init__(self, bot: Protocol, locale: str, stats: dict[str, Characteristic]):
        self.bot = bot
        self.stats = stats
        _ = self.bot.locale(locale)
        self.c_name = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label=_("Set Character Name"),
            placeholder=_("Name"),
            required=True,
        )
        super().__init__(title=_("Register a character"))
        self.add_item(self.c_name)

    async def on_submit(self, interaction: discord.Interaction):
        path = f"{self.bot.data_folder}Campaigns/{interaction.guild.id}.json"
        server = await JsonDataControl.get_file(path)
        _ = self.bot.locale(interaction.locale)

        if self.c_name.value in server.campaigns[server.current_c]:
            await interaction.response.send_message(
                _("There is already a character with that name!")
            )
            return

        new_char = Character(
            author=interaction.user.id,
        )
        new_char.stats = self.stats.copy()

        server.campaigns[server.current_c].characters[self.c_name.value] = new_char

        JsonDataControl.save_update(path, server)
        await interaction.response.send_message(
            _("Character `{0}` is created! Don't forget to set up their charateristics").format(self.c_name.value),
            ephemeral=False,
        )


class DeleteConfirm(discord.ui.View):
    def __init__(self, bot: Protocol, locale: str, char: str) -> None:
        super().__init__(timeout=15)
        self.bot = bot
        self.char = char
        _ = self.bot.locale(locale)
        self.titles = [_("YES"), _("NO")]
        self.add_buttons()

    async def page_yes(self, interaction: discord.Interaction):
        path = f"{self.bot.data_folder}Campaigns/{interaction.guild.id}.json"
        server = await JsonDataControl.get_file(path)
        del server.campaigns[server.current_c][self.char]
        _ = self.bot.locale(interaction.locale)
        JsonDataControl.save_update(path, server)
        await interaction.response.edit_message(
            content=_("## Character Deleted"), view=None
        )

    async def page_no(self, interaction: discord.Interaction):
        _ = self.bot.locale(interaction.locale)
        await interaction.response.edit_message(content=_("Cancelled"), view=None)

    def add_buttons(self):
        colors = [discord.ButtonStyle.red, discord.ButtonStyle.green]
        methods = [self.page_yes, self.page_no]
        for i in range(len(methods)):
            button = discord.ui.Button(label=self.titles[i], style=colors[i])
            button.callback = methods[i]
            self.add_item(button)


class EditForm(discord.ui.Modal):
    def __init__(self, bot: Protocol, locale: str, name: str, char: Character, stat: str):
        self.bot = bot
        self.name = name
        self.char = char
        self.stat = stat
        _ = self.bot.locale(locale)
        super().__init__(title=f"{_('Changing')}: {stat.capitalize()}")
        self.c_stat = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label=_("New value"),
            placeholder="0",
            required=True,
        )
        self.add_item(self.c_stat)

    async def on_submit(self, interaction: discord.Interaction):
        path = f"{self.bot.data_folder}Campaigns/{interaction.guild.id}.json"
        server = await JsonDataControl.get_file(path)
        _ = self.bot.locale(interaction.locale)
        try:
            self.char.stats[self.stat].value = int(self.c_stat.value)
            self.char.stats[self.stat].max_value = int(self.c_stat.value)
        except ValueError:
            await interaction.response.send_message(
                _("Only numbers in stat values!")
            )
        server.campaigns[server.current_c].characters[self.name] = self.char
        JsonDataControl.save_update(path, server)
        await interaction.response.send_message(
            _("Character `{0}` has been updated!").format(self.name), ephemeral=False
        )


def set_value(old_value: int, new_value: str):
    return old_value if new_value == "" else int(new_value)


def max(value: int, old_max: int, new_max: int):
    if new_max > old_max:
        return value + new_max - old_max
    else:
        return value if value <= new_max else new_max
