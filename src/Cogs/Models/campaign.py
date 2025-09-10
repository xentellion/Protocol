import discord
from src.data_control import JsonDataControl
from src.client import Protocol
from src.character_data import Campaign, DnDServer, Characteristic


class CreateCampaign(discord.ui.Modal):
    def __init__(self, bot: Protocol, locale: str, camp: DnDServer):
        self.camp = camp
        self.bot = bot
        _ = self.bot.locale(locale)
        super().__init__(title=_("Start new campaign!"))
        self.c_name = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label=_("Write campaign name"),
            placeholder=_("Title"),
            required=True,
        )
        self.add_item(self.c_name)

    async def on_submit(self, interaction: discord.Interaction):
        _ = self.bot.locale(interaction.locale)
        if self.c_name.value in self.camp.campaigns:
            self.c_name.label = _("{0} already exists").format(self.c_name)
        else:
            self.name = self.c_name.value
            self.camp.campaigns[self.name] = Campaign()
            await interaction.response.send_message(
                _("Do you want to create one more characteristic for this campaign?"),
                view=ContinueButton(self.bot, interaction.locale, self.camp, self.name),
                ephemeral=True
            )


class ContinueButton(discord.ui.View):
    def __init__(self, bot: Protocol, locale: str, camp: DnDServer, name: str):
        super().__init__(timeout=120)
        self.bot = bot
        self.camp = camp
        self.name = name
        _ = self.bot.locale(locale)
        self.titles = [_("YES"), _("NO")]
        self.add_buttons()

    async def page_yes(self, interaction: discord.Interaction):
        await interaction.response.send_modal(NewStat(self.bot, interaction.locale, self.camp, self.name))

    async def page_no(self, interaction: discord.Interaction):
        self.camp.current_c = self.name
        id = interaction.message.id
        path = "{0}Campaigns/{1}.json".format(self.bot.data_folder, "{0}")
        JsonDataControl.save_update(path.format(interaction.guild.id), self.camp)
        await interaction.response.defer()
        _ = self.bot.locale(interaction.locale)
        await interaction.followup.send(
            _("## Campaign {0} has been created!").format(self.name)
        )
        await interaction.followup.edit_message(
            message_id=id,
            content=f"**{_('Stats in campaign')}:**\n\n{chr(10).join(self.camp.campaigns[self.name].stats.keys())}",
            view=None)

    def add_buttons(self):
        colors = [discord.ButtonStyle.green, discord.ButtonStyle.red]
        methods = [self.page_yes, self.page_no]
        for i in range(len(methods)):
            button = discord.ui.Button(label=self.titles[i], style=colors[i])
            button.callback = methods[i]
            self.add_item(button)


class NewStat(discord.ui.Modal):
    def __init__(self, bot: Protocol, locale: str, camp: DnDServer, name: str):
        self.bot = bot
        self.name = name
        self.camp = camp
        _ = self.bot.locale(locale)
        super().__init__(title=_("New characteristic"))
        self.new_stat = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label=_("Stat"),
            placeholder=_("Stat name"),
            required=True,
        )
        self.has_max = discord.ui.TextInput(
            style=discord.TextStyle.short,
            placeholder=_("No"),
            label=_("Is limited by max value?"),
            required=False,
        )
        self.add_item(self.new_stat)
        self.add_item(self.has_max)

    async def on_submit(self, interaction: discord.Interaction):
        stat = Characteristic()
        if self.has_max.value:
            stat.has_max = True
        self.camp.campaigns[self.name].stats[self.new_stat.value] = stat
        await interaction.response.defer()


class DeleteConfirm(discord.ui.View):
    def __init__(self, bot: Protocol, locale: str, campaign: str) -> None:
        super().__init__(timeout=15)
        self.bot = bot
        self.deleted_campaign = campaign
        _ = self.bot.locale(locale)
        self.titles = [_("YES"), _("NO")]
        self.add_buttons()

    async def page_yes(self, interaction: discord.Interaction):
        path = f"{self.bot.data_folder}Campaigns/{interaction.guild.id}.json"
        camp = await JsonDataControl.get_file(path)
        camp.campaigns.pop(self.deleted_campaign)
        JsonDataControl.save_update(path, camp)
        _ = self.bot.locale(interaction.locale)
        await interaction.response.edit_message(
            content=_("## Campaign Deleted"), view=None
        )

    async def page_no(self, interaction: discord.Interaction):
        _ = self.bot.locale(interaction.locale)
        await interaction.response.edit_message(content=_("Cancelled"), view=None)

    def add_buttons(self):
        colors = [discord.ButtonStyle.red, discord.ButtonStyle.green]
        methods = [self.page_yes, self.page_no]
        for i in range(len(methods)):
            button = discord.ui.Button(label=self.titles[i], style=colors[i])
            button.callback = methods[i]
            self.add_item(button)

