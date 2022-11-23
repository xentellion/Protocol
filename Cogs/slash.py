from code import interact
from email import message
from secrets import choice
import discord
import pandas as pd
from enums import Enums
from typing import List
from client import Protocol
from discord import app_commands
from discord.ext import commands

class DeleteConfirm(discord.ui.View):
    def __init__(self, bot:Protocol, lang: dict, char) -> None:
        super().__init__(timeout= 10)
        self.bot = bot
        self.char = char
        self.titles = ["ДА", "НЕТ"]
        self.add_buttons()

    async def page_yes(self, interaction: discord.Interaction):
        self.bot.characters = self.bot.characters.drop(self.char.index[0])
        path = self.bot.data_folder + 'characters.csv'
        self.bot.characters.to_csv(path)
        self.bot.characters = pd.read_csv(path, index_col= 0)
        await interaction.response.send_message("Персонаж удален", ephemeral=True)

    async def page_no(self, interaction: discord.Interaction):
        await interaction.response.send_message("Отмена удаления", ephemeral=True)
        await interaction.delete_original_response()
        self.clear_items()

    def add_buttons(self):     
        colors = [
            discord.ButtonStyle.red, 
            discord.ButtonStyle.green 
        ]
        methods = [
            self.page_yes, 
            self.page_no 
        ]
        for i in range(len(methods)):
            button = discord.ui.Button(label= self.titles[i], style= colors[i])
            button.callback = methods[i]
            self.add_item(button)


class Form(discord.ui.Modal):  
    login = discord.ui.TextInput(
        label= 'temp',
        style= discord.TextStyle.short,
        placeholder= "SampleLogin",
        required= True,
        min_length= 3,
        max_length=64
    )

    avatar = discord.ui.TextInput(
        label= 'temp',
        style=discord.TextStyle.short,
        required= False
    )

    def __init__(self, bot:Protocol):      
        self.bot = bot
        super().__init__(title="Зарегистрировать персонажа")
        self.login.label = "Задайте имя персонажа"
        self.avatar.label = "Вставьте ссылку на аватарку вашего персонажа"
        self.avatar.placeholder = "Вставьте ссылку сюда"

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = f'**{self.login}** присоединился к сети!')
        embed.set_author(name = interaction.user, icon_url=interaction.user.avatar.url)
        avatar = self.avatar if self.avatar.value != '' else Enums.default_image
        embed.set_thumbnail(url= avatar)
        self.bot.characters.loc[len(self.bot.characters.index)] = [interaction.user.id, self.login, avatar]
        path = self.bot.data_folder + Enums.default_char_list
        self.bot.characters.to_csv(path)
        self.bot.characters = pd.read_csv(path, index_col= 0)
        await interaction.response.send_message(embed= embed)


class Slash(commands.Cog):
    def __init__(self, bot: Protocol):
        self.bot = bot
        super().__init__()

    @app_commands.command(name="twitter", description= "Log in to write as your character")
    async def twitter_login(self, interaction: discord.Interaction):
        await interaction.response.send_modal(Form(self.bot))

    async def rps_autocomplete(self, interaction: discord.Interaction, current: str
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


    @app_commands.command(name="twit", description= "Write as your character!")
    @app_commands.autocomplete(character=rps_autocomplete)
    async def twitter_post(self, interaction: discord.Interaction, character:str, *, text:str):
        df = self.bot.characters
        char = df.loc[(df['user'] == interaction.user.id) & (df['login'] == character)]
        webhook = await interaction.channel.create_webhook(name='Protocol')
        await webhook.send(
            content= text, 
            username= f"{df.at[char.index[0], 'login']}", 
            avatar_url= f"{df.at[char.index[0], 'avatar']}",
            wait= True)
        await webhook.delete()
        await interaction.response.send_message("Сообщение отправлено ✅", ephemeral=True)

    @app_commands.command(name="delete_twitter", description= "Delete your character")
    @app_commands.autocomplete(choices=rps_autocomplete)
    async def twitter_delete(self, interaction: discord.Interaction, choices:str):
        df = self.bot.characters
        char = df.loc[(df['user'] == interaction.user.id) & (df['login'] == choices)]
        await interaction.response.send_message(
            "Вы уверены, что хотите удалить персонажа?", 
            view= DeleteConfirm(self.bot, char), 
            ephemeral= True
        )

async def setup(bot: Protocol):
    await bot.add_cog(Slash(bot))