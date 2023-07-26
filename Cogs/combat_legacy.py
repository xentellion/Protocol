from discord.ext import commands
import json
import combat_data
import random
import os
from data_control import *

class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['init', 'i'])
    async def init_combat(self, ctx):
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            await ctx.send("""**Справка: `init` или `i`** 
                `/init begin` - Начать бой
                `/init end` - Закончить бой
                `/init add <mod> <name>` - Добавить участника
                `/init remove <name>` - Убрать участника
                `/init next` - Передать очередь""")

    @init_combat.command()
    async def begin(self, ctx):
        path = f'{self.bot.data_folder}{ctx.message.channel.id}.json'
        try:
            f = open(path)
            await ctx.send('There is already a combat in this channel!')
            f.close()
            return
        except FileNotFoundError:
            print('New Combat Session')

        text = "```md\nCurrent initiative: 0 (round 0)\n"
        text += '=' * (len(text) - 7) + '\n```'
        message = await ctx.send(text)
        await message.pin()
        new_combat = combat_data.Combat(ctx.message.channel.id, message.id)
        JsonDataControl.save_update(path, new_combat)
        await ctx.send("""**Справка: `init` или `i`**  
                `!init begin` - Начать бой
                `!init end` - Закончить бой
                `!init add <mod> <name>` - Добавить участника
                `!init remove <name>` - Убрать участника
                `!init next` - Передать очередь""")

    @init_combat.command()
    async def end(self, ctx):
        path = f'{self.bot.data_folder}{ctx.message.channel.id}.json'
        m = await self.get_file_data(ctx, path)


        msg = await ctx.fetch_message(m.message)
        await msg.unpin()
        os.remove(path)
        await ctx.send('**End of combat**')

    @init_combat.command()
    async def add(self, ctx, mod, *args):
        path = f'{self.bot.data_folder}{ctx.message.channel.id}.json'
        m = await self.get_file_data(ctx, path)
        rand = random.randint(1, 20)
        sign = '+'
        args = ' '.join(args)
        if not mod.isdigit():
            if mod[1:].isdigit():
                sign = mod[0]
                mod = mod[1:]
            else:
                args = mod + ' ' + args
                mod = 0
        sum = eval(str(rand) + sign + str(mod))
        actor = combat_data.Actor(args.strip(), ctx.message.author.id, sum) 
        m.add_actors(actor)
        if sum >= m.get_current().initiative and len(m.actors) > 1:
            m.turn += 1
        JsonDataControl.save_update(path, m)
        await self.update_message(ctx, m)
        await ctx.send(f'`{actor.name}` has been added to combat with initiative 1d20 ({rand}) {sign} {mod} = `{sum}`.')

    @init_combat.command()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, *args):
        path = f'{self.bot.data_folder}{ctx.message.channel.id}.json'
        m = await self.get_file_data(ctx, path)
        actor = m.get_current()
        name = ' '.join(args).strip()
        if actor.name == name:
            await ctx.send(f'You can\'t remove characters on their turn!')
            return
        try:
            if m.actors.index(m.get_actor(name)) < m.turn:
                m.turn -= 1
            m.remove_actors(name)
        except ValueError:
            await ctx.send(f'`{name}` has not been found')
            return
        JsonDataControl.save_update(path, m)
        await self.update_message(ctx, m)
        await ctx.send(f'`{name}` has been removed from combat')      

    @init_combat.command()
    async def next(self, ctx):
        path = f'{self.bot.data_folder}{ctx.message.channel.id}.json'
        m = await self.get_file_data(ctx, path)
        actor = m.get_current()
        if ctx.message.author.id == actor.author or ctx.message.author.guild_permissions.administrator:
            m.next_turn()
            actor = m.get_current()
            JsonDataControl.save_update(path, m)
            await self.update_message(ctx, m)
            await ctx.send(f"**Initiative {actor.initiative} (round {m.round}):** {actor.name} (<@{actor.author}>)```\n{actor.name}```")
        else:
            await ctx.send('It is not your turn!')

    async def update_message(self, ctx, combat: combat_data.Combat):
        msg = await ctx.fetch_message(combat.message)
        text = f"```md\nCurrent initiative: {combat.actors[combat.turn].initiative} (round {combat.round})\n"
        text += '=' * (len(text) - 7) + '\n'
        for i in range(len(combat.actors)):
            text += '# ' if i == combat.turn and combat.round > 0 else '  '
            actor = combat.actors[i]
            text += f"{actor.initiative}: {actor.name}\n"
        text += '```'
        await msg.edit(content= text)

    async def get_file_data(self, ctx, path) -> combat_data.Combat:
        try:
            with open(path, 'r') as file:
                data = file.read().replace('\n', '')
        except FileNotFoundError:
            await ctx.send('There is no combat in this channel!')
            return
        c = combat_data.Combat(**json.loads(data))
        c.actors = [combat_data.Actor.fromdict(x) for x in c.actors]
        return c

async def setup(bot):
    await bot.add_cog(Battle(bot))