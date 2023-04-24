import discord
from discord.ext import commands
import requests
import json

from config import *

class get_queue(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="get-queue")
    async def get_options(self, interaction: discord.Interaction):
        '''Bring the Queue Status.'''
        await interaction.response.send_message(json.loads(requests.get(url=f'{APIURL}/queue/status').text))

async def setup(bot: commands.Bot):
    await bot.add_cog(
        get_queue(bot),
        guilds=GUILDLIST
    )