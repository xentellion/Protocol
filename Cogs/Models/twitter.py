import discord
import pandas as pd
from client import Protocol
from enums import Enums


class Form(discord.ui.Modal):  
    login = discord.ui.TextInput(
        style= discord.TextStyle.short,
        label = "Задайте имя персонажа",
        placeholder= "SampleLogin",
        required= True,
        min_length= 3,
        max_length=64
    )

    avatar = discord.ui.TextInput(
        style=discord.TextStyle.short,
        required= False,
        label = "Вставьте ссылку на аватарку вашего персонажа",
        placeholder= "Link MUST have file format: .jpeg, .png, etc.",
    )

    def __init__(self, bot:Protocol):      
        self.bot = bot
        super().__init__(title="Зарегистрировать персонажа")

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


class Message(discord.ui.Modal): 
    login = discord.ui.TextInput(
        style= discord.TextStyle.long,
        label = "Введите сообщение",
        placeholder= "Ваше сообщение",
        required= True,
        max_length=2000
    )

    def __init__(self, bot:Protocol, char):      
        self.bot = bot
        super().__init__(title="Напишите сообщение")
        self.character = char

    async def on_submit(self, interaction: discord.Interaction, ):
        df = self.bot.characters
        char = df.loc[(df['user'] == interaction.user.id) & (df['login'] == self.character)]
        webhook = None

        try:
            webhook = await interaction.channel.create_webhook(name='Protocol1')
            await webhook.send(
                content= self.login.value, 
                username= f"{df.at[char.index[0], 'login']}", 
                avatar_url= f"{df.at[char.index[0], 'avatar']}",
                wait= True)
        except:
            webhook = await interaction.channel.parent.create_webhook(name='Protocol2')
            await webhook.send(
                content= self.login.value, 
                username= f"{df.at[char.index[0], 'login']}", 
                avatar_url= f"{df.at[char.index[0], 'avatar']}",
                thread= interaction.channel,
                wait= True)
         
        await webhook.delete()
        await interaction.response.send_message("Сообщение отправлено ✅", ephemeral=True)


class TopicStarter(discord.ui.Modal):
    topic_title = discord.ui.TextInput(
        style= discord.TextStyle.short,
        label = "Введите заголовок ветки",
        placeholder= "Заголовок",
        required= True,
        max_length=500
    )

    topic_text = discord.ui.TextInput(
        style= discord.TextStyle.long,
        label = "Введите сообщение",
        placeholder= "Ваше сообщение",
        required= True,
        max_length=2000
    )

    def __init__(self, bot:Protocol, char):      
        self.bot = bot
        super().__init__(title="Начните обсуждение в форуме")
        self.character = char

    async def on_submit(self, interaction: discord.Interaction, ):
        df = self.bot.characters
        char = df.loc[(df['user'] == interaction.user.id) & (df['login'] == self.character)]
        webhook = await interaction.channel.parent.create_webhook(name='Protocol2')

        await webhook.send(
            thread_name= self.topic_title.value,
            content= self.topic_text.value, 
            username= f"{df.at[char.index[0], 'login']}", 
            avatar_url= f"{df.at[char.index[0], 'avatar']}",
            wait= True)
         
        await webhook.delete()
        await interaction.response.send_message("Сообщение отправлено ✅", ephemeral=True)


class DeleteConfirm(discord.ui.View):
    def __init__(self, bot:Protocol, character) -> None:
        super().__init__(timeout= 10)
        self.bot = bot
        self.char = character
        self.titles = ["ДА", "НЕТ"]
        self.add_buttons()

    async def page_yes(self, interaction: discord.Interaction):
        self.bot.characters = self.bot.characters.drop(self.char.index[0])
        path = self.bot.data_folder + 'characters.csv'
        self.bot.characters.to_csv(path)
        self.bot.characters = pd.read_csv(path, index_col= 0)
        await interaction.response.edit_message(
            content="Персонаж удален", view = None)

    async def page_no(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content = "Отмена удаления", view = None)

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
