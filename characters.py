from discord.ext import commands

class Chars(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
# char create <name> - создать персонажа
# char delete <name> - удалить персонажа
# char set <hp/en> <number> - задать максимум хп/энергии
# char add <hp/en/gold> <number> - добавить/убрать хп энергию золото
# char look <inv/notes> - посмотреть инвентарь/заметки
# char change <inv/notes> - изменить инвентарь/заметки

    @commands.command(name='char')
    async def init(self, ctx):
        await ctx.message.delete()
        init_command = ctx.message.content[5:].strip()

def setup(bot):
    bot.add_cog(Chars(bot))