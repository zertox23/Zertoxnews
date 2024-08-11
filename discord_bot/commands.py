import discord
from discord import app_commands
from discord.ext import commands
from funks import create_embed
from api import Api
from db import DbStruct, BotDb
import asyncio
import json
import io

session = BotDb().session

class Commands(commands.Cog):
    def __init__(self, bot):
        """
        Initialize the commands cog.

        Args:
            bot (commands.Bot): The Discord bot instance.
        """
        self.bot: discord.ext.commands.Bot = bot
    @app_commands.command(name="add_all_sources")
    @app_commands.describe(
        cat="the category you want the bot to send news in")
    async def add_all_sources(self, interaction: discord.Interaction, cat: discord.CategoryChannel):
        try:
            await interaction.response.defer()
            guild = self.bot.get_guild(interaction.guild_id)
            existing_channel_ids = [channel.id for channel in cat.text_channels]
            channels = session.query(DbStruct.channels).all()
            channel_sources = session.query(DbStruct.sources).all()
            for source in channel_sources:
                if len(channels) < 1:
                    channel = await guild.create_text_channel(name=source.source, category=cat, nsfw=True,news=True)
                    obj = DbStruct.channels(source=source, channel_id=channel.id)
                    session.add(obj)
                    session.commit()
                else:
                    for channel in channels:
                        try:
                            if len(existing_channel_ids) < 1:
                                    
                                    channel = await guild.create_text_channel(name=channel.source, category=cat, nsfw=True,news=True)
                                    print(channel.id)
                                    print(source)
                                    obj = DbStruct.channels(source=source.source, channel_id=channel.id)
                                    session.add(obj)
                                    session.commit()

                            else:    
                                for id in existing_channel_ids:
                                    if id in [c.channel_id for c in channels]:
                                        print(f"Channel with {source} already exists.")
                                    else:
                                        channel = await guild.create_text_channel(name=channel.source, category=cat, nsfw=True,news=True)
                                        print(channel.id)
                                        print(source)
                                        obj = DbStruct.channels(source=source, channel_id=channel.id)
                                        session.add(obj)
                                        session.commit()
                                
                        except Exception as e:
                            session.rollback()  # Roll back the transaction in case of an error
                            print(f"Error processing source {source}: {e}")
        except Exception as e:
            print(f"Error during operation: {e}")

        embed = await create_embed("Success", "", color=discord.Color.green())
        await interaction.followup.send(embed=embed)
    @app_commands.command(name="add_new_source")
    @app_commands.describe(
        link="The URL of the website.",
        articles_parent_element="The HTML element for articles_parent (e.g., 'div').",
        articles_parent_attr="The class attribute for articles_parent (e.g., 'class_name').",
        articles_parent_attr_value="the value of the attr (id name or class name)",
        article_obj_element="The HTML element for article_obj (e.g., 'article').",
        article_obj_attr="the attribute of the article",
        article_obj_attr_value="The class attribute for article_obj (e.g., 'item').",
        url_attr="the element that has the url",
        url_attr_value="The attribute for links (e.g., 'href').",
    )
    async def add_new_source(
        self,
        interaction: discord.Interaction,
        link: str,
        articles_parent_element: str = None,
        articles_parent_attr: str = None,
        articles_parent_attr_value: str = None,
        article_obj_element: str = None,
        article_obj_attr: str = None,
        article_obj_attr_value: str = None,
        url_attr: str = None,
        url_attr_value: str = None):
        
        try:
            await interaction.response.defer()

            # Construct the JSON data
            data = {
                link: {
                    "articles_parent": {
                        "element": articles_parent_element or "",
                        "attrs": {
                            articles_parent_attr: articles_parent_attr_value or ""
                        }
                    },
                    "article_obj": {
                        "element": article_obj_element or "",
                        "attrs": {
                            article_obj_attr: article_obj_attr_value or ""
                        }
                    },
                    "href": {
                        url_attr: url_attr_value or ""
                    }
                }
            }

            api = Api()
            r = await api.test_web(data=data)
            if r:
                try:
                    json_data = json.dumps(r, indent=4)
                    file_like_object = io.BytesIO(json_data.encode('utf-8'))
                    file = discord.File(file_like_object, filename="response.json")
                    message = await interaction.followup.send("you have 30 seconds to decide if this response is correct or no", file=file)
                    await message.add_reaction('✅')
                    await message.add_reaction('❌')

                    try:
                        # Wait for a reaction with a timeout
                        def check(reaction: discord.Reaction, user: discord.User):
                            return user != self.bot.user and reaction.message.id == message.id

                        reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)

                        # Check which reaction was added
                        if str(reaction.emoji) == '✅':
                            await interaction.followup.send(f"adding the scrape configuration")
                            r = await api.add_new_source(data=data)
                            json_data = json.dumps(r, indent=4)
                            file_like_object = io.BytesIO(json_data.encode('utf-8'))
                            file = discord.File(file_like_object, filename="response.json")
                            await interaction.followup.send("server response", file=file)
                        elif str(reaction.emoji) == '❌':
                            pass
                    except asyncio.TimeoutError:
                        await interaction.followup.send("No reaction received within the timeout period. Skipping.")
                except Exception as e:
                    print(f"Error during reaction handling: {e}")
            else:
                await interaction.followup.send("Response not correct.")
        except Exception as e:
            print(f"Error in add_new_source: {e}")

    @app_commands.command(name="check_for_new_sources")
    async def check_for_sources(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            api = Api()

            sources = await api.sources()
            if sources:
                try:
                    db_sources = [x.source for x in session.query(DbStruct.sources).all()]
                    for source in sources:
                        try:
                            if source not in db_sources:
                                obj = DbStruct.sources(source=source)
                                session.add(obj)
                                session.commit()
                        except Exception as e:
                            session.rollback()
                            print(f"Error adding source {source}: {e}")
                except Exception as e:
                    print(f"Error querying sources: {e}")

            embed = await create_embed("Success", "", color=discord.Color.green())
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"Error in check_for_sources: {e}")

async def setup(bot):
    try:
        await bot.add_cog(Commands(bot=bot))
    except Exception as e:
        print(f"Error in setup: {e}")
