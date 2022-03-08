from discord.ext import commands
import asyncio

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='message')
    async def message(self, ctx, *, arg):
        await ctx.message.delete()
        webhook = await ctx.channel.create_webhook(name='The Protocol')
        await webhook.send(content=arg, username='Protocol', avatar_url=self.bot.user.avatar_url)
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

def setup(bot):
    bot.add_cog(Misc(bot))
