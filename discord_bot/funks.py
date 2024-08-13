import discord
import json
import aiohttp


from db import DbStruct, BotDb


async def create_embed(title: str, content: str, color: discord.Color):
    """
    Create and return a Discord embed with the specified title, content, and color.

    Args:
        title (str): The title of the embed.
        content (str): The content of the embed.
        color (discord.Color): The color of the embed.

    Returns:
        discord.Embed: The created embed.
    """
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name=content, value="")
    return embed


async def download_attachment(attachment):
    """
    Download the provided Discord attachment.

    Args:
        attachment: The Discord attachment to download.

    Returns:
        bool: True if the download is successful, False otherwise.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.url) as resp:
            if resp.status == 200:
                data = await resp.read()
                # You can save the video to a file or process it as needed
                with open(f"{attachment.filename}", "wb") as f:
                    f.write(data)
                return True
            else:
                return False
