from discord.ext import commands
from enums import Enums
import pandas as pd
import asyncio
import discord

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        path = self.bot.data_folder + Enums.default_char_list
        f = open(path, 'a+', encoding='utf-8')
        f.close()
        try:
            df = pd.read_csv(path, index_col= 0)
        except pd.errors.EmptyDataError:
            columns = ['user', 'login', 'avatar']
            df = pd.DataFrame(columns= columns)
        self.bot.characters = df
        df.to_csv(path)
        print(f'> Total characters: {len(df.index)}')
        print(f'{self.bot.user.name} has connected to Discord')

    @commands.command(name='message')
    async def message(self, ctx, *, arg):
        await ctx.message.delete()
        webhook = await ctx.channel.create_webhook(name='The Protocol')
        await webhook.send(
            content=arg, 
            username='Protocol', 
            avatar_url=self.bot.user.display_avatar.url
            )
        await webhook.delete()

    @commands.command(name='techo', help='Temporary message for up to 600 sceonds')
    async def techo(self, ctx, _time, *, arg):
        try:
            _time = int(_time)
        except ValueError:
            await ctx.send("Command must be in format `!techo <0-600> text`")
            return
        if(_time > 600 or _time < 0):
            await ctx.send("Time can be set anly between 0 and 600 seconds")
            return
        await ctx.message.delete()
        mes = await ctx.send(arg)
        await asyncio.sleep(_time)
        await mes.delete()

    @commands.command()
    async def protocol(self, ctx):
        embed = discord.Embed(
            title='**ПРОТОКОЛ ИНИЦИИРОВАН**',
            color=discord.Color.gold()
        )
        embed.set_image(url='https://cdn.discordapp.com/attachments/891746827798454343/945271937339371530/dfe33c069124f36c.png')
        await ctx.send(embed=embed)

    @commands.command(name='sync') 
    @commands.has_permissions(administrator=True)
    async def sync(self, ctx) -> None:
        synced = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands globally")
        return

async def setup(bot):
    await bot.add_cog(Misc(bot))
