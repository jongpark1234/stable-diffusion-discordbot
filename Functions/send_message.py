import asyncio
from typing import Optional, Sequence, Any
from discord import Interaction, Embed, File, AllowedMentions
from discord.utils import MISSING
from discord.ui import View
from discord.errors import NotFound

async def send_message(
    *,
    interaction: Interaction,
    content: Optional[Any] = None,
    embed: Embed = MISSING,
    embeds: Sequence[Embed] = MISSING,
    file: File = MISSING,
    files: Sequence[File] = MISSING,
    view: View = MISSING,
    tts: bool = False,
    ephemeral: bool = False,
    allowed_mentions: AllowedMentions = MISSING,
    suppress_embeds: bool = False,
    silent: bool = False,
    delete_after: Optional[float] = None,
) -> bool:
    while True:
        try:
            await interaction.response.send_message(
                content=content,
                embed=embed,
                embeds=embeds,
                file=file,
                files=files,
                view=view,
                tts=tts,
                ephemeral=ephemeral,
                allowed_mentions=allowed_mentions,
                suppress_embeds=suppress_embeds,
                silent=silent,
                delete_after=delete_after
            )
            break
        except NotFound as err:
            print(err, '(send message)')
            print('Command Session Exit')
            return False
        except Exception as err:
            print(err, '(send message)')
        await asyncio.sleep(0.5)
    return True

