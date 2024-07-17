from dotenv import load_dotenv
import os
import discord
from loguru import logger
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks


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
    print("Bot is up and ready!")
    
    await bot.load_extension("background_tasks")
    await bot.load_extension("commands")

    try:
        if not os.path.isdir("/imgs"):
            try:
                os.mkdir("/imgs")
            except:
                logger.error("/imgs Not found and unable to create it")
                exit()
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command[s]")
    except Exception as e:
        logger.error(str(e))
    

bot.run(token=TOKEN)  