from dotenv import load_dotenv
import os
import discord
from loguru import logger
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
import sys

from db import DbStruct, BotDb

session = BotDb().session

logger.add("logs_.log")

bot = commands.Bot(command_prefix="shabab", intents=discord.Intents.all())
load_dotenv()
my_ip = os.environ.get("my_ip").strip()
TOKEN = os.environ.get("TOKEN")
print(TOKEN)
print(type(TOKEN))

@bot.event
async def on_ready():
    guilds = bot.guilds
    print(guilds)
    '''
    for guild in guilds.values():
        guild = bot.get_guild(guild)
        if len(sys.argv) > 1 and sys.argv[1] == "check":
            channel_names = session.query(DbStruct.sources).all()

            for cat in guild.categories:
                channels = [channel.name for channel in cat.text_channels]
                for channel_source in channel_names:
                    print(channel_source.source)
                    if channel_source.source not in channels:
                        obj = DbStruct.channels(source=channel_source.source, channel_id=channel.id)            
                        session.add(obj)
                        session.commit()
    ''' 
    print("Bot is up and ready!")
    
    await bot.load_extension("background_tasks")
    await bot.load_extension("commands")

    try:
        if not os.path.isdir("/imgs"):
            try:
                os.mkdir("/imgs")
            except:
                logger.error("/imgs Not found and unable to create it")

        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command[s]")
    except Exception as e:
        logger.error(str(e))
    

bot.run(token=TOKEN)  