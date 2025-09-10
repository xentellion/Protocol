import asyncio
import random

# import discord
from discord.ext import commands

from src.client import Protocol
from src.enums import Enums


class Shooter(commands.Cog):
    def __init__(self, bot: Protocol):
        self.bot = bot

    @commands.command(
        name="shoot", help="ping user to try to kill them", pass_context=True
    )
    async def shoot(self, ctx, ping):
        await ctx.message.add_reaction(self.bot.get_emoji(Enums.gun))
        victim = ctx.guild.get_member(int(ping[2:-1]))
        _ = self.bot.locale(ctx.guild.preferred_locale)
        if ctx.author == victim:
            await ctx.send(_("There is no easy way out of here."))
            return
        if victim == self.bot.user:
            await ctx.send(_("Pointless. You cannot stop The Protocol."))
            return
        n = random.randint(0, 1)
        if n == 0:
            await ctx.send(_("You shot {0}").format(ping))
        else:
            await ctx.send(_("Miss! Such a shame."))

    @commands.command(name="gun", help="russian roulette", pass_context=True)
    async def gun(self, ctx):
        _ = self.bot.locale(ctx.guild.preferred_locale)
        async with ctx.typing():
            await ctx.message.add_reaction(self.bot.get_emoji(Enums.gun))
            await ctx.send(_("You took a revolover in your hand"))
        async with ctx.typing():
            await asyncio.sleep(2)
            await ctx.send(_("You checked the drum and spun it"))
        async with ctx.typing():
            await asyncio.sleep(2)
            await ctx.send(_("You pressed the gun to your temple..."))
        async with ctx.typing():
            await asyncio.sleep(4)
            n = random.randint(0, 6)
            if n == 0:
                await ctx.send(
                    _("The sound of a blast rang and {0}\'s body collapsed to the ground").format(ctx.author.mention)
                )
            else:
                await ctx.send(_("Misfire! Pass the gun to the one next to you. Let them test their luck."))


async def setup(bot):
    await bot.add_cog(Shooter(bot))

