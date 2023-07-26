import discord
import pandas as pd
from enums import Enums
from typing import List
from client import Protocol
from discord import app_commands
from discord.ext import commands
from .Models.twitter import *


class Twitter(commands.Cog):
    group = app_commands.Group(
        name="twit", 
        description="Set of commands for handling caracters")

    def __init__(self, bot: Protocol):
        self.bot = bot
        super().__init__()

    async def get_character(self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        choices = self.bot.characters.loc[self.bot.characters['user'] == interaction.user.id]['login']
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices if current.lower() in choice.lower()
        ]

    async def get_forums(self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[discord.ForumChannel]]:
        choices = interaction.guild.forums
        return [
            app_commands.Choice(name=choice.name, value=str(choice.id))
            for choice in choices if current.lower() in choice.name.lower()
        ]
    
    @group.command(name="register", description= "Log in to write as your character")
    async def twitter_login(self, interaction: discord.Interaction):
        await interaction.response.send_modal(Form(self.bot))

    @group.command(name="send", description= "Write as your character!")
    @app_commands.autocomplete(character=get_character)
    async def twitter_post(self, interaction: discord.Interaction, character:str):
        await interaction.response.send_modal(Message(self.bot, character))

    @group.command(name="start_topic", description= "Start your character topic in forum!")
    @app_commands.autocomplete(character=get_character)
    async def twitter_ts(self, interaction: discord.Interaction, character:str):
        await interaction.response.send_modal(TopicStarter(self.bot, character))
        

    @group.command(name="delete_account", description= "Delete your character")
    @app_commands.autocomplete(character=get_character)
    async def twitter_delete(self, interaction: discord.Interaction, character:str):
        df = self.bot.characters
        char = df.loc[(df['user'] == interaction.user.id) & (df['login'] == character)]
        await interaction.response.send_message(
            "Вы уверены, что хотите удалить персонажа?", 
            view= DeleteConfirm(self.bot, char), 
            ephemeral= True
        )

    @group.command(name="change_avatar", description= "Change character avatar")
    @app_commands.autocomplete(character=get_character)
    async def change_avatar(self, interaction: discord.Interaction, character:str, *, avatar:str):
        df = self.bot.characters
        char = df.loc[(df['user'] == interaction.user.id) & (df['login'] == character)]
        df.at[char.index[0], 'avatar'] = avatar
        path = self.bot.data_folder + Enums.default_char_list
        self.bot.characters = df
        self.bot.characters.to_csv(path)
        self.bot.characters = pd.read_csv(path, index_col= 0)
        await interaction.response.send_message("Аватар изменен ✅", ephemeral=True)

async def setup(bot: Protocol):
    await bot.add_cog(Twitter(bot))