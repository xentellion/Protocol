import discord
import random
import math
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
        self.directions = ['Up', 'Down']
        super().__init__()

    async def get_characters(self, interaction: discord.Interaction, char: str
    ) -> List[app_commands.Choice[str]]:
        path = f'{self.bot.data_folder}{interaction.channel.id}.json'
        combat = await self.get_file_data(interaction, path)
        if combat is None:
            return None
        return [
                app_commands.Choice(name= x.name, value= x.name )
                for x in combat.actors if char.lower() in x.name.lower()
            ]
    
    async def get_direction(self, interaction: discord.Interaction, selection: str
    ) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name= x, value= x)
            for x in self.directions if selection.lower() in x.lower()
        ]

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
        combat = await self.get_file_data(interaction, path)
        msg = await interaction.channel.fetch_message(combat.message)
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
        combat = await self.get_file_data(interaction, path)

        if any(x for x in combat.actors if x.name == name):
            await interaction.response.send_message(
                "There is already a character with that name", ephemeral=True)
            return

        rand = random.randint(1, 20)
        numb = rand + int(mod)
        
        actor = combat_data.Actor(name, interaction.user.id, numb) 
        combat.add_actors(actor)
        if numb >= combat.get_current().initiative and len(combat.actors) > 1:
            combat.turn += 1
        JsonDataControl.save_update(path, combat)
        await self.update_message(interaction, combat)
        await interaction.response.send_message(
            f'`{actor.name}` has been added to combat with initiative 1d20' + 
            f"({rand}) {'+' if int(mod) > 0 else '-'} {mod.lstrip('+-')} = `{numb}`.")

    @group.command(name="remove", description="Leave the combat")
    @app_commands.autocomplete(name = get_characters)
    async def remove(self, interaction: discord.Interaction, name:str):
        path = f'{self.bot.data_folder}{interaction.channel.id}.json'
        combat = await self.get_file_data(interaction, path)
        actor = combat.get_current()
        if actor.name == name:
            await interaction.response.send_message(
                f'You can\'t remove characters on their turn!',
                ephemeral=True)
            return
        try:
            if combat.actors.index(combat.get_actor(name)) < combat.turn:
                combat.turn -= 1
            combat.remove_actors(name)
        except ValueError:
            await interaction.response.send_message(
                f'`{name}` has not been found', ephemeral=True)
            return
        JsonDataControl.save_update(path, combat)
        await self.update_message(interaction, combat)
        await interaction.response.send_message(
            f'`{name}` has been removed from combat')
        
    @group.command(name="next", description="Progress the queue")
    async def remove(self, interaction: discord.Interaction):
        path = f'{self.bot.data_folder}{interaction.channel.id}.json'
        combat = await self.get_file_data(interaction, path)
        actor = combat.get_current()
        if interaction.user.id == actor.author or \
            interaction.user.guild_permissions.administrator:
            combat.next_turn()
            actor = combat.get_current()
            JsonDataControl.save_update(path, combat)
            await self.update_message(interaction, combat)
            await interaction.response.send_message(
                f"**Initiative {actor.initiative} (round {combat.round}):** {actor.name} (<@{actor.author}>)```\n{actor.name}```")
        else:
            await interaction.response.send_message(
                f'It is <@{actor.author}> turn!')
            
    @group.command(name="move", description="Move the character in queue!")
    # @app_commands.checks.has_permissions(administrator=True)
    @app_commands.autocomplete(name = get_characters, direction = get_direction)
    async def move(self, interaction: discord.Interaction, 
                   name:str, direction:str, shift:str=None):
        path = f'{self.bot.data_folder}{interaction.channel.id}.json'
        combat = await self.get_file_data(interaction, path)
        actor = combat.get_actor(name)
        index = combat.actors.index(actor)
        #current check
        current = combat.get_current()
        if current.name == name:
            await interaction.response.send_message(
                f'You can\'t move characters on their turn!',
                ephemeral=True)
            return
        # direction check
        if direction not in self.directions:
            await interaction.response.send_message(
                "No correct direction chosen", ephemeral= True)
            return
        # Extreme shift
        elif shift is None:
            actor.initiative = 50 \
                if direction == self.directions[0] \
                else -50
        # Digit check
        elif not shift.isdigit():
            await interaction.response.send_message(
                "Movement shift must be a number!", ephemeral= True)
            return 
        # Zero check
        elif shift == '0':
            await interaction.response.send_message(
                "Zero movement", ephemeral= True)
            return
        # Turn to int
        else:
            shift = int(shift)
            #new position
            new_pos = index - shift * (1 if direction == self.directions[0] else -1)
            # set first
            if new_pos <= 0:
                actor.initiative = combat.actors[0].initiative + 1
            # set last
            elif new_pos >= len(combat.actors):
                actor.initiative = combat.actors[-1].initiative - 1
            # Otherwise
            else:
                n1 = direction == self.directions[0]
                n2 = not n1
                
                up_init = combat.actors[new_pos - n1].initiative
                down_init = combat.actors[new_pos + n2].initiative 

                delta = up_init - down_init
                if delta <= 1:
                    for i in range(new_pos, len(combat.actors) - 1):
                        combat.actors[i].initiative -= (delta + 1)
                actor.initiative = up_init - 1
        # Analaize Queue
        combat.actors = sorted(combat.actors, key=lambda x: x.initiative, reverse=True)
        if combat.turn >= combat.actors.index(actor):
            combat.turn += 1
        # save
        JsonDataControl.save_update(path, combat)
        await self.update_message(interaction, combat)
        await interaction.response.send_message(
            f"{name} has moved in queue from position `{1 + index}` to `{1 + combat.actors.index(actor)}`!")

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

    async def get_file_data(self, interaction: discord.Interaction, path
                            ) -> combat_data.Combat:
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