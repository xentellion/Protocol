import discord
import pandas as pd
from src.enums import Enums
from typing import List
from src.client import Protocol
from discord import app_commands
from discord.ext import commands
from discord.app_commands import locale_str
from .Models.twitter import DeleteConfirm, TopicStarter, Form, Message


_ = lambda x: x


class Twitter(commands.Cog):
    group = app_commands.Group(
        name="twit", description="Set of commands for handling caracters"
    )

    def __init__(self, bot: Protocol):
        self.bot = bot
        super().__init__()

    async def get_character(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        choices = self.bot.characters.loc[
            self.bot.characters["user"] == interaction.user.id
        ]["login"]
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices
            if current.lower() in choice.lower()
        ]

    async def get_forums(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[discord.ForumChannel]]:
        choices = interaction.guild.forums
        return [
            app_commands.Choice(name=choice.name, value=str(choice.id))
            for choice in choices
            if current.lower() in choice.name.lower()
        ]

    async def get_forum_tags(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[discord.ForumTag]]:
        choices = interaction.channel.parent.available_tags
        return [
            app_commands.Choice(name=choice.name, value=str(choice.id))
            for choice in choices
            if current.lower() in choice.name.lower()
        ]

    @group.command(name="register", description=locale_str(_("Log in to write as your character!")))
    async def twitter_login(self, interaction: discord.Interaction):
        await interaction.response.send_modal(Form(self.bot, interaction.locale))

    @group.command(name="send", description=locale_str(_("Write as your character!")))
    @app_commands.describe(
        character=locale_str(_("Character name")),
        image_url=locale_str(_("Append image form this link to the message!"))
    )
    @app_commands.autocomplete(character=get_character)
    async def twitter_post(
        self, interaction: discord.Interaction, character: str, image_url: str = None
    ):
        await interaction.response.send_modal(Message(self.bot, interaction.locale, character, image_url))

    @group.command(
        name="start_topic", description="Start your character topic in forum!"
    )
    @app_commands.autocomplete(character=get_character, tag=get_forum_tags)
    @app_commands.describe(
        character=locale_str(_("Character name")),
        tag=locale_str(_("Append forum tag to your post"))
    )
    async def twitter_ts(
        self,
        interaction: discord.Interaction,
        character: str,
        tag: str = None,
        image_url: str = None,
    ):
        await interaction.response.send_modal(
            TopicStarter(self.bot, interaction.locale, character, tag, image_url)
        )

    @group.command(name="delete_account", description=locale_str(_("Delete your character")))
    @app_commands.autocomplete(character=get_character)
    @app_commands.describe(
        character=locale_str(_("Character name")),
    )
    async def twitter_delete(self, interaction: discord.Interaction, character: str):
        df = self.bot.characters
        char = df.loc[(df["user"] == interaction.user.id) & (df["login"] == character)]
        _ = self.bot.locale(interaction.locale)
        await interaction.response.send_message(
            _("Are you sure you want to delete the character?"),
            view=DeleteConfirm(self.bot, interaction.locale, char),
            ephemeral=True,
        )

    @group.command(name="change_avatar", description=locale_str(_("Change character avatar")))
    @app_commands.autocomplete(character=get_character)
    @app_commands.describe(
        character=locale_str(_("Character name")),
        avatar=locale_str(_("Append image form this link to set as character profile picture!"))
    )
    async def change_avatar(
        self, interaction: discord.Interaction, character: str, *, avatar: str
    ):
        df = self.bot.characters
        char = df.loc[(df["user"] == interaction.user.id) & (df["login"] == character)]
        df.at[char.index[0], "avatar"] = avatar
        path = self.bot.data_folder + Enums.default_char_list
        self.bot.characters = df
        self.bot.characters.to_csv(path)
        self.bot.characters = pd.read_csv(path, index_col=0)
        _ = self.bot.locale(interaction.locale)
        await interaction.response.send_message(
            f"{_('Avatar is changed')} ✅",
            ephemeral=True
        )


async def setup(bot: Protocol):
    await bot.add_cog(Twitter(bot))
