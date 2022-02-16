from discord.ext import commands
import json
import combat_data
import random
import main
import os
import asyncio
import discord

class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
 
    @commands.command(name='init')
    async def combat(self, ctx):
        await ctx.message.delete()
        init_command = ctx.message.content[5:].strip()
        data = init_command.split()
        if data[0] == 'begin':
            path = f'{main.folder}{ctx.message.channel.id}.json'
            try:
                f = open(path)
                await ctx.send('There is already a combat in this channel!')
                f.close()
                return
            except FileNotFoundError:
                print('New Combat Session')

            text = "```md\nCurrent initiative: 0 (round 0)\n```"
            text += '=' * (len(text) - 7) + '\n'
            message = await ctx.send(text)
            await message.pin()
            new_combat = combat_data.Combat(ctx.message.channel.id, message.id)
            self.save_update(path, new_combat)
            await ctx.send("""**Справка:** 
                        !init begin - Начать бой
                        !init end - Закончить бой
                        !init add <mod> <name> - Добавить участника
                        !init remove <name> - Убрать участника
                        !init next - Передать очередь""")
            
        elif data[0] == 'end':
            path = f'{main.folder}{ctx.message.channel.id}.json'
            m = await self.get_file_data(ctx, path)
            await ctx.send('**Are you sure you wnt to stop the combat? Type yes/no**')
            answers = { 'yes', 'no'}

            def check(m: discord.Message):
                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.content.lower() in answers

            try:
                request_msg = await main.bot.wait_for(event='message', check= check, timeout= 15.0)
            except asyncio.TimeoutError:
                await ctx.send('**Time for an answer has ended or the answer is wrong**')
            else:
                if request_msg.content.lower() == 'yes':
                    msg = await ctx.fetch_message(m.message)
                    await msg.delete()
                    os.remove(path)
                    await ctx.send('**End of combat**')
                else:
                    await ctx.send('**Cancelled**')
            
        elif data[0] == 'add':
            path = f'{main.folder}{ctx.message.channel.id}.json'
            m = await self.get_file_data(ctx, path)
            rand = random.randint(1, 20)
            sign = '+'
            try:
                if not data[1].isdigit():
                    if data[1][1:].isdigit():
                        sign = data[1][0]
                        data[1] = data[1][1:]
                    else:
                        data.insert(1, 0)
                sum = eval(str(rand) + sign + str(data[1]))
                actor = combat_data.Actor(''.join(data[2:]), ctx.message.author.id, sum)       
            except:
                await ctx.send('Incorrect input!')
                return
            m.add_actors(actor.__dict__)
            self.save_update(path, m)
            await self.update_message(ctx, m)
            await ctx.send(f'`{actor.name}` has been added to combat with initiative 1d20 ({rand}) {sign} {data[1]} = `{sum}`.')

        elif data[0] == 'remove':
            path = f'{main.folder}{ctx.message.channel.id}.json'
            m = await self.get_file_data(ctx, path)
            actor = m.get_current()
            if actor['name'] == data[1]:
                await ctx.send(f'You can\'t remove characters on their turn!')
                return
            try:
                if m.actors.index(m.get_actor(data[1])) < m.turn:
                    m.turn -= 1
                m.remove_actors(data[1])
            except ValueError:
                await ctx.send(f'`{data[1]}` has not been found')
                return
            self.save_update(path, m)
            await self.update_message(ctx, m)
            await ctx.send(f'`{data[1]}` has been removed from combat')

        elif data[0] == 'next':
            path = f'{main.folder}{ctx.message.channel.id}.json'
            m = await self.get_file_data(ctx, path)
            actor = m.get_current()
            if ctx.message.author.id == actor['author'] or ctx.message.author.guild_permissions.administrator:
                m.next_turn()
                actor = m.get_current()
                self.save_update(path, m)
                await self.update_message(ctx, m)
                await ctx.send(f"**Initiative {actor['initiative']} (round {m.round}):** {actor['name']} (<@{actor['author']}>)```\n{actor['name']}```")
            else:
                await ctx.send('It is not your turn!')

    async def update_message(self, ctx, combat: combat_data.Combat):
        msg = await ctx.fetch_message(combat.message)
        text = f"```md\nCurrent initiative: {combat.actors[combat.turn].get('initiative')} (round {combat.round})\n"
        text += '=' * (len(text) - 7) + '\n'
        for i in range(len(combat.actors)):
            text += '# ' if i == combat.turn and combat.round > 0 else '  '
            actor = combat.actors[i]
            text += f"{actor.get('initiative')}: {actor.get('name')}\n"
        text += '```'
        await msg.edit(content= text)

    def save_update(self, path, data):
        with open(path, 'w') as file:
            file.write(data.toJSON())

    async def get_file_data(self, ctx, path):
        try:
            f = open(path)
            data = json.load(f)
            f.close()
        except FileNotFoundError:
            await ctx.send('There is no combat in this channel!')
            return
        return combat_data.Combat(data)

def setup(bot):
    bot.add_cog(Battle(bot))
