import discord
from discord.ext import commands

from config import *

class test(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name='test')
    async def lora(self, interaction: discord.Interaction):
        interaction.response.send_message('test')

async def setup(bot: commands.Bot):
    await bot.add_cog(
        test(bot),
        guilds=GUILDLIST
    )