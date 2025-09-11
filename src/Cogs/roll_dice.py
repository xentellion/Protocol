import re
from random import randint
from discord.ext import commands
from discord import errors


regex_comment = (
    r"[\+\-\*\/]?\s?(\d+\.?\d*d\d+\.?\d*)\s?([\+\-\*\/]\s?\d+\.?\d*\s?)*(?!d)"
)
regex_brac = r"\((?=.*((\d+d\d+)|[\+\-\/]))[^()]*\)"
regex_dice = r"(\d+\.?\d*d\d+\.?\d*)"
regex_cursive = r"\*{2,}"


class RollDice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roll")
    async def roll_send(self, ctx, *, input_query: str):
        _ = self.bot.locale(ctx.guild.preferred_locale)
        try:
            await ctx.message.delete()
        except errors.NotFound:
            return
        # --------Separate commentary and strip spaces
        comment = re.sub(regex_comment, "", input_query).strip()
        expression = input_query.replace(comment, "").strip()
        # --------Separate dices and roll them
        split = re.split(regex_dice, expression)
        split = [spl.replace("*", "\*") for spl in split]

        text_result = []
        roll_result = []
        for j in range(1, len(split), 2):
            dices = list(map(int, split[j].split("d")))
            if dices[0] > 100:
                await ctx.send(_("Too many dices in one throw"))
                return
            split[j] = f"{dices[0]}d{dices[1]}"
            rand = [randint(1, dices[1]) for _ in range(dices[0])]
            roll_result.append(rand)

            demo_roll = []
            for k in rand:
                crit = "**" if k == dices[1] or k == 1 else ""
                demo_roll.append(f"{crit}{str(k)}{crit}")
            try:
                text_result.append(f"{split[j]}({', '.join(demo_roll)}){split[j+1]}")
            except IndexError:
                await ctx.send(_('No dices found in "{0}"').format(input_query))
                return
        # --------Calculate rolls
        # one dice - calclulates all rolls individually
        # multile - sums all up
        if len(roll_result) > 1:
            for j in roll_result:
                expression = re.sub(regex_dice, str(sum(j)), expression, 1)
            try:
                summa = round(eval(expression), 2)
            except SyntaxError:
                await ctx.send(_("I can't calculate that!"))
                return
        else:
            expression = [
                re.sub(regex_dice, str(roll), expression, 1) for roll in roll_result[0]
            ]
            try:
                expression = [round(eval(j), 2) for j in expression]
            except SyntaxError:
                await ctx.send(_("I can't calculate that!"))
                return
            summa = expression[0] if len(expression) == 1 else tuple(expression)
        # --------Result
        comment = _("Result") if comment == "" else re.sub(regex_cursive, "*", comment)
        total = _('Total')
        message = f"{ctx.message.author.mention} 🎲\n**{comment}:** {''.join(text_result)} \n**{total}: **{summa}\n"
        if len(message) > 1950:
            await ctx.send(_("The answer is too long"))
            return
        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(RollDice(bot))
