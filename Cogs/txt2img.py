import discord
from discord.ext import commands
from collections import deque
from PIL import Image, PngImagePlugin
import json
import requests
import io
import base64
import asyncio

from config import *

getimg_result = False
is_drawing = False
queue = deque()

class txt2img(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name='txt2img')
    async def txt2img(
        self,
        interaction: discord.Interaction,
        prompt: str,
        negative_prompt: str='EasyNegative, extra fingers, fewer fingers',
        width: discord.app_commands.Range[int, 64, 1024]=512,
        height: discord.app_commands.Range[int, 64, 1024]=768,
        steps: discord.app_commands.Range[int, 1, 50]=40,
        seed: int=-1,
        hires_toggle: bool=True
    ):
        '''텍스트를 그림으로 만들어 줍니다.

        Args
        ----------
        prompt: str
            AI에게 그려야 할 것을 알려주는 문자열 입니다.
        negative_prompt: str
            AI에게 하지 말아야 할 것을 알려주는 문자열 입니다. 기본값 - EasyNegative, extra fingers, fewer fingers
        width: int
            이미지의 너비 입니다. (width는 64에서 1024 사이의 정수여야 합니다.) 기본값 - 384
        height: int
            이미지의 높이 입니다. (height는 64에서 1024 사이의 정수여야 합니다.) 기본값 - 512
        steps: int
            AI가 반복해서 그림을 그릴 횟수입니다. ( 기본값: 40 )
        seed : bool
            이미지 생성의 시드값을 정합니다. ( 기본값: -1 ( random ) )
        hires_toggle : bool
            hires_fix의 on/off 여부를 정합니다. ( 기본값: True )
        '''
        global is_drawing
        queued = False
        if is_drawing:
            await interaction.response.send_message(f"In Queue...")
            queue.append(interaction.id)
            queued = interaction.id
            while True:
                if not is_drawing and queue[0] == interaction.id:
                    queue.popleft()
                    break
                await interaction.edit_original_response(content = f"In Queue... **[ Waiting Order : {queue.index(interaction.id) + 1} ]**")
                await asyncio.sleep(1)
        is_drawing = True
    
        payload = {
            'enable_hr': hires_toggle,
            'denoising_strength': 0.4,
            'hr_scale': 2,
            'hr_second_pass_steps': 20,
            'firstphase_width': 0,
            'firstphase_height': 0,
            'hr_upscaler': "4x-AnimeSharp",
            'prompt': prompt,
            'negative_prompt': negative_prompt,
            'sampler_index': "DPM++ 2M Karras",
            'sampler_name': "DPM++ 2M Karras",
            'steps': steps,
            'width': width,
            'height': height,
            'cfg_scale': 7,
            'seed': seed,
        }
        json_data = {}
        with open(JSONPATH, 'r') as json_file:
            json_data = json.load(json_file)

        override_settings = {}
        for user in json_data['users']:
            if interaction.user.id == user['userid']:
                override_settings['sd_model_checkpoint'] = user['model']
                override_payload = { 'override_settings': override_settings }
                payload.update(override_payload)
                break
                
        if queued == interaction.id:
            await interaction.edit_original_response(content = "그림 그리는 중..")
        else:
            await interaction.response.send_message("그림 그리는 중..")

        async def getimg():
            global response, getimg_result
            await asyncio.sleep(1)
            response = await asyncio.to_thread(requests.post, url=f'{APIURL}/sdapi/v1/txt2img', json=payload)
            getimg_result = True
            return

        async def loop():
            while not getimg_result: # Persistent until all images are received
                progress = json.loads(requests.get(url=f'{APIURL}/sdapi/v1/progress').text)
                percent = round(progress['progress'] * 100) # Progress Percent
                eta = max(progress['eta_relative'], 0) # Remaining time ( Guess )

                if percent == 100:
                    await interaction.edit_original_response(content=f"그림 가져오는 중..")
                else:
                    await interaction.edit_original_response(content=f'`[{"#" * (percent // 5)}{"." * (20 - percent // 5)}]` **[ {percent}% | 예상 시간 : {eta:.1f}초 ]**')

                await asyncio.sleep(0.1)

            await interaction.edit_original_response(content='그림 완성!')
            return

        async def process():
            global getimg_result
            getimg_result = False
            getImage = asyncio.create_task(getimg())
            displayRemainTime = asyncio.create_task(loop())
            await getImage
            await displayRemainTime
            return
        
        await process()
        

        for i in response.json()['images']:
            image = Image.open(io.BytesIO(base64.b64decode(i.split(',', 1)[0])))

            png_payload = {
                'image': f'data:image/png;base64,{i}'
            }

            response2 = requests.post(url=f'{APIURL}/sdapi/v1/png-info', json=png_payload)

            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", response2.json().get('info'))
            image.save('output.png', pnginfo=pnginfo)
    
        res = discord.File(OUTPUTPATH, filename='output.png')
        embed=discord.Embed(title=f"@{interaction.user.name}", color=0x4fff4a)
        embed.set_author(name="✅ 텍스트 -> 이미지")
        embed.set_image(url="attachment://output.png")
        embed.add_field(name="Positive Prompt", value=prompt, inline=False)
        embed.add_field(name="Negative Prompt", value=negative_prompt, inline=False)
        embed.set_footer(text="@DavidChoi#6516")
        await interaction.edit_original_response(embed=embed,attachments=[res])
        is_drawing = False

async def setup(bot: commands.Bot):
    await bot.add_cog(
        txt2img(bot),
        guilds=GUILDLIST
    )
