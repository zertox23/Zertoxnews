import discord
from discord import app_commands
from discord.ext import commands
import discord.ext
import discord.ext.commands
from funks import create_embed
from api import Api
from db import DbStruct, BotDb


session = BotDb().session


class Commands(commands.Cog):

    def __init__(self, bot):
        """
        Initialize the commands cog.

        Args:
            bot (commands.Bot): The Discord bot instance.
        """
        self.bot:discord.ext.commands.Bot = bot


    @app_commands.command(name="add_all_sources")
    @app_commands.describe(
        cat="the category you want the bot to send news in")
    async def add_all_sources(self, interaction: discord.Interaction, cat: discord.CategoryChannel):
        await interaction.response.defer()
        guild = self.bot.get_guild(interaction.guild_id)
        channels = [channel.name for channel in cat.text_channels]
        channel_names = session.query(DbStruct.sources).all()
        for channel_source in channel_names:
            print(channel_source.source)
            if channel_source.source not in channels:
                channel = await guild.create_text_channel(name=channel_source.source, category=cat, nsfw=True)
                print(channel.id)
                print(channel_source.source)
                obj = DbStruct.channels(source=channel_source.source, channel_id=channel.id)            
                session.add(obj)
                session.commit()

        embed = await create_embed("Success","",color=discord.Color.green())            
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="check_for_new_sources")
    async def check_for_sources(self,interaction:discord.Interaction):
        await interaction.response.defer()
        api = Api()

        sources = await api.sources()
        if sources:
            db_sources = [x.source for x in session.query(DbStruct.sources).all()]
            for source in sources: 
                if source not in db_sources:
                    obj = DbStruct.sources(source=source)
                    session.add(obj)
                    session.commit()
        embed = await create_embed("Success","",color=discord.Color.green())            
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Commands(bot=bot))