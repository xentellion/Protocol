import discord
import src.character_data as char_data
from src.client import Protocol
from src.data_control import *


def set_value(old_value: str, new_value: str):
    return int(old_value) if new_value == "" else int(new_value)


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
        campaigns = await JsonDataControl.get_file(path)
        current = campaigns.get_campain(campaigns.current_camp)

        if current.check_character(self.c_name.value):
            await interaction.response.send_message(
                "There is already a character with that name!"
            )
            return

        new_char = char_data.Character(
            name=self.c_name.value,
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
        current.add_character(new_char)
        campaigns.update_campaign(current)
        JsonDataControl.save_update(path, campaigns)
        await interaction.response.send_message(
            f"Character `{new_char.name}` has been created!", ephemeral=False
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
        campaigns = await JsonDataControl.get_file(path)
        current = campaigns.get_campain(campaigns.current_camp)
        current.remove_character(self.char)
        campaigns.update_campaign(current)
        JsonDataControl.save_update(path, campaigns)
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
        campaigns = await JsonDataControl.get_file(path)
        current = campaigns.get_campain(campaigns.current_camp)

        old_char = current.get_character(self.char)

        if old_char is None:
            await interaction.response.send_message(
                "There is no character with that name!"
            )
            return

        new_char = char_data.Character(
            name=old_char.name,
            author=interaction.user.id,
            hp=set_value(old_char.hp, self.c_hp.value),
            max_hp=set_value(old_char.max_hp, self.c_hp.value),
            energy=set_value(old_char.energy, self.c_ep.value),
            max_energy=set_value(old_char.max_energy, self.c_ep.value),
            reaction=set_value(old_char.reaction, self.c_rp.value),
            max_reaction=set_value(old_char.max_reaction, self.c_rp.value),
            style=set_value(old_char.style, self.c_sp.value),
            max_style=set_value(old_char.max_style, self.c_sp.value),
        )

        current.remove_character(self.char)
        current.add_character(new_char)
        campaigns.update_campaign(current)
        JsonDataControl.save_update(path, campaigns)
        await interaction.response.send_message(
            f"Character `{new_char.name}` has been updated!", ephemeral=False
        )
