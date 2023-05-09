import discord
from discord.ext import commands
from discord.ui import Button, View, Select
from discord import ButtonStyle
import json
import requests
import math
from config import *

is_selected = {}
class ButtonView(discord.ui.View):
    def __init__(self):
        super().__init__()

class set_model(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="set-model")
    async def set_model(self, interaction: discord.Interaction):
        '''Change Model.'''
        global curPage, is_selected
        is_selected[interaction.user.id] = False
        modelList = json.loads(requests.get(url=f'{APIURL}/sdapi/v1/sd-models').text)
        modelCount = len(modelList)
        pageLimit = math.ceil(modelCount / 25)
        curPage = 1
        
        def generateSelector():
            return [
                discord.SelectOption(
                    label=f'{modelList[i]["model_name"]}',
                    description=f'{modelList[i]["hash"]}'
                ) for i in range((curPage - 1) * 25, min(curPage * 25, modelCount)) # available maxValue is modelCount.
            ]


        # UI 선언 및 콜백 함수
        selects = Select(options=generateSelector())
        left = Button(label='<<', style=ButtonStyle.primary)
        right = Button(label='>>', style=ButtonStyle.primary)
        page = Button(label = f'{curPage}/{pageLimit}', style=ButtonStyle.grey, disabled=True)
        approve = Button(label='✅', style=ButtonStyle.green)
        cancel = Button(label='X', style=ButtonStyle.red)
        
        async def select_callback(interaction : discord.Interaction):
            global is_selected
            is_selected[interaction.user.id] = ''.join(selects.values)
            embed=discord.Embed(title=f"{is_selected[interaction.user.id]}", color=0x4fff4a)
            embed.set_author(name=f'{is_selected[interaction.user.id]} 모델로 바꿀까요?')
            embed.set_footer(text='@DavidChoi#6516')
            try:
                res = discord.File(f"{MODELPATH}\\{is_selected[interaction.user.id]}.png", filename=f"{is_selected[interaction.user.id]}.png")
                embed.set_image(url=f"attachment://{is_selected[interaction.user.id]}.png")
                await interaction.response.edit_message(view=view_make(), embed=embed, attachments=[res])
            except:
                await interaction.response.edit_message(view=view_make(), embed=embed)

        async def left_callback(interaction: discord.Interaction):
            global curPage
            curPage = max(curPage - 1, 1)
            await interaction.response.edit_message(view=view_make())

        async def right_callback(interaction: discord.Interaction):
            global curPage
            curPage = min(curPage + 1, pageLimit)
            await interaction.response.edit_message(view=view_make())

        async def page_callback(interaction: discord.Interaction):
            global is_selected
            is_selected[interaction.user.id] = False
            await interaction.response.edit_message(content='Todo: 페이지 한번에 이동하기', view=view_make())

        async def approve_callback(interaction: discord.Interaction):
            embed=discord.Embed(title=f'**{is_selected[interaction.user.id]}** 모델로 설정합니다.', color=0x777777)
            embed.set_footer(text='@DavidChoi#6516')
            await interaction.response.edit_message(embed=embed,view=View(),attachments=[])

            json_data = json.load(open(JSONPATH, 'r'))
            user_cnt = len(json_data['users'])

            for i in range(user_cnt):
                if interaction.user.id == json_data['users'][i]['userid']:
                    json_data['users'][i]['model'] = is_selected[interaction.user.id]
                    break
            else:
                json_data['users'].append({
                    'userid': interaction.user.id,
                    'model': is_selected[interaction.user.id]
                })
            
            with open(JSONPATH, 'w') as outfile:
                json.dump(json_data, outfile, indent=4)
            embed.title = f"**{is_selected[interaction.user.id]}** 모델로 설정했어요!"
            is_selected.pop(interaction.user.id)
            await interaction.edit_original_response(embed=embed)

        async def cancel_callback(interaction : discord.Interaction):
            embed=discord.Embed(title=f"모델 변경을 취소했어요.", color=0xca474c)
            embed.set_footer(text='@DavidChoi#6516')
            await interaction.response.edit_message(view=View() , embed=embed ,attachments=[])

        selects.callback = select_callback
        left.callback = left_callback
        right.callback = right_callback
        page.callback = page_callback
        approve.callback = approve_callback
        cancel.callback = cancel_callback

        def view_make():
            view = View()

            left.disabled = curPage == 1
            right.disabled = curPage == pageLimit
            approve.disabled = is_selected[interaction.user.id] == False
            page.label = f'{curPage} / {pageLimit}'

            selects.options = generateSelector()

            for ui in [selects, left, page, right, approve, cancel]:
                view.add_item(ui)
                
            return view

        embed=discord.Embed(title=f"아래 선택 메뉴에서 모델을 골라 주세요", color=0x777777)
        embed.set_footer(text='@DavidChoi#6516')
        await interaction.response.send_message(embed=embed, view=view_make())


async def setup(bot: commands.Bot):
    await bot.add_cog(
        set_model(bot),
        guilds=GUILDLIST
    )
