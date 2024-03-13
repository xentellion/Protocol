import asyncio
import discord
import pandas as pd
from src.enums import Enums
from discord import app_commands
from discord.ext import commands
from .Models.help import HelpView


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        path = self.bot.data_folder + Enums.default_char_list
        f = open(path, "a+", encoding="utf-8")
        f.close()
        try:
            df = pd.read_csv(path, index_col=0)
        except pd.errors.EmptyDataError:
            columns = ["user", "login", "avatar"]
            df = pd.DataFrame(columns=columns)
        self.bot.characters = df
        df.to_csv(path)
        print(f"> Total characters: {len(df.index)}")
        print(f"{self.bot.user.name} has connected to Discord")

    @app_commands.command(name="help", description="Get Protocol info!")
    async def help(self, interaction: discord.Interaction):
        view = HelpView(self.bot)
        await interaction.response.send_message(
            embed=view.set_embed(self.bot.help[0]), view=view, ephemeral=True
        )

    @commands.command(name="message")
    async def message(self, ctx, *, arg):
        await ctx.message.delete()
        webhook = await ctx.channel.create_webhook(name="The Protocol")
        await webhook.send(
            content=arg,
            username="Protocol",
            avatar_url=self.bot.user.display_avatar.url,
        )
        await webhook.delete()

    @commands.command(name="techo", help="Temporary message for up to 600 sceonds")
    async def techo(self, ctx, _time, *, arg):
        try:
            _time = int(_time)
        except ValueError:
            await ctx.send("Command must be in format `!techo <0-600> text`")
            return
        if _time > 600 or _time < 0:
            await ctx.send("Time can be set anly between 0 and 600 seconds")
            return
        await ctx.message.delete()
        webhook = await ctx.channel.create_webhook(name="The Protocol")
        message = await webhook.send(
            content=arg,
            username=ctx.message.author.display_name,
            avatar_url=ctx.message.author.display_avatar.url,
            wait=True,
        )
        await asyncio.sleep(_time)
        await message.delete()
        await webhook.delete()

    @commands.command()
    async def protocol(self, ctx):
        embed = discord.Embed(
            title="**ПРОТОКОЛ ИНИЦИИРОВАН**", color=discord.Color.gold()
        )
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/1133840435014545488/1133849046281363486/protocol.png"
        )
        await ctx.send(embed=embed)

    @commands.command(name="sync")
    @commands.has_permissions(administrator=True)
    async def sync(self, ctx) -> None:
        synced = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands globally")
        return

    # @commands.command(name="servers")
    # async def servers(self, ctx) -> None:
    #     t = ""
    #     for guild in self.bot.guilds:
    #         t += f"{guild.name}\n"
    #     await ctx.send(t)


async def setup(bot):
    await bot.add_cog(Misc(bot))
