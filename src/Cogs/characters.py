import discord
import math
from .Models.characters import *
from src.data_control import *
from typing import List
from src.client import Protocol
from discord import app_commands
from discord.ext import commands


class Characters(commands.Cog):
    group = app_commands.Group(
        name="char", description="Set of commands for handling characters"
    )

    def __init__(self, bot: Protocol):
        self.bot = bot
        self.choises = ["Energy", "Reaction points", "Style points"]
        self.rest = ["Short", "Long"]
        self.path = "{0}Campaigns/{1}.json".format(self.bot.data_folder, "{0}")
        super().__init__()

    async def get_characters(
        self, interaction: discord.Interaction, char: str
    ) -> List[app_commands.Choice[str]]:
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        campaign = Campaign(server.campaigns[server.current_c])
        if campaign is None:
            return None

        if interaction.user.guild_permissions.administrator:
            return [app_commands.Choice(name=x[0], value=x[0]) for x in campaign]
        else:
            return [
                app_commands.Choice(name=x[0], value=x[0])
                for x in campaign
                if x[1].author == interaction.user.id
            ]

    async def resources_types(
        self, interaction: discord.Interaction, selection: str
    ) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=x, value=x)
            for x in self.choises
            if selection.lower() in x.lower()
        ]

    async def rest_types(
        self, interaction: discord.Interaction, selection: str
    ) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=x, value=x)
            for x in self.rest
            if selection.lower() in x.lower()
        ]

    @group.command(name="create", description="Create character for combat!")
    # ->
    async def add_char(self, interaction: discord.Interaction):
        camp = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        if camp.current_c in camp.campaigns:
            await interaction.response.send_modal(StartForm(self.bot))
        else:
            await interaction.response.send_message("There is no active campaign!")

    @group.command(name="delete", description="Remove the unused character!")
    @app_commands.autocomplete(name=get_characters)
    # ->
    async def remove_char(self, interaction: discord.Interaction, name: str):
        await interaction.response.send_message(
            f"## Are you sure you want to delete character {name}?",
            view=DeleteConfirm(self.bot, name),
            ephemeral=True,
        )

    @group.command(name="edit", description="Fix character errors!")
    @app_commands.autocomplete(name=get_characters)
    # ->
    async def edit_char(self, interaction: discord.Interaction, name: str):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        if server.current_c in server.campaigns:
            await interaction.response.send_modal(EditForm(self.bot, name))
        else:
            await interaction.response.send_message("There is no active campaign!")

    @group.command(name="status", description="Check character stats!")
    @app_commands.autocomplete(name=get_characters)
    # ->
    async def show_char(self, interaction: discord.Interaction, name: str):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        if server.current_c not in server.campaigns:
            await interaction.response.send_message("There is no active campaign!")
            return
        character = Campaign(server.campaigns[server.current_c])[name]

        description = [
            f"Author - <@{character.author}>\n",
            f"**Health** ❤️ {character.hp}/{character.max_hp}",
            f"**Energy** ⚡ {character.energy}/{character.max_energy}",
        ]
        if character.max_reaction > 0:
            description.append(
                f"**Reaction** 👁️ {character.reaction}/{character.max_reaction}"
            )
        if character.max_style > 0:
            description.append(f"**Style** ✨ {character.style}/{character.max_style}")

        embed = discord.Embed(
            title=f"{name.capitalize()}",
            colour=discord.Color.gold(),
            description="\n".join(description),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @group.command(name="damage", description="Register an attack on your character")
    @app_commands.autocomplete(name=get_characters)
    # ->
    async def damage_char(
        self, interaction: discord.Interaction, name: str, damage: int
    ):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        if server.current_c not in server.campaigns:
            await interaction.response.send_message("There is no active campaign!")
            return
        character = Campaign(server.campaigns[server.current_c])[name]

        character.hp -= abs(damage)
        text = []
        warn = False

        if character.hp <= 0:
            if character.hp + character.max_hp < character.max_hp // 2:
                text.append(f"**⚠️ CRITICAL ⚠️**\n\n*{name}* is **DEAD**\n")
            else:
                text.append(f"**⚠️ CRITICAL ⚠️**\n\n*{name}* is **IN COMA**\n")
            character.hp = 0
            warn = True
        text.append(f"**Health ❤️**: {character.hp}/{character.max_hp}")

        server.campaigns[server.current_c][name] = character
        JsonDataControl.save_update(self.path.format(interaction.guild.id), server)

        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"{name} status",
                description="".join(text),
                color=discord.Color.red() if warn else discord.Color.green(),
            ),
            ephemeral=not warn,
        )

    @group.command(name="heal", description="Heal your character!")
    @app_commands.autocomplete(name=get_characters)
    async def heal_char(self, interaction: discord.Interaction, name: str, heal: int):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        if server.current_c not in server.campaigns:
            await interaction.response.send_message("There is no active campaign!")
            return
        character = Campaign(server.campaigns[server.current_c])[name]

        character.hp += abs(heal)
        if character.hp > character.max_hp:
            character.hp = character.max_hp

        server.campaigns[server.current_c][name] = character
        JsonDataControl.save_update(self.path.format(interaction.guild.id), server)

        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"{name} status",
                description=f"**Health ❤️**: {character.hp}/{character.max_hp}",
                color=discord.Color.green(),
            ),
            ephemeral=True,
        )

    @group.command(name="spend", description="Spend energy, reaction or style points!")
    @app_commands.autocomplete(name=get_characters, resource=resources_types)
    async def spend_char(
        self, interaction: discord.Interaction, name: str, resource: str, value: int
    ):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        if server.current_c not in server.campaigns:
            await interaction.response.send_message("There is no active campaign!")
            return
        character = Campaign(server.campaigns[server.current_c])[name]
        warn = True

        if resource == self.choises[0]:
            if character.energy < abs(value):
                await interaction.response.send_message(
                    "You don't have enough energy for that action!", ephemeral=True
                )
                return
            elif character.energy == abs(value):
                character.energy = 0
                await interaction.response.send_message(
                    "You have just spend all of your energy!", ephemeral=True
                )
            else:
                character.energy -= abs(value)
                warn = False

        if resource == self.choises[1]:
            if character.reaction < abs(value):
                await interaction.response.send_message(
                    "You don't have enough reaction for that action!", ephemeral=True
                )
                return
            elif character.reaction == abs(value):
                character.reaction = 0
                await interaction.response.send_message(
                    "You have just spend all of your reaction!", ephemeral=True
                )
            else:
                character.reaction -= abs(value)
                warn = False

        if resource == self.choises[2]:
            if character.style < value:
                await interaction.response.send_message(
                    "You don't have enough style for that action!", ephemeral=True
                )
                return
            elif character.style == abs(value):
                character.style = 0
                await interaction.response.send_message(
                    "You have just spend all of your style!", ephemeral=True
                )
            else:
                character.style -= abs(value)
                warn = False

        server.campaigns[server.current_c][name] = character
        JsonDataControl.save_update(self.path.format(interaction.guild.id), server)
        if not warn:
            await interaction.response.send_message(
                f"{value} {resource.lower()} has been spent! Call status to check it out",
                ephemeral=True,
            )

    @group.command(
        name="restore", description="Restore energy, reaction or style points!"
    )
    @app_commands.autocomplete(name=get_characters, resource=resources_types)
    async def restore_char(
        self, interaction: discord.Interaction, name: str, resource: str, value: int
    ):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        if server.current_c not in server.campaigns:
            await interaction.response.send_message("There is no active campaign!")
            return
        character = Campaign(server.campaigns[server.current_c])[name]
        warn = True

        if resource == self.choises[0]:
            if character.energy == character.max_energy:
                await interaction.response.send_message(
                    "You don't have to restore energy!", ephemeral=True
                )
                return
            else:
                character.energy += abs(value)
                if character.energy > character.max_energy:
                    character.energy = character.max_energy
                warn = False
        elif resource == self.choises[1]:
            if character.reaction == character.max_reaction:
                await interaction.response.send_message(
                    "You don't have to restore reaction!", ephemeral=True
                )
                return
            else:
                character.reaction += abs(value)
                if character.reaction > character.max_reaction:
                    character.reaction = character.max_reaction
                warn = False
        elif resource == self.choises[2]:
            if character.style == character.max_style:
                await interaction.response.send_message(
                    "You don't have to restore style!", ephemeral=True
                )
                return
            else:
                character.style += abs(value)
                if character.style > character.max_style:
                    character.style = character.max_style
                warn = False

        server.campaigns[server.current_c][name] = character
        JsonDataControl.save_update(self.path.format(interaction.guild.id), server)
        if not warn:
            await interaction.response.send_message(
                f"{value} {resource.lower()} has been restored! Call status to check it out",
                ephemeral=True,
            )

    @group.command(
        name="rest",
        description="Let the character rest and restore some health and energy",
    )
    @app_commands.autocomplete(name=get_characters, rest=rest_types)
    async def rest_char(self, interaction: discord.Interaction, name: str, rest: str):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        if server.current_c not in server.campaigns:
            await interaction.response.send_message("There is no active campaign!")
            return
        character = Campaign(server.campaigns[server.current_c])[name]

        if rest == self.rest[0]:
            character.hp += math.ceil(character.max_hp / 4)
            character.energy += math.ceil(character.max_energy / 2)
        elif rest == self.rest[1]:
            character.hp += math.ceil(character.max_hp / 2)
            character.energy = character.max_energy

        if character.hp > character.max_hp:
            character.hp = character.max_hp
        if character.energy > character.max_energy:
            character.energy = character.max_energy

        character.reaction = character.max_reaction
        character.style = character.max_style

        server.campaigns[server.current_c][name] = character
        JsonDataControl.save_update(self.path.format(interaction.guild.id), server)
        await interaction.response.send_message(
            f"{name} has rested and restored some energy and health!", ephemeral=True
        )


async def setup(bot: Protocol):
    await bot.add_cog(Characters(bot))
