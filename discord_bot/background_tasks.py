import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import requests
from loguru import logger
import re
import uuid
from chunkify import chunkify
import sqlalchemy.orm
from db import BotDb, DbStruct
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy
import textwrap
import mdformat
import glob
import io
from api import Api

load_dotenv()
proxy = str(os.environ.get("proxy"))
DEBUG = False

timer = int(os.environ.get("time_between_checks"))
if timer < 3:
    timer = 3

logger.add("logs_.log")


def split_text_by_character_limit(text, char_limit):
    try:
        paragraphs = text.splitlines()
        segments = []
        current_segment = ""

        for paragraph in paragraphs:
            try:
                wrapped = textwrap.fill(
                    paragraph, width=char_limit, replace_whitespace=False
                )
                lines = wrapped.split("\n")

                for line in lines:
                    try:
                        if len(current_segment) + len(line) > char_limit:
                            segments.append(current_segment.rstrip())
                            current_segment = ""
                        current_segment += line + "\n"
                    except Exception as e:
                        logger.error(
                            f"Error in processing line in split_text_by_character_limit: {e}"
                        )
                        if DEBUG:
                            raise

            except Exception as e:
                logger.error(
                    f"Error in processing paragraph in split_text_by_character_limit: {e}"
                )
                if DEBUG:
                    raise

        if current_segment:
            try:
                current_segment = current_segment.rstrip()
                current_segment2 = mdformat.text(current_segment, extensions=["gfm"])
                if len(current_segment2) >= 1999:
                    segments.extend(
                        split_text_by_character_limit(current_segment, char_limit=1500)
                    )
                else:
                    segments.append(current_segment2)
            except Exception as e:
                logger.error(
                    f"Error in final segment processing in split_text_by_character_limit: {e}"
                )
                if DEBUG:
                    raise

        return segments
    except Exception as e:
        logger.error(f"Error in split_text_by_character_limit: {e}")
        if DEBUG:
            raise
        return []


async def download_img_through_tor(url: str, folder: str, method: str = "GET"):
    try:
        tor_proxy = proxy  # Assuming Tor proxy is running locally

        response = requests.get("http://icanhazip.com/", proxies={"http": tor_proxy})
        current_ip = response.text
        if current_ip.strip() == os.environ.get("my_ip").strip():
            return False

        if method.upper() == "GET" and ".mp4" not in url:
            try:
                r = requests.get(
                    url,
                    proxies={"http": tor_proxy},
                    headers={"User-agent": "Mozilla/5.0"},
                )
                if r.status_code == 200:
                    img_data = r.content
                    image_name = str(uuid.uuid4()) + ".png"
                    return [str(image_name), img_data]
            except Exception as e:
                logger.error(f"Error occurred in image download: {e}")
                if DEBUG:
                    raise
                return False
        elif ".mp4" in url:
            try:
                r = requests.get(
                    url,
                    proxies={"http": tor_proxy},
                    headers={"User-agent": "Mozilla/5.0"},
                )
                if r.status_code == 200:
                    video_data = r.content
                    d = requests.post(
                        "https://store1.gofile.io/contents/uploadfile",
                        files={"file": (f"{uuid.uuid4()}.mp4", video_data)},
                        proxies={"http": tor_proxy},
                    )
                    if d.status_code == 200:
                        response = d.json()
                        download_page = response["data"]["downloadPage"]
                        return [download_page, video_data]
            except Exception as e:
                logger.error(f"Error occurred in video download: {e}")
                if DEBUG:
                    raise
                return False
        return False
    except Exception as e:
        logger.error(f"Error in download_img_through_tor: {e}")
        if DEBUG:
            raise
        return False


def rnewlines(text: str):
    try:
        # Replace sequences of '#' characters
        for x in range(3, 6):
            try:
                text = text.replace(x * "#", "###")
            except Exception as e:
                logger.error(f"Error replacing '#' characters in rnewlines: {e}")
                if DEBUG:
                    raise

        # Replace sequences of newlines (more than two consecutive)
        try:
            text = re.sub(r"\n{3,}", "\n\n", text)
        except Exception as e:
            logger.error(f"Error replacing newlines in rnewlines: {e}")
            if DEBUG:
                raise

        return text
    except Exception as e:
        logger.error(f"Error in rnewlines: {e}")
        if DEBUG:
            raise
        return text


async def down_media(url, embed, db, article_id, article_img=False):
    try:
        path = await download_img_through_tor(url=url, folder=os.getcwd() + "/imgs")
        if path:
            if "http" in path[0]:
                pass
            else:
                try:
                    name = path[0]
                    image_bytes = io.BytesIO(path[1])
                    file = discord.File(fp=image_bytes, filename=name)
                    path[0] = file

                    if embed:
                        embed.set_image(url=f"attachment://{name}")
                except Exception as e:
                    logger.error(f"Error processing image in down_media: {e}")
                    if DEBUG:
                        raise

            if isinstance(path[0], str):
                media = "video/mp4"
            else:
                media = "image/png"

            if not article_img:
                article_img = False

            try:
                db.add(
                    DbStruct.ArticleMedia(
                        article_id=int(article_id),
                        file_data=path[1],
                        media_type=media,
                        img_main=article_img,
                    )
                )
                db.commit()
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error in down_media: {e}")
                if DEBUG:
                    raise
    except Exception as e:
        logger.error(f"Error adding media to database in down_media: {e}")
        if DEBUG:
            raise

        try:
            return {"media_type": media, "path": path}
        except Exception as e:
            logger.error(f"Error in down_media: {e}")
            if DEBUG:
                raise
            return {"media_type": None, "path": None}


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
        channels: list,
        message: str = None,
        embed: discord.Embed = None,
        file: str = None,
    ):
        try:
            messages = []
            for channel in channels:
                try:
                    kwargs = {}
                    if message:
                        kwargs["content"] = message
                    if embed:
                        kwargs["embed"] = embed
                    if file:
                        kwargs["file"] = file

                    messages.append(await channel.send(**kwargs))
                except Exception as e:
                    logger.error(f"Error sending message to channel {channel.id}: {e}")
                    if DEBUG:
                        raise

            return messages
        except Exception as e:
            logger.error(f"Error in send: {e}")
            if DEBUG:
                raise
            return []

    @tasks.loop(minutes=timer)
    async def get_latest_news(self):
        try:

            def looparticles(
                articles: list, sending_articles: list, db: sqlalchemy.orm.Session
            ):
                try:
                    for article in articles:
                        try:
                            articles_db = db.query(DbStruct.articles.url).all()
                            if article["url"] in [x[0] for x in articles_db]:
                                pass
                            else:
                                sending_articles.append(article)
                                if not article["article_text"]:
                                    obj = DbStruct.articles(
                                        img_url=article["img_url"],
                                        title=article["title"],
                                        url=article["url"],
                                        author=article["author"],
                                        brief=article["brief"],
                                        article=None,
                                    )
                                else:
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

                                db.add(obj)
                                db.commit()
                                sending_articles[-1]["id"] = (
                                    db.query(DbStruct.articles)
                                    .filter(
                                        DbStruct.articles.url
                                        == sending_articles[-1]["url"]
                                    )
                                    .first()
                                    .id
                                )
                        except Exception as e:
                            logger.error(
                                f"Error processing article {article.get('url')} in looparticles: {e}"
                            )
                            if DEBUG:
                                raise
                    return sending_articles
                except Exception as e:
                    logger.error(f"Error in looparticles: {e}")
                    if DEBUG:
                        raise
                    return sending_articles

            sending_articles = []
            api_resp = await Api().get_all()
            for key, value in api_resp.items():
                try:
                    sending_articles = looparticles(
                        articles=value, sending_articles=sending_articles, db=self.db
                    )
                except Exception as e:
                    logger.error(f"Error processing API response for key {key}: {e}")
                    if DEBUG:
                        raise

            sending_articles.reverse()
            logger.info(f"SENDING ARTICLES: {len(sending_articles)}")
            for article in sending_articles:
                try:
                    logger.info(article["url"])
                    send_channels = (
                        self.db.query(DbStruct.channels)
                        .filter(DbStruct.channels.source == str(article["source"]))
                        .all()
                    )
                    send_channels = [int(x.channel_id) for x in send_channels]
                    send_channels_list = []
                    for id in send_channels:
                        try:
                            channel = self.bot.get_channel(id)
                            send_channels_list.append(channel)
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

                    d = await down_media(
                        article["img_url"],
                        embed=embed,
                        article_id=article["id"],
                        db=self.db,
                        article_img=True,
                    )
                    if d["path"]:
                        if d["path"][0]:
                            if d["media_type"] == "video/mp4":
                                messages = await self.send(
                                    channels=send_channels_list,
                                    message=f"🎥 [رابط تحميل الفيديو المرفق]({d['path'][0]})",
                                    embed=embed,
                                )
                            elif d["media_type"] == "image/png":
                                logger.info("FILE ->" + str(d["path"][0]))
                                messages = await self.send(
                                    channels=send_channels_list,
                                    embed=embed,
                                    file=d["path"][0],
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

                            for message in messages:
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
                                                d = await down_media(
                                                    str(image),
                                                    embed=False,
                                                    article_id=article["id"],
                                                    db=self.db,
                                                )
                                                d["path"][0].filename = (
                                                    "SPOILER_" + d["path"][0].filename
                                                )
                                                await t.send(file=d["path"][0])
                                            except Exception as e:
                                                logger.error(
                                                    f"Error sending image in thread {t.id}: {e}"
                                                )
                                                if DEBUG:
                                                    raise

                                    if article_data["videos"]:
                                        for vid in article_data["videos"]:
                                            try:
                                                d = await down_media(
                                                    vid,
                                                    embed=False,
                                                    article_id=article["id"],
                                                    db=self.db,
                                                )
                                                if d["media_type"] == "video/mp4":
                                                    await t.send(d["path"][0])
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

        except Exception as e:
            logger.error(f"Error in get_latest_news: {e}")
            if DEBUG:
                raise


async def setup(bot):
    try:
        await bot.add_cog(BackgroundTasks(bot))
    except Exception as e:
        logger.error(f"Error in setup: {e}")
        if DEBUG:
            raise
