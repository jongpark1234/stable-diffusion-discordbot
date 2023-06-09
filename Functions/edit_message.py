from typing import Optional, Sequence, Union, Any
from discord import Interaction, Embed, Attachment, File, AllowedMentions
from discord.utils import MISSING
from discord.ui import View

async def edit_message(
    *,
    interaction: Interaction,
    content: Optional[Any] = MISSING,
    embed: Optional[Embed] = MISSING,
    embeds: Sequence[Embed] = MISSING,
    attachments: Sequence[Union[Attachment, File]] = MISSING,
    view: Optional[View] = MISSING,
    allowed_mentions: Optional[AllowedMentions] = MISSING,
    delete_after: Optional[float] = None,
) -> None:
    while True:
        try:
            await interaction.response.edit_message(
                content=content,
                embeds=embeds,
                embed=embed,
                attachments=attachments,
                view=view,
                allowed_mentions=allowed_mentions,
                delete_after=delete_after
            )
            break
        except Exception as err:
            print(err, '(edit message)')
            continue
