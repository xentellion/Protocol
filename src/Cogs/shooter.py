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
        if ctx.author == victim:
            await ctx.send("Стреляться вздумали? Не в мою смену")
            return
        if victim == self.bot.user:
            await ctx.send("Не стоит стараний. Протокол невозможно остановить.")
            return
        n = random.randint(0, 1)
        if n == 0:
            await ctx.send(f"Вы застрелили {ping}")
        else:
            await ctx.send("Промах! Какая досада ")

    @commands.command(name="gun", help="russian roulette", pass_context=True)
    async def gun(self, ctx):
        async with ctx.typing():
            await ctx.message.add_reaction(self.bot.get_emoji(Enums.gun))
            await ctx.send("Вы взяли в руки револьвер")
        async with ctx.typing():
            await asyncio.sleep(2)
            await ctx.send("Вы проверили барабан и прокрутили его")
        async with ctx.typing():
            await asyncio.sleep(2)
            await ctx.send("Вы приложили револьвер к виску...")
        async with ctx.typing():
            await asyncio.sleep(4)
            n = random.randint(0, 6)
            if n == 0:
                await ctx.send(
                    f"Раздался выстрел и тело {ctx.author.mention} с грохотом упало на пол"
                )
            else:
                await ctx.send("Осечка! Передайте пистолет другому. Пусть он тоже испытает удачу.")


async def setup(bot):
    await bot.add_cog(Shooter(bot))

