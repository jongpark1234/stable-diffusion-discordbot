import discord
from discord.ext import commands

from config import *

class DavidChoi(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='.',
            intents=discord.Intents.all(),
            sync_command=True,
            application_id=APPID
        )

        self.inital_extension = [
            'Cogs.ping',
            'Cogs.memory',
            'Cogs.get-options',
            'Cogs.set_model',
            'Cogs.lora',
            'Cogs.txt2img',
            # 'Cogs.img2img',
            'Cogs.test'
        ]
        
    async def setup_hook(self):
        for extension in self.inital_extension:
            await self.load_extension(extension)
        await bot.tree.sync()

    async def on_ready(self):
        print('Logged In.')
        print(f'bot name : {self.user.name}')
        print(f'bot id : {self.user.id}')
        print('---------------')
        activity = discord.Game('그림 그리기')
        await self.change_presence(status=discord.Status.online, activity=activity)

bot = DavidChoi()
bot.run(token=TOKEN)