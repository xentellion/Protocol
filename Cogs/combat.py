import discord
import random
import combat_data
from typing import List
from client import Protocol
from data_control import *
from discord import app_commands
from discord.ext import commands

class Combat(commands.Cog):
    group = app_commands.Group(
        name="init", 
        description="Set of commands for handling combat")
    
    def __init__(self, bot: Protocol):
        self.bot = bot
        super().__init__()

    @group.command(name= "begin", description= "Initiate combat queue")
    async def init_begin(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "<:revolver:603601152885522465>", ephemeral=True)
        path = f'{self.bot.data_folder}{interaction.channel.id}.json'
        try:
            with open(path) as f:
                await interaction.response.send_message(
                    'There is already a combat in this channel!')
            return
        except FileNotFoundError:
            print('New Combat Session')
        text = "```md\nCurrent initiative: 0 (round 0)\n"
        text += '=' * (len(text) - 7) + '\n```'
        message = await interaction.channel.send(text)
        await message.pin()
        await interaction.channel.send("""**Справка:**
                `/init begin` - Start combat
                `/init add` - Join combat
                `/init next` - Progress queue
                `/init remove` - Leave combat
                `/init end` - Finish combat""")
        new_combat = combat_data.Combat(interaction.channel.id, message.id)
        JsonDataControl.save_update(path, new_combat)

    @group.command(name= "end", description= "Finish the combat")
    @app_commands.checks.has_permissions(administrator=True)
    async def init_end(self, interaction: discord.Interaction):
        path = f'{self.bot.data_folder}{interaction.channel.id}.json'
        m = await self.get_file_data(interaction, path)
        msg = await interaction.channel.fetch_message(m.message)
        await msg.unpin()
        os.remove(path)
        await interaction.response.send_message('**End of combat**')

    @group.command(name="add", description="Join the combat!")
    async def add(self, interaction: discord.Interaction, 
                  mod:str, name:str):
        if not mod.lstrip("+-").isdigit():
            await interaction.response.send_message(
                "Modifier is not a number!", ephemeral=True)
            return
        if len(name) < 3:
            await interaction.response.send_message(
                "Name too short", ephemeral=True)
            return
        
        path = f'{self.bot.data_folder}{interaction.channel.id}.json'
        m = await self.get_file_data(interaction, path)

        if any(x for x in m.actors if x.name == name):
            await interaction.response.send_message(
                "There is already a character with that name", ephemeral=True)
            return

        rand = random.randint(1, 20)
        numb = rand + int(mod)
        
        actor = combat_data.Actor(name, interaction.user.id, numb) 
        m.add_actors(actor)
        if numb >= m.get_current().initiative and len(m.actors) > 1:
            m.turn += 1
        JsonDataControl.save_update(path, m)
        await self.update_message(interaction, m)
        await interaction.response.send_message(
            f'`{actor.name}` has been added to combat with initiative 1d20' + 
            f"({rand}) {'+' if int(mod) > 0 else '-'} {mod.lstrip('+-')} = `{numb}`.")

    @group.command(name="remove", description="Leave the combat")
    async def remove(self, interaction: discord.Interaction, name:str):
        path = f'{self.bot.data_folder}{interaction.channel.id}.json'
        m = await self.get_file_data(interaction, path)
        actor = m.get_current()
        if actor.name == name:
            await interaction.response.send_message(
                f'You can\'t remove characters on their turn!',
                ephemeral=True)
            return
        try:
            if m.actors.index(m.get_actor(name)) < m.turn:
                m.turn -= 1
            m.remove_actors(name)
        except ValueError:
            await interaction.response.send_message(
                f'`{name}` has not been found', ephemeral=True)
            return
        JsonDataControl.save_update(path, m)
        await self.update_message(interaction, m)
        await interaction.response.send_message(
            f'`{name}` has been removed from combat')
        
    @group.command(name="next", description="Progress the queue")
    async def remove(self, interaction: discord.Interaction):
        path = f'{self.bot.data_folder}{interaction.channel.id}.json'
        m = await self.get_file_data(interaction, path)
        actor = m.get_current()
        if interaction.user.id == actor.author or \
            interaction.user.guild_permissions.administrator:
            m.next_turn()
            actor = m.get_current()
            JsonDataControl.save_update(path, m)
            await self.update_message(interaction, m)
            await interaction.response.send_message(
                f"**Initiative {actor.initiative} (round {m.round}):** {actor.name} (<@{actor.author}>)```\n{actor.name}```")
        else:
            await interaction.response.send_message(
                f'It is <@{actor.author}> turn!')

    #<------------------------------------------------------------>

    async def update_message(self, interaction, combat: combat_data.Combat):
        msg = await interaction.channel.fetch_message(combat.message)
        text = f"```md\nCurrent initiative: {combat.actors[combat.turn].initiative} (round {combat.round})\n"
        text += '=' * (len(text) - 7) + '\n'
        for i in range(len(combat.actors)):
            text += '# ' if i == combat.turn and combat.round > 0 else '  '
            actor = combat.actors[i]
            text += f"{actor.initiative}: {actor.name}\n"
        text += '```'
        await msg.edit(content= text)

    async def get_file_data(
            self, interaction: discord.Interaction, path) -> combat_data.Combat:
        try:
            with open(path, 'r') as file:
                data = file.read().replace('\n', '')
        except FileNotFoundError:
            await interaction.response.send_message(
                'There is no combat in this channel!')
            return
        c = combat_data.Combat(**json.loads(data))
        c.actors = [combat_data.Actor.fromdict(x) for x in c.actors]
        return c


async def setup(bot: Protocol):
    await bot.add_cog(Combat(bot))