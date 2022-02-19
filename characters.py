from discord.ext import commands
import character_data
import discord
import asyncio
import main
import json

class Chars(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
    @commands.group()
    async def campaign(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("""**Справка: `campaign`** 
                `!campaign create <name>` - Начать новую кампанию
                `!campaign delete <name>` - Удалить данные о кампании
                `!campaign list` - Посмотреть список активных кампаний на сервере
                `!campaign set <name>` - Установить кампанию как активную""")

    @campaign.command()
    @commands.has_permissions(administrator=True)
    async def create(self, ctx, *args):
        path = f'{main.folder}{main.server_folder}{ctx.message.guild.id}.json'
        camp = await self.get_file(ctx, path)
        name = ' '.join(args)
        if camp.find_campain(name):
            await ctx.send('There is already a campaign with that name!')
            return
        camp.add_campain(name.strip())
        self.save_update(path, camp)
        await ctx.send(f'Campaign `{name.strip()}` has been created!')

    @campaign.command()
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx, *args):
        path = f'{main.folder}{main.server_folder}{ctx.message.guild.id}.json'
        camp = await self.get_file(ctx, path)
        name = ' '.join(args)
        
        await ctx.send('**Are you sure you want to delete the campaign? Type yes/no**')
        answers = { 'yes', 'no'}

        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.content.lower() in answers
        
        try:
            request_msg = await main.bot.wait_for(event='message', check= check, timeout= 15.0)
        except asyncio.TimeoutError:
            await ctx.send('**Time for an answer has ended or the answer is wrong**')
        else:
            if request_msg.content.lower() == 'yes':
                camp.remove_campain(name.strip())
                self.save_update(path, camp)
                await ctx.send(f'Campaign `{name.strip()}` has been deleted!')
            else:
                await ctx.send('**Cancelled**')

    @campaign.command()
    @commands.has_permissions(administrator=True)
    async def list(self, ctx):
        path = f'{main.folder}{main.server_folder}{ctx.message.guild.id}.json'
        camp = await self.get_file(ctx, path)
        text = ''
        for i in camp.campaigns:
            text += ('# ' if i.name == camp.current_c else ' ') + i.name + '\n'
        await ctx.send(f"```md\nCAMPAIGNS OF THIS SERVER \n========================\n{text}```")

    @campaign.command()
    @commands.has_permissions(administrator=True)
    async def set(self, ctx, *args):
        path = f'{main.folder}{main.server_folder}{ctx.message.guild.id}.json'
        camp = await self.get_file(ctx, path)
        name = ' '.join(args)
        if camp.find_campain(name):
            camp.current_c = name
            self.save_update(path, camp)
            await ctx.send(f'Campaign `{name.strip()}` has been set as Active!')
        else:
            await ctx.send(f'Campaign `{name.strip()}` is not found!')

    @commands.group(aliases=['char', 'c'])
    async def chars(self, ctx):
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            await ctx.send("""**Справка: `char` или `c`** 
                    `!char create <name>` - создать персонажа
                    `!char delete <name>` - удалить персонажа
                    `!char set <hp/energy> <number>` - задать максимум хп/энергии
                    `!char add <hp/enerhy/gold> <number>` - добавить/убрать хп энергию золото
                    `!char look <inv/notes>` - посмотреть инвентарь/заметки
                    `!char change <inv/notes>` - изменить инвентарь/заметки
                """)

    # @chars.command()
    # async def add(self, ctx, name):
    #     path = f'{main.folder}{main.server_folder}{ctx.message.guild.id}.json'
    #     serv = await self.get_file(ctx, path)
    #     # check if there is second
    #     camp = serv.get_campain(serv.current_c)
    #     camp.add_character(character_data.Character(name, ctx.message.author.id))
    #     self.save_update(path, serv)
    #     await ctx.send(f'`{name}` has joind into campaign `{camp.name}`')


    async def get_file(self, ctx, path) -> character_data.DnDServer:
        try:
            with open(path, 'r') as file:
                data = file.read().replace('\n', '')
        except FileNotFoundError:
            print('New DnD server!')
            self.save_update(path, character_data.DnDServer())
            with open(path, 'r') as file:
                data = file.read().replace('\n', '')
            
        current_c = character_data.DnDServer(**json.loads(data))
        current_c.campaigns = [character_data.Campaign.fromdict(x) for x in current_c.campaigns]
        for camp in current_c.campaigns:
            camp.characters = [character_data.Character.fromdict(x) for x in camp.characters]
        return current_c

    def save_update(self, path, data):
        with open(path, 'w') as file:
            file.write(data.toJSON())    

def setup(bot):
    bot.add_cog(Chars(bot))