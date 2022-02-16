import random
from discord.ext import commands
import re

class RollDice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='roll')
    async def roll_send(self, ctx):
        await ctx.message.delete()
        start = ctx.message.content[5:].strip()
        start = ' '.join(start.split())

        text2 = re.sub(r'[\+\-\*\/]?\s?(\d+d\d+)\s?([\+\-\*\/]\s?\d+\s?)*(?!d)', '', start)
        text = text2 if len(text2) > 0 else 'Result'
        rolldata = start.replace(text2, '')
        rolldata = rolldata.replace(' ', '')
        rolldata = re.sub(r'([\+,\-,\*,\/])', r' \1 ', rolldata)
        demo = rolldata

        dice = re.compile(r'\d+d\d+')
        rolls = re.finditer(dice, rolldata)
        if len(re.findall(dice, rolldata)) < 1:
            await ctx.send(f'< No dices found in \"{start}\" >')
            return

        # rolling dices
        results = []
        for i in rolls:
            out = ' ('       
            parts = [int(part) for part in i.group(0).split('d')]
            dropped = [random.randint(1, parts[1]) for z in range(parts[0])]
            for a in range(len(dropped)):
                crit = '**' if dropped[a] == 1 or dropped[a] == parts[1] else ''
                out += f'{crit}{dropped[a]}{crit}'    
                out += ', ' if a+1 < len(dropped) else ')'  
            results.append((dropped, out, i.end())) 

        # demonstration
        for i in reversed(results):
            demo = demo[:i[2]] + i[1] + demo[i[2]:]

        # Calculating
        if len(results) == 1 and len(results[0][0]) > 1:
            calc = []
            try:
                calc = [eval(re.sub(dice, str(i), rolldata)) for i in results[0][0]]
            except:
                await ctx.send(f'Cannot calculate that')
                return
            rolldata = '('
            for i in calc:
                rolldata += f'{i}, '
            rolldata = rolldata[:-2] + ')'           
        else:
            for i in results:
                roll_res = 0
                for j in i[0]:
                    roll_res += j
                rolldata = re.sub(dice, str(roll_res), rolldata, 1)

            try:    
                rolldata = eval(rolldata) # FFS how do i remove that? SymPy?
            except:
                await ctx.send(f'Cannot calculate that')
                return

        await ctx.send(f'{ctx.message.author.mention}  🎲\n **{text}:** {demo} \n **Total: **{rolldata}')

def setup(bot):
    bot.add_cog(RollDice(bot))
