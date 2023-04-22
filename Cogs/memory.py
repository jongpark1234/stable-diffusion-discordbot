import discord
from discord.ext import commands
import json
import requests

from config import *

class memory(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name='memory')
    async def memory(self, interaction: discord.Interaction):
        '''현재 서버 컴퓨터의 RAM과 VRAM 사용량을 알려 줍니다.'''
        data = json.loads(requests.get(url=f'{APIURL}/sdapi/v1/memory').text)
        await interaction.response.send_message(
            f'''사용 가능 RAM: **{data['ram']['free'] / 1e+9:.1f}GB**
            전체 메모리 **{data['ram']['total'] / 1e+9:.1f}GB** 중 **{data['ram']['used'] / 1e+9:.1f}GB** 사용 중
            
            사용 가능 VRAM : **{data['cuda']['system']['free'] / 1e+9:.1f}GB**
            전체 메모리 **{data['cuda']['system']['total'] / 1e+9:.1f}GB** 중 **{data['cuda']['system']['used'] / 1e+9:.1f}GB** 사용 중
            '''
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(
        memory(bot),
        guilds=GUILDLIST
    )