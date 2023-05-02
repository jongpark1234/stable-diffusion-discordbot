import discord
from discord.ext import commands
from discord.ui import Select, Button, View

from config import *

globalVariable = 0

class test(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.classVariable = 0

    @discord.app_commands.command(name='test')
    async def lora(self, interaction: discord.Interaction):
        global globalVariable
        globalVariable += 1
        self.classVariable += 1
        await interaction.response.send_message(
            f'{globalVariable=}'
            f'{self.classVariable=}'
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(
        test(bot),
        guilds=GUILDLIST
    )