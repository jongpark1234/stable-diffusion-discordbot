from typing import Optional, Sequence, Union, Any
from discord import Interaction, Embed, Attachment, File, AllowedMentions
from discord.utils import MISSING
from discord.ui import View

async def edit_original_response(
    *,
    interaction: Interaction,
    content: Optional[Any] = MISSING,
    embeds: Sequence[Embed] = MISSING,
    embed: Optional[Embed] = MISSING,
    attachments: Sequence[Union[Attachment, File]] = MISSING,
    view: Optional[View] = MISSING,
    allowed_mentions: Optional[AllowedMentions] = MISSING,
) -> None:
    while True:
        try:
            await interaction.edit_original_response(
                content=content,
                embeds=embeds,
                embed=embed,
                attachments=attachments,
                view=view,
                allowed_mentions=allowed_mentions,
            )
            break
        except Exception as err:
            print(err, '(edit original response)')
            continue
