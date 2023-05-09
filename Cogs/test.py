import discord
from discord.ext import commands
import json
import requests

from config import *

class test(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name='test')
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message(json.loads(requests.get(url=f'{APIURL}/sdapi/v1/sd-vaes').text))

async def setup(bot: commands.Bot):
    await bot.add_cog(
        test(bot),
        guilds=GUILDLIST
    )