import os
import json
import discord
from client import Protocol
import character_data


class DeleteConfirm(discord.ui.View):
    def __init__(self, bot:Protocol, campaign: str) -> None:
        super().__init__(timeout= 15)
        self.bot = bot
        self.campaign = campaign
        self.titles = ["ДА", "НЕТ"]
        self.add_buttons()

    async def page_yes(self, interaction: discord.Interaction):
        path = f'{self.bot.data_folder}Campaigns/{interaction.guild.id}.json'
        camp = await self.get_file(path)
        camp.remove_campain(self.campaign)
        self.save_update(path, camp)
        await interaction.response.edit_message(
            content="## Campaign Deleted", view= None)
        
    async def page_no(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="Deletion cancelled", view= None)

    def add_buttons(self):     
        colors = [
            discord.ButtonStyle.red, 
            discord.ButtonStyle.green 
        ]
        methods = [
            self.page_yes, 
            self.page_no 
        ]
        for i in range(len(methods)):
            button = discord.ui.Button(label= self.titles[i], style= colors[i])
            button.callback = methods[i]
            self.add_item(button)

    async def get_file(self, path) -> character_data.DnDServer:
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
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as file:
            file.write(data.toJSON())