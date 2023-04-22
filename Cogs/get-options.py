import discord
from discord.ext import commands
import json

from config import *

class get_options(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.app_commands.command(name="get-options")
    async def get_options(self, interaction: discord.Interaction):
        '''현재 설정되있는 모델과 vae를 알려 줍니다.'''
        json_data = {}
        with open(JSONPATH, 'r') as json_file:
            json_data = json.load(json_file)
        user_cnt = len(json_data['users'])

        for i in range(user_cnt):
            if interaction.user.id == json_data['users'][i]['userid']:
                await interaction.response.send_message(f"<@{interaction.user.id}> 님의 설정값\n\nModel_Checkpoint : **{json_data['users'][i]['model']}**\nVAE : **kl-f8-anime2.ckpt**")
                break
        else:
            await interaction.response.send_message(f"<@{interaction.user.id}>님은 아직 모델 설정을 하지 않으신것 같아요!\n **/set-model** 으로 설정해주세요.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        get_options(bot),
        guilds=GUILDLIST
    )