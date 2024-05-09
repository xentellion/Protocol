import discord
from src.character_data import Character
from src.client import Protocol
from src.data_control import *


def set_value(old_value: int, new_value: str):
    return old_value if new_value == "" else int(new_value)


class StartForm(discord.ui.Modal):
    c_name = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Set Character Name",
        placeholder="Name",
        required=True,
    )

    c_hp = discord.ui.TextInput(
        style=discord.TextStyle.short,
        required=True,
        label="Set Character Health",
        placeholder="10",
    )

    c_ep = discord.ui.TextInput(
        style=discord.TextStyle.short,
        required=True,
        label="Set Character Energy",
        placeholder="10",
    )

    c_rp = discord.ui.TextInput(
        style=discord.TextStyle.short,
        required=True,
        label="Set Character Reaction Points",
        placeholder="0",
    )

    c_sp = discord.ui.TextInput(
        style=discord.TextStyle.short,
        required=True,
        label="Set Character Style Points",
        placeholder="0",
    )

    def __init__(self, bot: Protocol):
        self.bot = bot
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
            hp=int(self.c_hp.value),
            max_hp=int(self.c_hp.value),
            energy=int(self.c_ep.value),
            max_energy=int(self.c_ep.value),
            reaction=int(self.c_rp.value),
            max_reaction=int(self.c_rp.value),
            style=int(self.c_sp.value),
            max_style=int(self.c_sp.value),
        )

        server.campaigns[server.current_c][self.c_name.value] = new_char

        JsonDataControl.save_update(path, server)
        await interaction.response.send_message(
            f"Character `{self.c_name.value}` has been created!", ephemeral=False
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

    c_hp = discord.ui.TextInput(
        style=discord.TextStyle.short,
        required=False,
        label="Edit Character Max Health",
        placeholder="10",
    )

    c_ep = discord.ui.TextInput(
        style=discord.TextStyle.short,
        required=False,
        label="Edit Character Max Energy",
        placeholder="10",
    )

    c_rp = discord.ui.TextInput(
        style=discord.TextStyle.short,
        required=False,
        label="Edit Character Reaction Points",
        placeholder="0",
    )

    c_sp = discord.ui.TextInput(
        style=discord.TextStyle.short,
        required=False,
        label="Edit Character Style Points",
        placeholder="0",
    )

    def __init__(self, bot: Protocol, char: str):
        self.bot = bot
        self.char = char
        super().__init__(title="Edit a character")

    async def on_submit(self, interaction: discord.Interaction):
        path = f"{self.bot.data_folder}Campaigns/{interaction.guild.id}.json"
        server = await JsonDataControl.get_file(path)

        old_char = Character(server.campaigns[server.current_c][self.char])

        if old_char is None:
            await interaction.response.send_message(
                "There is no character with that name!"
            )
            return

        new_char = Character(
            author=interaction.user.id,
            hp=old_char.hp,
            max_hp=set_value(old_char.max_hp, self.c_hp.value),
            energy=old_char.energy,
            max_energy=set_value(old_char.max_energy, self.c_ep.value),
            reaction=old_char.reaction,
            max_reaction=set_value(old_char.max_reaction, self.c_rp.value),
            style=old_char.style,
            max_style=set_value(old_char.max_style, self.c_sp.value),
        )

        server.campaigns[server.current_c][self.char] = new_char

        JsonDataControl.save_update(path, server)
        await interaction.response.send_message(
            f"Character `{self.char}` has been updated!", ephemeral=False
        )
