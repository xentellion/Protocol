from client import Protocol
import discord
from discord.ext import commands
from discord.ui import Button, View


class Help(commands.Cog):
    def __init__(self, bot: Protocol):
        self.bot = bot
        super().__init__()
        
    @commands.command()
    async def help(self, ctx):
        currentPage = 0

        async def next_callback(interaction: discord.Interaction):
            nonlocal currentPage, msg
            currentPage += 1
            await msg.edit(embed=self.get_data(currentPage), view=myview)
            await interaction.response.defer(ephemeral= True)

        async def previous_callback(interaction: discord.Interaction):
            nonlocal currentPage, msg
            currentPage -= 1
            await msg.edit(embed=self.get_data(currentPage), view=myview)
            await interaction.response.defer(ephemeral= True)

        previousButton = Button(label="←", style=discord.ButtonStyle.blurple)
        nextButton = Button(label="→", style=discord.ButtonStyle.blurple)
        previousButton.callback = previous_callback
        nextButton.callback =  next_callback

        myview = View(timeout=None)
        myview.add_item(previousButton)
        myview.add_item(nextButton)

        msg = await ctx.send(embed = self.get_data(currentPage), view = myview)

    def get_data(self, currentPage):
        pageNum = currentPage % len(list(self.bot.help))
        pageTitle = list(self.bot.help[pageNum])[0]
        embed=discord.Embed(color=0x0080ff, title=pageTitle)
        # I really hate this place
        for key, val in self.bot.help[pageNum].items():
            for i in val:
                l = list(i.items())
                embed.add_field(name=l[0][0], value=l[0][1], inline=False)
                embed.set_footer(text=f"Page {pageNum+1} of {len(list(self.bot.help))}")
        return embed

async def setup(bot):
    await bot.add_cog(Help(bot))