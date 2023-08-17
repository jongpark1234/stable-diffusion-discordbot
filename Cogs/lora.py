import discord
from discord.ext import commands
from discord.ui import Select, Button, View
import math
import os

from config import *
from Functions.edit_message import edit_message
from Functions.send_message import send_message

class lora(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.curPage = 1

    def generateSelector(self, fileList: list[str], fileSize: int) -> list[discord.SelectOption]:
        return [
            discord.SelectOption(
                label=file
            ) for file in fileList
        ][(self.curPage - 1) * 25:min(self.curPage * 25, fileSize)]

    @discord.app_commands.command(name='lora')
    async def lora(self, interaction: discord.Interaction):
        '''Showing lora list.'''
        loraList = [i for i in os.listdir(LORAPATH) if i.endswith('.safetensors')] # All lora list ( .safetensors )
        loraCount = len(loraList) # Length of lora
        pageLimit = math.ceil(loraCount / 25) # Limit of page

        selects = Select(options=self.generateSelector(loraList, loraCount)) # Main view
        left = Button(label='<<', style=discord.ButtonStyle.primary) # Page left button
        right = Button(label='>>', style=discord.ButtonStyle.primary) # Page right button
        page = Button(label=f'{self.curPage}/{pageLimit}', style=discord.ButtonStyle.grey, disabled=True) # Showing page button

        async def select_callback(interaction: discord.Interaction):
            selected = ''.join(selects.values) # Currently selected option
            loraName = selected.split('.')[0] # Selected lora's name
            loraCoverPath = f'{LORAPATH}\\{loraName}.png' # Cover path of selected lora
            loraTriggerWordPath = f'{LORAPATH}\\{loraName}.txt' # Trigger-word path of selected lora

            embed = discord.Embed(title=f'Lora', description=f'{loraName}', color=0x4fff4a) # Create embed
            embed.add_field(name='Lora Prompt', value=f'<lora:{loraName}:1>', inline=False) # Lora prompt information
            embed.set_footer(text='@DavidChoi#6516') # Bot information

            if os.path.exists(loraTriggerWordPath): # If there's lora trigger-word text file
                embed.add_field(name='Trigger Words', value=', '.join(map(lambda x: x.strip(), open(loraTriggerWordPath, 'r'))), inline=False) # Lora trigger-word information

            if os.path.exists(loraCoverPath): # If there's Lora cover
                attach = discord.File(fp=loraCoverPath, filename=f'{loraName}.png')
                embed.set_image(url=f'attachment://{loraName}.png')
                await edit_message(
                    interaction=interaction,
                    view=view_make(),
                    embed=embed,
                    attachments=[attach]
                )
            else: # If there's not Lora Cover
                await edit_message(
                    interaction=interaction,
                    view=view_make(),
                    embed=embed
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
            await edit_message(
                interaction=interaction,
                view=view_make()
            )
        
        selects.callback = select_callback
        left.callback = left_callback
        page.callback = page_callback
        right.callback = right_callback

        def view_make() -> View:
            view = View()

            left.disabled = self.curPage == 1
            right.disabled = self.curPage == pageLimit
            page.label = f'{self.curPage} / {pageLimit}'

            selects.options = self.generateSelector(loraList, loraCount)

            for ui in [selects, left, page, right]:
                view.add_item(ui)

            return view

        embed=discord.Embed(title='Lora List', color=0x777777)
        embed.set_footer(text='@DavidChoi#6516')
        if not await send_message(
            interaction=interaction,
            embed=embed,
            view=view_make()
        ):
            return

async def setup(bot: commands.Bot):
    await bot.add_cog(
        lora(bot),
    )