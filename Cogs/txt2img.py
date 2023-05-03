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

class txt2img(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.imgSuccess = False
        self.isDrawing = False
        self.queue = deque()
        self.imgResult: requests.Response = None
    
    @discord.app_commands.command(name='txt2img')
    async def txt2img(
        self,
        interaction: discord.Interaction,
        prompt: str,
        negative_prompt: str='EasyNegative, extra fingers, fewer fingers, NSFW',
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
        
        async def loadModel():
            for user in json.load(open(JSONPATH, 'r'))['users']:
                if interaction.user.id == user['userid']:
                    payload.update({
                        'override_settings': {
                            'sd_model_checkpoint': user['model']
                        }
                    })
                    return True
            return False
     
        async def waiting():
            if self.isDrawing: # If drawing something else
                await interaction.response.send_message('In Queue...')
                self.queue.append(interaction.id)
                while True:
                    if not self.isDrawing and self.queue[0] == interaction.id: # If no other picture is drawn and I'm at the top of the queue
                        self.queue.popleft() # Exporting oneself from the queue
                        break # Stop waiting
                    await interaction.edit_original_response(content=f'In Queue... [ Waiting Order : {self.queue.index(interaction.id) + 1} ]')
                    asyncio.sleep(1)
            self.isDrawing = True # Drawing weather turn on
                
        async def process():
            async def getimg():
                '''The Function that get Image from Webui API'''
                await asyncio.sleep(1)
                self.imgResult = await asyncio.to_thread(requests.post, url=f'{APIURL}/sdapi/v1/txt2img', json=payload)
                self.imgSuccess = True
            async def progress():
                while not self.imgSuccess: # Persistent until all images are received
                    progress = json.loads(requests.get(url=f'{APIURL}/sdapi/v1/progress').text)
                    percent = round(progress['progress'] * 100) # Progress Percent
                    eta = max(progress['eta_relative'], 0) # Remaining time ( Guess )

                    await interaction.edit_original_response(content=f'`[{"#" * (percent // 5)}{"." * (20 - percent // 5)}]` **[ {percent}% | 예상 시간 : {eta:.1f}s  ]**')
                    await asyncio.sleep(0.1)

                await interaction.edit_original_response(content='그림 완성!')
            self.imgSuccess = False
            getImage = asyncio.create_task(getimg())
            displayProgress = asyncio.create_task(progress())
            await getImage
            await displayProgress
            
        async def saveImage():
            for i in self.imgResult.json()['images']:
                image = Image.open(io.BytesIO(base64.b64decode(i.split(',', 1)[0])))

                png_info = requests.post(
                    url=f'{APIURL}/sdapi/v1/png-info',
                    json={
                        'image': f'data:image/png;base64,{i}'
                    }
                ).json().get('info')

                image.save(
                    'output.png',
                    pnginfo=PngImagePlugin.PngInfo().add_text(
                        key='parameters',
                        value=png_info
                    )
                )


        if not await loadModel():
            interaction.response.send_message('/set-model please.')
            return
        await interaction.response.send_message('대기중..')               
        await waiting()
        await process()
        await saveImage()

    
        embed=discord.Embed(
            title=f"@{interaction.user.name}", color=0x4fff4a
        ).set_author(
            name='✅ 텍스트 -> 이미지'
        ).set_image(
            url='attachment://output.png'
        ).add_field(
            name='Positive Prompt', value=prompt, inline=False
        ).add_field(
            name='Negative Prompt', value=negative_prompt, inline=False
        ).set_footer(
            text='@DavidChoi#6516'
        )

        await interaction.edit_original_response(
            embed=embed,
            attachments=[
                discord.File(OUTPUTPATH, filename='output.png')
            ]
        )

        self.isDrawing = False

async def setup(bot: commands.Bot):
    await bot.add_cog(
        txt2img(bot),
        guilds=GUILDLIST
    )
