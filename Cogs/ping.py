import discord
from discord.ext import commands
from config import *

class ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name='ping')
    async def ping(self, interaction: discord.Interaction):
        '''pong!'''
        await interaction.response.send_message('pong!')


async def setup(bot: commands.Bot):
    await bot.add_cog(
        ping(bot),
        guilds=GUILDLIST
    )