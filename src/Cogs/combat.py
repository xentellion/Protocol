import os
import json
import discord
import random
import src.combat_data as combat_data
from typing import List
from src.client import Protocol
from src.data_control import JsonDataControl
from discord import app_commands
from discord.app_commands import locale_str
from discord.ext import commands

_ = lambda x: x


class Combat(commands.Cog):
    group = app_commands.Group(
        name="init", description="Set of commands for handling combat"
    )

    def __init__(self, bot: Protocol):
        self.bot = bot
        self.directions = ["Up", "Down"]
        self.path = "{0}Combat/{1}.json".format(self.bot.data_folder, {0})
        super().__init__()

    async def get_characters(
        self, interaction: discord.Interaction, char: str
    ) -> List[app_commands.Choice[str]]:
        combat = await self.get_file_data(
            interaction, self.path.format(interaction.channel.id)
        )
        if combat is None:
            return None

        return [
            app_commands.Choice(name=x.name, value=x.name)
            for x in combat.actors
            if char.lower() in x.name.lower()
        ]

    async def get_direction(
        self, interaction: discord.Interaction, selection: str
    ) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=x, value=x)
            for x in self.directions
            if selection.lower() in x.lower()
        ]

    @group.command(name="begin", description=locale_str(_("Initiate combat")))
    async def init_begin(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "<:revolver:603601152885522465>",
            ephemeral=True,
        )
        path = self.path.format(interaction.channel.id)
        _ = self.bot.locale(interaction.locale)
        if os.path.exists(path):
            await interaction.response.send_message(
                _("There is already a combat in this channel!")
            )
            return
        message = await interaction.channel.send(
            "\n".join(self.combat_header(interaction.locale) + ["```"])
        )
        await message.pin()
        await interaction.channel.send(
            _("""**Tips:**
                `/init begin` - Start combat
                `/init add` - Join combat
                `/init next` - Progress queue
                `/init remove` - Leave combat
                `/init end` - Finish combat"""
            )
        )
        JsonDataControl.save_update(
            path, combat_data.Combat(interaction.channel.id, message.id)
        )

    @group.command(name="end", description=locale_str(_("Finish the combat")))
    @app_commands.checks.has_permissions(administrator=True)
    async def init_end(self, interaction: discord.Interaction):
        path = self.path.format(interaction.channel.id)
        combat = await self.get_file_data(interaction, path)
        if combat is None:
            return
        for temp in combat.temp_chars:
            await self.remove_temp_char(interaction, temp, combat)
        msg = await interaction.channel.fetch_message(combat.message)
        await msg.unpin()
        os.remove(path)
        _ = self.bot.locale(interaction.locale)
        await interaction.response.send_message(_("**End of combat**"))

    @group.command(name="add", description=locale_str(_("Join the combat!")))
    @app_commands.describe(
        mod=locale_str(_("Initiative modifier")),
        name=locale_str(_("Character name"))
    )
    async def add(
        self,
        interaction: discord.Interaction,
        mod: str,
        name: str,
    ):
        _ = self.bot.locale(interaction.locale)
        if not mod.lstrip("+-").isdigit():
            await interaction.response.send_message(
                _("Modifier is not a number!"), ephemeral=True
            )
            return
        if len(name) < 3:
            await interaction.response.send_message(_("Name too short"), ephemeral=True)
            return

        path = self.path.format(interaction.channel_id)
        combat = await self.get_file_data(interaction, path)
        if combat is None:
            return
        if combat.check_actor(name):
            await interaction.response.send_message(
                _("There is already a character with that name"), ephemeral=True
            )
            return

        rand = random.randint(1, 20)
        numb = rand + int(mod)

        actor = combat_data.Actor(name, interaction.user.id, numb)
        combat.add_actors(actor)
        if numb >= combat.get_current().initiative and len(combat.actors) > 1:
            combat.turn += 1

        JsonDataControl.save_update(path, combat)
        await self.update_message(interaction, combat)
        text = _("`{0}` has joined the combat with initiative 1d20({1}) {2} {3} = `{4}`")
        await interaction.response.send_message(
            text.format(actor.name, rand, '+' if int(mod) > 0 else '-', mod.lstrip('+-'), numb)
        )

    @group.command(name="remove", description=locale_str(_("Leave the combat")))
    @app_commands.describe(
        name=locale_str(_("Character name"))
    )
    @app_commands.autocomplete(name=get_characters)
    async def remove(self, interaction: discord.Interaction, name: str):
        path = self.path.format(interaction.channel.id)
        combat = await self.get_file_data(interaction, path)
        if combat is None:
            return
        actor = combat.get_current()
        _ = self.bot.locale(interaction.locale)
        if actor.name == name:
            await interaction.response.send_message(
                _("You can't remove characters on their turn!"),
                ephemeral=True,
            )
            return
        try:
            if combat.actors.index(combat.get_actor(name)) < combat.turn:
                combat.turn -= 1
            combat.remove_actors(name)
        except ValueError:
            await interaction.response.send_message(
                _("`{0}` has not been found").format(name), ephemeral=True
            )
            return
        if name in combat.temp_chars:
            await self.remove_temp_char(interaction, name, combat)

        JsonDataControl.save_update(path, combat)
        await self.update_message(interaction, combat)
        await interaction.response.send_message(
            _("`{0}` has been removed from combat").format(name)
        )

    @group.command(name="next", description=locale_str(_("Progress the queue")))
    async def next(self, interaction: discord.Interaction):
        path = self.path.format(interaction.channel.id)
        combat = await self.get_file_data(interaction, path)
        if combat is None:
            return
        actor = combat.get_current()
        _ = self.bot.locale(interaction.locale)
        if (
            interaction.user.id == actor.author
            or interaction.user.guild_permissions.administrator
        ):
            combat.next_turn()
            actor = combat.get_current()
            JsonDataControl.save_update(path, combat)
            await self.update_message(interaction, combat)
            text = _("**Initiative {0} (round {1}):** {2} (<@{3}>)```\n{2}```")
            await interaction.response.send_message(
                text.format(actor.initiative, combat.round, actor.name, actor.author)
            )
        else:
            await interaction.response.send_message(_("It is <@{0}> turn!").format(actor.author))

    @group.command(name="move", description=locale_str(_("Move the character in queue!")))
    @app_commands.describe(
        name=locale_str(_("Character name")),
        direction=locale_str(_("Movement direction")),
        shift=locale_str(_("Amount of positions to move"))
    )
    @app_commands.autocomplete(name=get_characters, direction=get_direction)
    async def move(
        self,
        interaction: discord.Interaction,
        name: str,
        direction: str,
        shift: str = None,
    ):
        path = self.path.format(interaction.channel.id)
        combat = await self.get_file_data(interaction, path)
        actor = combat.get_actor(name)
        index = combat.actors.index(actor)
        # current check
        current = combat.get_current()
        _ = self.bot.locale(interaction.locale)
        if current.name == name:
            await interaction.response.send_message(
                _("You can't move characters on their turn!"), ephemeral=True
            )
            return
        # direction check
        if direction not in self.directions:
            await interaction.response.send_message(
                _("Incorrect direction"), ephemeral=True
            )
            return
        # Extreme shift
        elif shift is None:
            actor.initiative = 50 if direction == self.directions[0] else -50
        # Digit check
        elif not shift.isdigit():
            await interaction.response.send_message(
                _("Movement shift must be a number!"), ephemeral=True
            )
            return
        # Zero check
        elif shift == "0":
            await interaction.response.send_message(_("Zero movement"), ephemeral=True)
            return
        # Turn to int
        else:
            shift = int(shift)
            # new position
            new_pos = index - shift * (1 if direction == self.directions[0] else -1)
            # set first
            if new_pos <= 0:
                actor.initiative = combat.actors[0].initiative + 1
            # set last
            elif new_pos >= len(combat.actors) - 1:
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
                        combat.actors[i].initiative -= delta + 1
                actor.initiative = up_init - 1
        # Analaize Queue
        combat.actors = sorted(combat.actors, key=lambda x: x.initiative, reverse=True)
        new_index = combat.actors.index(actor)
        if index > combat.turn >= new_index:
            combat.turn += 1
        elif index < combat.turn <= new_index:
            combat.turn -= 1
        # save
        JsonDataControl.save_update(path, combat)
        await self.update_message(interaction, combat)
        await interaction.response.send_message(
            _("{0} has moved in queue from position `{1}` to `{2}`!").format(name, index + 1, new_index + 1)
        )

    # <------------------------------------------------------------>

    async def update_message(self, interaction, combat: combat_data.Combat):
        msg = await interaction.channel.fetch_message(combat.message)
        text = self.combat_header(interaction.locale, combat.actors[combat.turn].initiative, combat.round)
        for i in range(len(combat.actors)):
            actor = combat.actors[i]
            text.append(
                f"{'# ' if i == combat.turn and combat.round > 0 else '  '}{actor.initiative}: {actor.name}"
            )
        text.append("```")
        await msg.edit(content="\n".join(text))

    async def get_file_data(
        self, interaction: discord.Interaction, path
    ) -> combat_data.Combat:
        try:
            with open(path, "r") as file:
                data = file.read().replace("\n", "")
        except FileNotFoundError:
            _ = self.bot.locale(interaction.locale)
            await interaction.response.send_message(
                _("There is no combat in this channel!")
            )
            return
        c = combat_data.Combat(**json.loads(data))
        # c.actors = [combat_data.Actor.fromdict(x) for x in c.actors]
        c.actors = [combat_data.Actor(**x) for x in c.actors]
        return c

    def combat_header(self, locale: str, initiative: int = 0, round: int = 0):
        _ = self.bot.locale(locale)
        head = _("```md\nCurrent initiative: {0} (round {1})").format(initiative, round)
        return [head, "=" * (len(head) - 7)]

    async def remove_temp_char(self, interaction, name, combat: combat_data.Combat):
        combat.temp_chars.remove(name)
        path_c = f"{self.bot.data_folder}Campaigns/{interaction.guild.id}.json"
        server = await JsonDataControl.get_file(path_c)
        del server.campaigns[server.current_c][name]
        JsonDataControl.save_update(path_c, server)


async def setup(bot: Protocol):
    await bot.add_cog(Combat(bot))
