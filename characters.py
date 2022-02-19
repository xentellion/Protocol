from discord.ext import commands
import combat_data
import main

class Chars(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
    @commands.group(name='company')
    async def campain(self, ctx):
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            await ctx.send("""**Справка: `char` или `c`** 
                !init begin - Начать бой
                !init end - Закончить бой
                !init add <mod> <name> - Добавить участника
                !init remove <name> - Убрать участника
                !init next - Передать очередь""")

    # @campain.command()
    # @commands.has_permissions(administrator=True)
    # async def create(self, ctx, name:str):
    #     name = name.replace(' ', '_')
    #     id = ctx.message.guild.id
    #     comp = combat_data.Campain(name, id)
    #     path = f'{main.folder}{main.server_folder}{id}.json'
    #     try:
    #         f = open(path)
    #     except FileNotFoundError:
    #         self.save_update(path, comp)
    #     # self.save_update(path, comp)


# !char create <name> - создать персонажа
# !char delete <name> - удалить персонажа
# !char set <hp/en> <number> - задать максимум хп/энергии
# !char add <hp/en/gold> <number> - добавить/убрать хп энергию золото
# !char look <inv/notes> - посмотреть инвентарь/заметки
# !char change <inv/notes> - изменить инвентарь/заметки
    @commands.group(aliases=['char', 'c'])
    async def char_command(self, ctx):
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            await ctx.send("""**Справка: `char` или `c`** 
                !init begin - Начать бой
                !init end - Закончить бой
                !init add <mod> <name> - Добавить участника
                !init remove <name> - Убрать участника
                !init next - Передать очередь""")

    def save_update(self, path, data):
        with open(path, 'w') as file:
            file.write(data.toJSON())    

def setup(bot):
    bot.add_cog(Chars(bot))