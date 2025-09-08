import discord
from src.data_control import JsonDataControl
from src.client import Protocol
from src.character_data import Campaign, DnDServer, Characteristic


class CreateCampaign(discord.ui.Modal):
    c_name = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Введите название кампании",
        placeholder="Title",
        required=True,
    )

    def __init__(self, bot: Protocol, camp: DnDServer):
        self.camp = camp
        self.bot = bot
        super().__init__(title="Создайте новую кампанию!")

    async def on_submit(self, interaction: discord.Interaction):
        if self.c_name.value in self.camp.campaigns:
            self.c_name.label = f"{self.c_name} уже существует"
        else:
            self.name = self.c_name.value
            self.camp.campaigns[self.name] = Campaign()
            await interaction.response.send_message(
                "Хотите ли вы создать еще одну характеристику?",
                view=ContinueButton(self.bot, self.camp, self.name),
                ephemeral=True
            )


class ContinueButton(discord.ui.View):
    def __init__(self, bot: Protocol, camp: DnDServer, name: str):
        super().__init__(timeout=120)
        self.bot = bot
        self.camp = camp
        self.name = name

    @discord.ui.button(label="ДА", style=discord.ButtonStyle.green)
    async def page_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NewStat(self.bot, self.camp, self.name))

    @discord.ui.button(label="НЕТ", style=discord.ButtonStyle.red)
    async def page_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.camp.current_c = self.name
        id = interaction.message.id
        path = "{0}Campaigns/{1}.json".format(self.bot.data_folder, "{0}")
        JsonDataControl.save_update(path.format(interaction.guild.id), self.camp)
        await interaction.response.defer()
        await interaction.followup.send(
            f"## Кампания {self.name} создана!"
        )
        await interaction.followup.edit_message(
            message_id=id,
            content=f"**Характеристики в кампании:**\n\n{chr(10).join(self.camp.campaigns[self.name].stats.keys())}",
            view=None)


class NewStat(discord.ui.Modal):
    new_stat = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Характеристика",
        placeholder="Название",
        required=True,
    )

    has_max = discord.ui.TextInput(
        style=discord.TextStyle.short,
        placeholder="Нет",
        label="Есть максимум?",
        required=False,
    )

    def __init__(self, bot: Protocol, camp: DnDServer, name: str):
        self.bot = bot
        self.name = name
        self.camp = camp
        super().__init__(title="Новая характеристика")

    async def on_submit(self, interaction: discord.Interaction):
        stat = Characteristic()
        if self.has_max.value:
            stat.has_max = True
        self.camp.campaigns[self.name].stats[self.new_stat.value] = stat
        await interaction.response.defer()


class DeleteConfirm(discord.ui.View):
    def __init__(self, bot: Protocol, campaign: str) -> None:
        super().__init__(timeout=15)
        self.bot = bot
        self.deleted_campaign = campaign
        self.titles = ["YES", "NO"]

    @discord.ui.button(label="ДА", style=discord.ButtonStyle.red)
    async def page_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        path = f"{self.bot.data_folder}Campaigns/{interaction.guild.id}.json"
        camp = await JsonDataControl.get_file(path)
        camp.campaigns.pop(self.deleted_campaign)
        JsonDataControl.save_update(path, camp)
        await interaction.response.edit_message(
            content="## Campaign Deleted", view=None
        )

    @discord.ui.button(label="НЕТ", style=discord.ButtonStyle.green)
    async def page_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Deletion cancelled", view=None)

