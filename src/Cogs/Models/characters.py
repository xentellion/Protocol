import discord
from src.character_data import Character, Characteristic
from src.client import Protocol
from src.data_control import JsonDataControl


class StartForm(discord.ui.Modal):
    c_name = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Set Character Name",
        placeholder="Name",
        required=True,
    )

    def __init__(self, bot: Protocol, stats: dict[str, Characteristic]):
        self.bot = bot
        self.stats = stats
        super().__init__(title="Register a character")

    async def on_submit(self, interaction: discord.Interaction):
        path = f"{self.bot.data_folder}Campaigns/{interaction.guild.id}.json"
        server = await JsonDataControl.get_file(path)

        if self.c_name.value in server.campaigns[server.current_c]:
            await interaction.response.send_message(
                "There is already a character with that name!"
            )
            return

        new_char = Character(
            author=interaction.user.id,
        )
        new_char.stats = self.stats.copy()

        server.campaigns[server.current_c].characters[self.c_name.value] = new_char

        JsonDataControl.save_update(path, server)
        await interaction.response.send_message(
            f"Персонаж `{self.c_name.value}` создан! Не забудьте задать характеристики.", ephemeral=False
        )


class DeleteConfirm(discord.ui.View):
    def __init__(self, bot: Protocol, char: str) -> None:
        super().__init__(timeout=15)
        self.bot = bot
        self.char = char
        self.titles = ["YES", "NO"]
        self.add_buttons()

    async def page_yes(self, interaction: discord.Interaction):
        path = f"{self.bot.data_folder}Campaigns/{interaction.guild.id}.json"
        server = await JsonDataControl.get_file(path)
        del server.campaigns[server.current_c][self.char]

        JsonDataControl.save_update(path, server)
        await interaction.response.edit_message(
            content="## Character Deleted", view=None
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


class EditForm(discord.ui.Modal):
    c_stat = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Новое значение",
        placeholder="0",
        required=True,
    )

    def __init__(self, bot: Protocol, name: str, char: Character, stat: str):
        self.bot = bot
        self.name = name
        self.char = char
        self.stat = stat
        super().__init__(title=f"Изменение: {stat.capitalize()}")

    async def on_submit(self, interaction: discord.Interaction):
        path = f"{self.bot.data_folder}Campaigns/{interaction.guild.id}.json"
        server = await JsonDataControl.get_file(path)

        try:
            self.char.stats[self.stat].value = int(self.c_stat.value)
            self.char.stats[self.stat].max_value = int(self.c_stat.value)
        except ValueError:
            await interaction.response.send_message(
                "Only numbers in stat values!"
            )
        server.campaigns[server.current_c].characters[self.name] = self.char
        JsonDataControl.save_update(path, server)
        await interaction.response.send_message(
            f"Character `{self.name}` has been updated!", ephemeral=False
        )


def set_value(old_value: int, new_value: str):
    return old_value if new_value == "" else int(new_value)


def max(value: int, old_max: int, new_max: int):
    if new_max > old_max:
        return value + new_max - old_max
    else:
        return value if value <= new_max else new_max
