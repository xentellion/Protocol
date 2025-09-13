import discord
from .Models.characters import StartForm, DeleteConfirm, EditForm
from src.data_control import JsonDataControl
from typing import List
from src.client import Protocol
from discord import app_commands
from discord.app_commands import locale_str
from discord.ext import commands


_ = lambda x: x


class Characters(commands.Cog):
    group = app_commands.Group(
        name="char", description="Set of commands for handling characters"
    )

    def __init__(self, bot: Protocol):
        self.bot = bot
        self.path = "{0}Campaigns/{1}.json".format(self.bot.data_folder, "{0}")
        super().__init__()

    async def get_characters(
        self, interaction: discord.Interaction, char: str
    ) -> List[app_commands.Choice[str]]:
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        campaign = server.campaigns[server.current_c]
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

    async def get_stats(
        self, interaction: discord.Interaction, selection: str
    ) -> List[app_commands.Choice[str]]:
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        campaign = server.campaigns[server.current_c]
        if campaign is None:
            return None

        return [
            app_commands.Choice(name=x, value=x)
            for x in campaign.stats
            if selection.lower() in x.lower()
        ]

    @group.command(name="create", description=locale_str(_("Create character for combat!")))
    async def add_char(self, interaction: discord.Interaction):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        if server.current_c in server.campaigns:
            campaign = server.campaigns[server.current_c]
            await interaction.response.send_modal(StartForm(self.bot, interaction.locale, campaign.stats))

        else:
            _ = self.bot.locale(interaction.locale)
            await interaction.response.send_message(_("There is no active campaign!"))

    @group.command(name="delete", description=locale_str(_("Remove the unused character!")))
    @app_commands.describe(
        name=locale_str(_("Character name"))
    )
    @app_commands.autocomplete(name=get_characters)
    async def remove_char(self, interaction: discord.Interaction, name: str):
        _ = self.bot.locale(interaction.locale)
        await interaction.response.send_message(
            _("## Are you sure you want to delete character {0}?").format(name),
            view=DeleteConfirm(self.bot, interaction.locale, name),
            ephemeral=False,
        )

    @group.command(name="edit", description=locale_str(_("Fix character stats!")))
    @app_commands.describe(
        name=locale_str(_("Character name")),
        stat=locale_str(_("Character stat"))
    )
    @app_commands.autocomplete(name=get_characters, stat=get_stats)
    async def edit_char(self, interaction: discord.Interaction, name: str, stat: str):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        if server.current_c in server.campaigns:
            char = server.campaigns[server.current_c].characters[name]
            await interaction.response.send_modal(EditForm(self.bot, interaction.locale, name, char, stat))
        else:
            _ = self.bot.locale(interaction.locale)
            await interaction.response.send_message(_("There is no active campaign!"))

    @group.command(name="status", description=locale_str(_("Check character stats!")))
    @app_commands.describe(
        name=locale_str(_("Character name"))
    )
    @app_commands.autocomplete(name=get_characters)
    async def show_char(self, interaction: discord.Interaction, name: str):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        _ = self.bot.locale(interaction.locale)
        if server.current_c not in server.campaigns:
            await interaction.response.send_message(_("There is no active campaign!"))
            return
        character = server.campaigns[server.current_c].characters[name]
        description = [_("Author - <@{0}>\n").format(character.author)]
        for k, stat in character.stats.items():
            if stat.has_max:
                text = _("**{0}:**\t{1}/{2}").format(k, stat.value, stat.max_value)
            else:
                text = _("**{0}:**\t{1}").format(k, stat.value)
            description.append(text)

        embed = discord.Embed(
            title=f"{name.capitalize()}",
            colour=discord.Color.gold(),
            description="\n".join(description),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @group.command(name="lose", description=locale_str(_("Recieve damage or lose money!")))
    @app_commands.describe(
        name=locale_str(_("Character name")),
        resource=locale_str(_("Affected resource")),
        value=locale_str(_("Amount of lost items or points"))
    )
    @app_commands.autocomplete(name=get_characters, resource=get_stats)
    async def spend_char(
        self, interaction: discord.Interaction, name: str, resource: str, value: int
    ):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        _ = self.bot.locale(interaction.locale)
        if server.current_c not in server.campaigns:
            await interaction.response.send_message(_("There is no active campaign!"))
            return
        character = server.campaigns[server.current_c].characters[name]

        character.stats[resource].value -= value
        if character.stats[resource].value < 0:
            await interaction.response.send_message(
                _("Not enough {0}! You dont have {1}!").format(resource.lower(), character.stats[resource].value * -1),
                ephemeral=False,
            )
            return

        server.campaigns[server.current_c].characters[name] = character
        JsonDataControl.save_update(self.path.format(interaction.guild.id), server)
        await interaction.response.send_message(
            _("{0} {1} have been spent! {3} now has {2} {1}").format(value, resource.lower(), character.stats[resource].value, name),
            ephemeral=False,
        )

    @group.command(
        name="gain", description=locale_str(_("Heal your wounds or get money!"))
    )
    @app_commands.describe(
        name=locale_str(_("Character name")),
        resource=locale_str(_("Affected resource")),
        value=locale_str(_("Amount of gained items or points"))
    )
    @app_commands.autocomplete(name=get_characters, resource=get_stats)
    async def restore_char(
        self, interaction: discord.Interaction, name: str, resource: str, value: int
    ):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        _ = self.bot.locale(interaction.locale)
        if server.current_c not in server.campaigns:
            await interaction.response.send_message(_("There is no active campaign!"))
            return
        character = server.campaigns[server.current_c].characters[name]

        character.stats[resource].value += value
        if character.stats[resource].has_max:
            if character.stats[resource].value > character.stats[resource].max_value:
                character.stats[resource].value = character.stats[resource].max_value

        server.campaigns[server.current_c].characters[name] = character
        JsonDataControl.save_update(self.path.format(interaction.guild.id), server)
        await interaction.response.send_message(
            _("{3} has recieved {0} {1}! They have {2} {1}").format(value, resource.lower(), character.stats[resource].value, name),
            ephemeral=False,
        )

    @group.command(
        name="rest",
        description=locale_str(_("Recover restorable resources")),
    )
    @app_commands.describe(
        name=locale_str(_("Character name"))
    )
    @app_commands.autocomplete(name=get_characters)
    async def rest_char(self, interaction: discord.Interaction, name: str):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        _ = self.bot.locale(interaction.locale)
        if server.current_c not in server.campaigns:
            await interaction.response.send_message(_("There is no active campaign!"))
            return
        character = server.campaigns[server.current_c].characters[name]
        for k, stat in character.stats.items():
            if not stat.has_max:
                continue
            stat.value = stat.max_value
            character.stats[k] = stat

        server.campaigns[server.current_c].characters[name] = character
        JsonDataControl.save_update(self.path.format(interaction.guild.id), server)
        await interaction.response.send_message(
            _("{0} has managed to rest and recover!").format(name.capitalize()), ephemeral=False
        )


async def setup(bot: Protocol):
    await bot.add_cog(Characters(bot))
