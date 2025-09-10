import io
import discord
import pandas as pd
from src.client import Protocol
from src.enums import Enums


class Form(discord.ui.Modal):
    def __init__(self, bot: Protocol, locale: str):
        self.bot = bot
        _ = self.bot.locale(locale)
        super().__init__(title=_("Register your character!"))
        self.login = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label=_("Set character name"),
            placeholder=_("Name"),
            required=True,
            min_length=3,
            max_length=64,
        )
        self.avatar = discord.ui.TextInput(
            style=discord.TextStyle.short,
            required=False,
            label=_("Insert link on character avatar"),
            placeholder=_("Link MUST end with file format: .jpeg, .png"),
        )
        self.add_item(self.login)
        self.add_item(self.avatar)

    async def on_submit(self, interaction: discord.Interaction):
        _ = self.bot.locale(interaction.locale)
        embed = discord.Embed(title=f"**{self.login}** {_('joined the network!')}")
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        avatar = self.avatar if self.avatar.value != "" else Enums.default_image
        embed.set_thumbnail(url=avatar)

        self.bot.characters.loc[len(self.bot.characters.index)] = [
            interaction.user.id,
            self.login,
            avatar,
        ]
        path = self.bot.data_folder + Enums.default_char_list
        self.bot.characters.to_csv(path)
        self.bot.characters = pd.read_csv(path, index_col=0)
        await interaction.response.send_message(embed=embed)


class Message(discord.ui.Modal):
    def __init__(self, bot: Protocol, locale: str, char, image_url: str = None):
        self.bot = bot
        _ = self.bot.locale(locale)
        super().__init__(title=_("Write the message"))
        self.character = char
        self.url = image_url
        self.login = discord.ui.TextInput(
            style=discord.TextStyle.long,
            label=_("Enter your message"),
            placeholder=_("Message"),
            required=True,
            max_length=2000,
        )
        self.add_item(self.login)

    async def on_submit(
        self,
        interaction: discord.Interaction,
    ):
        df = self.bot.characters
        char = df.loc[
            (df["user"] == interaction.user.id) & (df["login"] == self.character)
        ]
        webhook = None
        file = None
        if self.url is not None:
            asset = discord.Asset(self.bot._connection, url=self.url, key="")
            with io.BytesIO(await asset.read()) as a:
                file = discord.File(a, filename="0.png")
        try:
            webhook = await interaction.channel.create_webhook(name="Protocol1")
            if file is None:
                await webhook.send(
                    content=self.login.value,
                    username=f"{df.at[char.index[0], 'login']}",
                    avatar_url=f"{df.at[char.index[0], 'avatar']}",
                    wait=True,
                )
            else:
                await webhook.send(
                    content=self.login.value,
                    username=f"{df.at[char.index[0], 'login']}",
                    avatar_url=f"{df.at[char.index[0], 'avatar']}",
                    file=file,
                    wait=True,
                )
        except:
            webhook = await interaction.channel.parent.create_webhook(name="Protocol2")
            if file is None:
                await webhook.send(
                    content=self.login.value,
                    username=f"{df.at[char.index[0], 'login']}",
                    avatar_url=f"{df.at[char.index[0], 'avatar']}",
                    thread=interaction.channel,
                    wait=True,
                )
            else:
                await webhook.send(
                    content=self.login.value,
                    username=f"{df.at[char.index[0], 'login']}",
                    avatar_url=f"{df.at[char.index[0], 'avatar']}",
                    file=file,
                    thread=interaction.channel,
                    wait=True,
                )

        await webhook.delete()
        _ = self.bot.locale(interaction.locale)
        await interaction.response.send_message(
            f"{_('Message sent!')} ✅", ephemeral=True
        )


class TopicStarter(discord.ui.Modal):
    def __init__(self, bot: Protocol, char, tag, image_url: str):
        self.bot = bot
        super().__init__(title="Start topic discussion!")
        self.character = char
        self.tag = tag
        self.url = image_url
        self.topic_title = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label="Write topic title",
            placeholder="Title",
            required=True,
            max_length=500,
        )
        self.topic_text = discord.ui.TextInput(
            style=discord.TextStyle.long,
            label="Enter your message",
            placeholder="Message body",
            required=True,
            max_length=2000,
        )
        self.add_item(self.topic_title)
        self.add_item(self.topic_text)

    async def on_submit(self, interaction: discord.Interaction):
        df = self.bot.characters
        char = df.loc[
            (df["user"] == interaction.user.id) & (df["login"] == self.character)
        ]
        webhook = await interaction.channel.parent.create_webhook(name="Protocol2")

        file = None
        if self.url is not None:
            asset = discord.Asset(self.bot._connection, url=self.url, key="")
            with io.BytesIO(await asset.read()) as a:
                file = discord.File(a, filename="0.png")
        message = None
        if file is None:
            message = await webhook.send(
                thread_name=self.topic_title.value,
                content=self.topic_text.value,
                username=f"{df.at[char.index[0], 'login']}",
                avatar_url=f"{df.at[char.index[0], 'avatar']}",
                wait=True,
            )
        else:
            message = await webhook.send(
                thread_name=self.topic_title.value,
                content=self.topic_text.value,
                username=f"{df.at[char.index[0], 'login']}",
                avatar_url=f"{df.at[char.index[0], 'avatar']}",
                file=file,
                wait=True,
            )

        if self.tag is not None:
            topic = await self.bot.fetch_channel(message.channel.id)
            tags = topic.parent.available_tags
            tag = next(x for x in tags if x.id == int(self.tag))
            await topic.add_tags(tag)

        await webhook.delete()
        _ = self.bot.locale(interaction.locale)
        await interaction.response.send_message(
            f"{_('Message sent!')} ✅", ephemeral=True
        )


class DeleteConfirm(discord.ui.View):
    def __init__(self, bot: Protocol, locale: str, character) -> None:
        super().__init__(timeout=10)
        self.bot = bot
        self.char = character
        _ = self.bot.locale(locale)
        self.titles = [_("YES"), _("NO")]
        self.add_buttons()

    async def page_yes(self, interaction: discord.Interaction):
        self.bot.characters = self.bot.characters.drop(self.char.index[0])
        self.bot.characters = self.bot.characters.reset_index(drop=True)
        path = self.bot.data_folder + "characters.csv"
        self.bot.characters.to_csv(path)
        self.bot.characters = pd.read_csv(path, index_col=0)
        _ = self.bot.locale(interaction.locale)
        await interaction.response.edit_message(content=_("Character deleted"), view=None)

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
