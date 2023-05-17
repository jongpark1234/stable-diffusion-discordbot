import discord
from discord.ext import commands
from discord.ui import Button, View, Select
from discord import ButtonStyle
import json
import requests
import math

from config import *
from Functions.send_message import send_message
from Functions.edit_message import edit_message
from Functions.edit_original_response import edit_original_response

is_selected = {}

class set_model(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.curPage = 1

    def generateSelector(self, fileList: list[str], fileSize: int) -> list[discord.SelectOption]:
        return [
            discord.SelectOption(
                label=file['model_name'],
                description=file['hash']
            ) for file in fileList
        ][(self.curPage - 1) * 25:min(self.curPage * 25, fileSize)]

    @discord.app_commands.command(name='set-model')
    async def set_model(self, interaction: discord.Interaction):
        '''Change Model.'''
        global is_selected
        is_selected[interaction.user.id] = False
        modelList = json.loads(requests.get(url=f'{APIURL}/sdapi/v1/sd-models').text)
        modelCount = len(modelList)
        pageLimit = math.ceil(modelCount / 25)
        
        # UI 선언 및 콜백 함수
        selects = Select(options=self.generateSelector(modelList, modelCount))
        left = Button(label='<<', style=ButtonStyle.primary)
        right = Button(label='>>', style=ButtonStyle.primary)
        page = Button(label = f'{self.curPage}/{pageLimit}', style=ButtonStyle.grey, disabled=True)
        approve = Button(label='✅', style=ButtonStyle.green)
        cancel = Button(label='X', style=ButtonStyle.red)
        
        async def select_callback(interaction : discord.Interaction):
            global is_selected
            is_selected[interaction.user.id] = ''.join(selects.values)
            embed=discord.Embed(title=f"{is_selected[interaction.user.id]}", color=0x4fff4a)
            embed.set_author(name=f'{is_selected[interaction.user.id]} 모델로 바꿀까요?')
            embed.set_footer(text='@DavidChoi#6516')
            try:
                modelCover = discord.File(f"{MODELPATH}\\{is_selected[interaction.user.id]}.png", filename=f"{is_selected[interaction.user.id]}.png")
                embed.set_image(url=f"attachment://{is_selected[interaction.user.id]}.png")
                await edit_message(
                    interaction=interaction,
                    embed=embed,
                    attachments=[modelCover],
                    view=view_make(),
                )
            except:
                await edit_message(
                    interaction=interaction,
                    embed=embed,
                    attachments=[],
                    view=view_make()
                )

        async def left_callback(interaction: discord.Interaction):
            self.curPage = max(self.curPage - 1, 1)
            await edit_message(
                interaction=interaction,
                view=view_make()
            )

        async def right_callback(interaction: discord.Interaction):
            self.curPage = min(self.curPage + 1, pageLimit)
            await edit_message(
                interaction=interaction,
                view=view_make()
            )

        async def page_callback(interaction: discord.Interaction):
            global is_selected
            is_selected[interaction.user.id] = False
            await edit_message(
                interaction=interaction,
                view=view_make()
            )

        async def approve_callback(interaction: discord.Interaction):
            embed = discord.Embed(title=f'**{is_selected[interaction.user.id]}** 모델로 설정합니다.', color=0x777777)
            embed.set_footer(text='@DavidChoi#6516')
            await edit_message(
                interaction=interaction,
                embed=embed,
                attachments=[],
                view=View()
            )

            json_data = json.load(open(JSONPATH, 'r'))
            userCount = len(json_data['users'])

            for i in range(userCount):
                if interaction.user.id == json_data['users'][i]['userid']:
                    json_data['users'][i]['model'] = is_selected[interaction.user.id]
                    break
            else:
                json_data['users'].append({
                    'userid': interaction.user.id,
                    'model': is_selected[interaction.user.id]
                })
            
            json.dump(json_data, open(JSONPATH, 'w'), indent=4)
            is_selected.pop(interaction.user.id)

        async def cancel_callback(interaction : discord.Interaction):
            embed=discord.Embed(title=f'모델 변경을 취소했어요.', color=0xca474c)
            embed.set_footer(text='@DavidChoi#6516')
            await edit_message(
                interaction=interaction,
                embed=embed,
                attachments=[],
                view=View(),
            )

        selects.callback = select_callback
        left.callback = left_callback
        right.callback = right_callback
        page.callback = page_callback
        approve.callback = approve_callback
        cancel.callback = cancel_callback

        def view_make():
            view = View()

            left.disabled = self.curPage == 1
            right.disabled = self.curPage == pageLimit
            approve.disabled = is_selected[interaction.user.id] == False
            page.label = f'{self.curPage} / {pageLimit}'

            selects.options = self.generateSelector(modelList, modelCount)

            for ui in [selects, left, page, right, approve, cancel]:
                view.add_item(ui)
                
            return view

        embed=discord.Embed(title='아래 선택 메뉴에서 모델을 골라 주세요', color=0x777777)
        embed.set_footer(text='@DavidChoi#6516')
        await send_message(
            interaction=interaction,
            embed=embed,
            view=view_make()
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(
        set_model(bot),
        guilds=GUILDLIST
    )
