import io
import os

from dotenv import load_dotenv
from loguru import logger
import uuid
import aiohttp
import asyncio
# Models
from models import DownFile,DownMedia
from db import BotDb, DbStruct

import discord
from discord.ext import commands, tasks

from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy
import textwrap
import mdformat
import glob
from api import Api


logger.add("logs_.log")

load_dotenv()
proxy = str(os.environ.get("proxy"))
DEBUG = True

# Erorrs
IP_DIDNT_CHANGE = "IP didn't change, sorry try later" 
ERROR_IN_IMAGE_DOWNLOAD = "Error occurred in image download"
ERROR_IN_VIDEO_DOWNLOAD = "Error occurred in video download"
ERROR_IN_DOWNLOAD_THROUGH_TOR = "Error in download_img_through_tor"

timer = int(os.environ.get("time_between_checks"))
if timer < 3:
    timer = 3
lines2  = "\n\n"
logger.info(f"DEBUG MODE -> "+str(DEBUG)+lines2+ "Proxy -> "+str(proxy)+lines2+"Timer -> "+str(timer))




def split_text_by_character_limit(text, char_limit):
    try:
        paragraphs = text.splitlines()
        segments = []
        current_segment = ''

        for paragraph in paragraphs:
            try:
                wrapped = textwrap.fill(paragraph, width=char_limit, replace_whitespace=False)
                lines = wrapped.split('\n')

                for line in lines:
                    try:
                        if len(current_segment) + len(line) > char_limit:
                            segments.append(current_segment.rstrip())
                            current_segment = ''
                        current_segment += line + '\n'
                    except Exception as e:
                        logger.error(f"Error in processing line in split_text_by_character_limit: {e}")
                        if DEBUG:
                            raise

            except Exception as e:
                logger.error(f"Error in processing paragraph in split_text_by_character_limit: {e}")
                if DEBUG:
                    raise

        if current_segment:
            try:
                current_segment = current_segment.rstrip()
                current_segment2 = mdformat.text(current_segment, extensions=["gfm"])
                if len(current_segment2) >= 1999:
                    segments.extend(split_text_by_character_limit(current_segment, char_limit=1500))
                else:
                    segments.append(current_segment2)
            except Exception as e:
                logger.error(f"Error in final segment processing in split_text_by_character_limit: {e}")
                if DEBUG:
                    raise

        return segments
    except Exception as e:
        logger.error(f"Error in split_text_by_character_limit: {e}")
        if DEBUG:
            raise
        return []



async def download_img_through_tor(url: str) -> DownFile | str: 
    my_ip = os.environ.get("my_ip").strip()
    is_video = True if ".mp4" in url else False # if true then video else image
    headers  = {'User-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/604.'} # to hide the fact that this is a bot 
    try:
        tor_proxy = proxy  # Assuming Tor proxy is running locally
        async with aiohttp.ClientSession() as session:
            async with session.get('http://icanhazip.com/', ssl=False) as response:

                current_ip = await response.text()
                if current_ip.strip() != my_ip:
                    logger.error(f"Failed Proxy -> YourIp {str(my_ip)} == proxyip | {str(current_ip.strip())}")
                    return IP_DIDNT_CHANGE

            if not is_video: # image
                try:
                    async with session.get(url=url,headers=headers,ssl=False) as r:
                        if r.status == 200: # if went successfull 
                            img_data = await r.content.read()
                            image_name = str(uuid.uuid4()) + '.png' #generate image
                            return DownFile(file_data=img_data,file_name=image_name)
                        
                except Exception as e:
                    logger.error(f"{ERROR_IN_IMAGE_DOWNLOAD}: {e}")
                    if DEBUG:
                        raise
                    return ERROR_IN_IMAGE_DOWNLOAD
                
            elif is_video:
                try:
                    async with session.get(url,headers=headers,ssl=False) as r:
                        if r.status == 200:
                            video_data = r.content
                            data = aiohttp.FormData()
                            data.add_field('file',data,filename=f"{uuid.uuid4()}.mp4")
                            async with session.post(url='https://store1.gofile.io/contents/uploadfile',data=data,ssl=False) as d:
                                if d.status == 200:
                                    response = await d.json()
                                    download_page = response["data"]["downloadPage"]
                                    return DownFile(direct_link=download_page,file_data=video_data)
                                
                except Exception as e:
                    logger.error(f"{ERROR_IN_VIDEO_DOWNLOAD}: {e}")
                    if DEBUG:
                        raise
                    return ERROR_IN_VIDEO_DOWNLOAD
                
    except Exception as e:
        logger.error(f"{ERROR_IN_DOWNLOAD_THROUGH_TOR}: {e}")
        if DEBUG:
            raise
        return ERROR_IN_DOWNLOAD_THROUGH_TOR

async def down_media(url, embed, db, article_id, article_img=False) -> DownMedia:
    try:
        response = await download_img_through_tor(url=url)
        logger.info("is response -> " + str(bool(response)))
        if isinstance(response,DownFile):
            if response.direct_link: # if not bytes
                pass
            else:
                try:
                    name = response.file_name
                    image_bytes = io.BytesIO(response.file_data)
                    file = discord.File(fp=image_bytes, filename=name)

                    if embed:
                        embed.set_image(url=f"attachment://{name}")
                except Exception as e:
                    logger.error(f"Error processing image in down_media: {e}")
                    if DEBUG:
                        raise

            if response.direct_link:
                media = "video/mp4"
                file=response.direct_link
            else:
                media = "image/png"

            if not article_img:
                article_img = False

            try:
                db.add(
                    DbStruct.ArticleMedia(
                        article_id=int(article_id),
                        file_data=response.file_data,
                        media_type=media,
                        img_main=article_img,
                    )
                )
                db.commit()
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error in down_media: {e}")
                if DEBUG:
                    raise
        return DownMedia(media_type=media,file=file)
    except Exception as e:
        logger.error(f"Error adding media to database in down_media: {e}")
        if DEBUG:
            raise

        try:
            return DownMedia(media_type=media,file=file)
        except Exception as e:
            logger.error(f"Error in down_media: {e}")
            if DEBUG:
                raise
            return DownMedia(media_type=None,file=None)

class BackgroundTasks(commands.Cog):
    def __init__(self, bot: discord.Client):
        try:
            self.db = BotDb().session
            self.bot = bot
            self.get_latest_news.start()
        except Exception as e:
            logger.error(f"Error initializing BackgroundTasks: {e}")
            if DEBUG:
                raise

    async def send(
        self,
        channel:discord.channel,
        message: str = None,
        embed: discord.Embed = None,
        file: str = None,
    ):
        try:
            kwargs = {}
            if message:
                kwargs["content"] = message
            if embed:
                kwargs["embed"] = embed
            if file:
                kwargs["file"] = file

            message:discord.Message = await channel.send(**kwargs)
            try:
                await message.publish()
                asyncio.sleep(5)
            except Exception as e:
                logger.error(e)
            return message
        except Exception as e:
            logger.error(f"Error in send: {e}")
            if DEBUG:
                raise


    def add_article(self,article: dict, db: sqlalchemy.orm.Session):
                    try:
                        logger.info(article["url"])
                        articles_db = db.query(DbStruct.articles.url).all()
                        saved_articles = [x[0] for x in articles_db] # urls
                        if article["url"] in saved_articles:
                            return None
                        else:
                            if article["article_text"]:
                                if article["article_text"]["text"]:
                                    text = article["article_text"]["text"]
                                    obj = DbStruct.articles(
                                        title=article["title"],
                                        url=article["url"],
                                        author=article["author"],
                                        brief=article["brief"],
                                        article=mdformat.text(
                                            md=text, extensions=["gfm"]
                                        ),
                                    )

                            else:
                                obj = DbStruct.articles(
                                    title=article["title"],
                                    url=article["url"],
                                    author=article["author"],
                                    brief=article["brief"],
                                    article=None,
                                )

                        logger.info(obj)
                        if obj:
                            db.add(obj)
                            db.commit()
                        id = (
                            db.query(DbStruct.articles)
                            .filter(
                                DbStruct.articles.url
                                == article["url"]
                            )
                            .first()
                            .id
                        )
                        logger.info("ID -> "+ str(id))
                        article["id"] = id
                        logger.info(article["id"])
                    except Exception as e:
                        logger.error(
                            f"Error processing article {article.get('url')} in looparticles: {e}"
                        )
                        if DEBUG:
                            raise
                    return article

    @tasks.loop(minutes=timer)
    async def get_latest_news(self):
            api_resp:dict = await Api().get_all()
            articles_dict = dict(reversed(list(api_resp.items())))
            for key, value in articles_dict.items():
                for article in value: # value is list of articles
                    article = self.add_article(article=article,db=self.db)
                    if not article:
                        continue
                    try:
                        logger.info(article["url"])
                        send_channel = (
                            self.db.query(DbStruct.channels)
                            .filter(DbStruct.channels.source == str(article["source"]))
                            .first()
                        )
                        logger.info(article["url"],send_channel)
                        send_channel_id = send_channel.channel_id
                        try:
                            channel = self.bot.get_channel(send_channel_id)
                        except Exception as e:
                            logger.error(f"Error fetching channel {id}: {e}")
                            if DEBUG:
                                raise

                        article["title"] = article["title"][:255]
                        desc = f"{article['brief']}"
                        embed = discord.Embed(title=article["title"], description=desc)
                        embed.url = article["url"]
                        embed.set_author(name=article["author"])
                        embed.set_footer(text=f"كُتب في {article['date']}")

                        downloaded:DownMedia = await down_media(
                            article["img_url"],
                            embed=embed,
                            article_id=article["id"],
                            db=self.db,
                            article_img=True,
                        )
                        logger.info("DOwnloaded -> " + str(downloaded))
                        if downloaded.file:
                                if downloaded.media_type == "video/mp4":
                                    message = await self.send(
                                        channel=channel,
                                        message=f"🎥 [رابط تحميل الفيديو المرفق]({downloaded.file})",
                                        embed=embed,
                                    )
                                elif downloaded.media_type == "image/png":
                                    message = await self.send(
                                        channel=channel,
                                        embed=embed,
                                        file=downloaded.file,
                                    )

                        try:
                            article_data = article["article_text"]
                        except Exception as e:
                            logger.error(f"Error accessing article_text: {e}")
                            if DEBUG:
                                raise
                            article_data = None

                        if article_data:
                            if article_data["text"]:
                                try:
                                    article_text = split_text_by_character_limit(
                                        article_data["text"], 2000
                                    )
                                except Exception as e:
                                    logger.error(f"Error splitting article text: {e}")
                                    if DEBUG:
                                        raise
                                    article_text = [None]

                                try: 
                                    t = await message.create_thread(
                                        name=article["title"][:99]
                                    )
                                    for text in article_text:
                                        try:
                                            if text:
                                                await t.send(content=text)
                                        except Exception as e:
                                            logger.error(
                                                f"Error sending text in thread {t.id}: {e}"
                                            )
                                            if DEBUG:
                                                raise

                                    if article_data["images"]:
                                        for image in article_data["images"]:
                                            try:
                                                downloaded = await down_media(
                                                    str(image),
                                                    embed=False,
                                                    article_id=article["id"],
                                                    db=self.db,
                                                )
                                                downloaded.file.filename = (
                                                    "SPOILER_" + downloaded.file.filename
                                                )
                                                await t.send(file=downloaded.file)
                                            except Exception as e:
                                                logger.error(
                                                    f"Error sending image in thread {t.id}: {e}"
                                                )
                                                if DEBUG:
                                                    raise

                                    if article_data["videos"]:
                                        for vid in article_data["videos"]:
                                            try:
                                                downloaded = await down_media(
                                                    vid,
                                                    embed=False,
                                                    article_id=article["id"],
                                                    db=self.db,
                                                )
                                                if downloaded.media_type == "video/mp4":
                                                    await t.send(downloaded.file)
                                            except Exception as e:
                                                logger.error(
                                                    f"Error sending video in thread {t.id}: {e}"
                                                )
                                                if DEBUG:
                                                    raise
                                except Exception as e:
                                        logger.error(f"Error creating thread: {e}")
                                        if DEBUG:
                                            raise

                        try:
                            files = glob.glob("/imgs/" + "*")
                            for file in files:
                                try:
                                    os.remove(file)
                                except Exception as e:
                                    logger.error(f"Error removing file {file}: {e}")
                                    if DEBUG:
                                        raise
                        except Exception as e:
                            logger.error(f"Error cleaning up images: {e}")
                            if DEBUG:
                                raise
                    except Exception as e:
                        logger.error(f"Error processing article {article['url']}: {e}")
                        if DEBUG:
                            raise





async def setup(bot):
    try:
        await bot.add_cog(BackgroundTasks(bot))
    except Exception as e:
        logger.error(f"Error in setup: {e}")
        if DEBUG:
            raise