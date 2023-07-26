import discord
from client import Protocol
from .Models.help import HelpView
from discord import app_commands
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot: Protocol):
        self.bot = bot
        super().__init__()

    @app_commands.command(name= "help", description= "Get Protocol info!")
    async def help(self, interaction: discord.Interaction):
        view = HelpView(self.bot)
        await interaction.response.send_message(
            embed= view.set_embed(self.bot.help[0]),
            view= view, 
            ephemeral= True
        )

async def setup(bot):
    await bot.add_cog(Help(bot))