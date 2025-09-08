import discord
from .Models.characters import StartForm, DeleteConfirm, EditForm
from src.data_control import JsonDataControl
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

    @group.command(name="create", description="Create character for combat!")
    async def add_char(self, interaction: discord.Interaction):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        if server.current_c in server.campaigns:
            campaign = server.campaigns[server.current_c]
            await interaction.response.send_modal(StartForm(self.bot, campaign.stats))

        else:
            await interaction.response.send_message("There is no active campaign!")

    @group.command(name="delete", description="Remove the unused character!")
    @app_commands.autocomplete(name=get_characters)
    async def remove_char(self, interaction: discord.Interaction, name: str):
        await interaction.response.send_message(
            f"## Are you sure you want to delete character {name}?",
            view=DeleteConfirm(self.bot, name),
            ephemeral=True,
        )

    @group.command(name="edit", description="Fix character errors!")
    @app_commands.autocomplete(name=get_characters, stat=get_stats)
    async def edit_char(self, interaction: discord.Interaction, name: str, stat: str):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        if server.current_c in server.campaigns:
            char = server.campaigns[server.current_c].characters[name]
            await interaction.response.send_modal(EditForm(self.bot, name, char, stat))
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
        character = server.campaigns[server.current_c].characters[name]
        description = [f"Author - <@{character.author}>\n"]
        for k, stat in character.stats.items():
            if stat.has_max:
                text = f"**{k}:**\t{stat.value}/{stat.max_value}"
            else:
                text = f"**{k}:**\t{stat.value}"
            description.append(text)

        embed = discord.Embed(
            title=f"{name.capitalize()}",
            colour=discord.Color.gold(),
            description="\n".join(description),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @group.command(name="lose", description="Получите урон или потратьте деньги!")
    @app_commands.autocomplete(name=get_characters, resource=get_stats)
    async def spend_char(
        self, interaction: discord.Interaction, name: str, resource: str, value: int
    ):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        if server.current_c not in server.campaigns:
            await interaction.response.send_message("There is no active campaign!")
            return
        character = server.campaigns[server.current_c].characters[name]

        character.stats[resource].value -= value
        if character.stats[resource].value < 0:
            await interaction.response.send_message(
                f"Недостаточно {resource}! У вас не хватает {character.stats[resource].value * -1}!",
                ephemeral=False,
            )
            return

        server.campaigns[server.current_c].characters[name] = character
        JsonDataControl.save_update(self.path.format(interaction.guild.id), server)
        await interaction.response.send_message(
            f"{value} {resource.lower()} потрачены! у вас теперь {character.stats[resource].value} {resource}",
            ephemeral=False,
        )

    @group.command(
        name="gain", description="Излечите раны или получите денег - улучшите ситуацию!"
    )
    @app_commands.autocomplete(name=get_characters, resource=get_stats)
    async def restore_char(
        self, interaction: discord.Interaction, name: str, resource: str, value: int
    ):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        if server.current_c not in server.campaigns:
            await interaction.response.send_message("There is no active campaign!")
            return
        character = server.campaigns[server.current_c].characters[name]

        character.stats[resource].value += value
        if character.stats[resource].has_max:
            if character.stats[resource].value > character.stats[resource].max_value:
                character.stats[resource].value = character.stats[resource].max_value

        server.campaigns[server.current_c].characters[name] = character
        JsonDataControl.save_update(self.path.format(interaction.guild.id), server)
        await interaction.response.send_message(
            f"{value} {resource.lower()} получены! У вас теперь {character.stats[resource].value} {resource}",
            ephemeral=False,
        )

    @group.command(
        name="rest",
        description="Восстановить потраченные ресурсы",
    )
    @app_commands.autocomplete(name=get_characters)
    async def rest_char(self, interaction: discord.Interaction, name: str):
        server = await JsonDataControl.get_file(self.path.format(interaction.guild.id))
        if server.current_c not in server.campaigns:
            await interaction.response.send_message("There is no active campaign!")
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
            f"{name} удалось отдохнуть и восстановиться!", ephemeral=True
        )


async def setup(bot: Protocol):
    await bot.add_cog(Characters(bot))
