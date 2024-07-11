import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import json
import requests
import aiohttp
from loguru import logger
import re
import uuid
from chunkify import chunkify
import sqlalchemy.orm
from db import BotDb,DbStruct 
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy
import textwrap
import mdformat


load_dotenv()

class Api:
    def __init__(self):
        return None

    async def get_all(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:2222/api/latest_news") as r:
                return await r.json()

logger.add("logs_.log")
def split_text_by_character_limit(text, char_limit):
    paragraphs = text.splitlines()
    segments = []
    current_segment = ''

    for paragraph in paragraphs:
        wrapped = textwrap.fill(paragraph, width=char_limit, replace_whitespace=False)
        lines = wrapped.split('\n')
        
        for line in lines:
            if len(current_segment) + len(line) > char_limit:
                segments.append(current_segment.rstrip())
                current_segment = ''
            current_segment += line + '\n'

    if current_segment:
        segments.append(current_segment.rstrip())

    return segments
async def download_img_through_tor(url: str, folder: str, method: str = "GET"):
    tor_proxy = '127.0.0.1:8118'  # Assuming Tor proxy is running locally

    response = requests.get('http://icanhazip.com/', proxies={'http':tor_proxy})
    current_ip = response.text
    print("Current IP:", current_ip.strip())
    if current_ip.strip() == os.environ.get("my_ip").strip():
        print("Tor connection failed. IP address did not change.")
        return False
        
    if method.upper() == "GET" and ".mp4" not in url:
        print("IN GET AND IMG")
        try:
            r = requests.get(url, proxies={'http':tor_proxy}, headers={'User-agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                img_data = r.content
                image_name = str(uuid.uuid4()) + '.jpg'
                image_path = os.path.join(folder, image_name)
                with open(image_path, 'wb') as f:
                    f.write(img_data)

                print(f"Image downloaded and saved: {image_path}")
                return image_path
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return False
    elif ".mp4" in url:
        print("MP4")
        r = requests.get(url, proxies={'http':tor_proxy}, headers={'User-agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            video_data =  r.content                    
            d = requests.post('https://store1.gofile.io/contents/uploadfile', files={"file": (f"{uuid.uuid4()}.mp4",video_data)},proxies={'http':tor_proxy})
            print(d.status_code)
            if d.status_code == 200:
                response = d.json()
                download_page = response["data"]["downloadPage"]
                print(download_page)
                return download_page
        return False


def rnewlines(text: str):
    # Replace sequences of '#' characters
    for x in range(3, 6):
        text = text.replace(x * "#", "###")
    
    # Replace sequences of newlines (more than two consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text

async def down_media(url,embed):
    path = await download_img_through_tor(url=url, folder=os.getcwd() + "/imgs")
    file = False
    if path:
        if "http" in path:
            pass
        else:
            file = discord.File(path)
            if embed:
                embed.set_image(url=f"attachment://{os.path.basename(path)}")
        if "alraud" in url:
            source = "is"
            if "http" in path:
                media = "video"
            else:
                media = "image"
        else:
            source = "aq"
            if "http" in path:
                media = "video"
            else:    
                media = "image"

    return {"source":source,"media_type":media,"path":path,"file_obj":file}

class BackgroundTasks(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.aq_channel = int(os.environ.get("aq_channel"))
        self.is_channel = int(os.environ.get("is_channel"))
        self.bot = bot
        self.get_latest_news.start()
        self.db = BotDb().session
    
    @tasks.loop(minutes=30)
    async def get_latest_news(self):
        def looparticles(articles: list,sending_articles: list,db:sqlalchemy.orm.Session):
           
            for article in articles:
                articles_db = db.query(DbStruct.articles.url).all()
                print(articles_db)
                if article["url"] in [x[0] for x in articles_db]:
                    pass
                else:
                    sending_articles.append(article)
                    obj = DbStruct.articles(img_url=article["img_url"],title=article["title"],url=article["url"],author=article["author"],brief=article["brief"],article=None)
                    db.add(obj)
                    db.commit()
            
            return sending_articles

        aq_channel = self.bot.get_channel(self.aq_channel)
        dawla_channel = self.bot.get_channel(self.is_channel)

        sending_articles = []

        api_resp = await Api().get_all()
        for key, value in api_resp.items():
                print("in except")
                sending_articles = looparticles(articles=value,sending_articles=sending_articles,db=self.db)

        sending_articles.reverse()
        print(str(len(sending_articles)))
        for article in sending_articles:
            try:
                article["title"] = article["title"][:255]
                desc = f"{article['brief']}"
                embed = discord.Embed(title=article["title"], description=desc)
                embed.url = article["url"]
                embed.set_author(name=article["author"])
                embed.set_footer(text=f"كُتب في {article['date']}")
                if "onion" in article["img_url"] or "alezza" in article["img_url"]:
                    d = await down_media(article["img_url"],embed=embed)
                    if d["path"]:
                        if d["source"] == "is" and d["media_type"] == "video":
                            message = await dawla_channel.send(f"🎥[رابط تحميل الفيديو المرفق]({d['path']})🎥",embed=embed,)
                        elif d["source"] == "is" and d["media_type"] == "image":
                                message = await dawla_channel.send(embed=embed, file=d['file_obj'])
                        elif d["source"] == "aq" and d["media_type"] == "video":
                                message = await aq_channel.send(f"[رابط تحميل الفيديو المرفق]({d['path']})",embed=embed,)
                        elif d["source"] == "aq" and d["media_type"] == "image":
                            message = await aq_channel.send(embed=embed, file=d['file_obj'])
                        
                        os.remove(d['path'])




                    """     path = await download_img_through_tor(url=article["img_url"], folder=os.getcwd() + "/imgs")
                            print(path)

                            if path:
                                if "http" in path:
                                    pass
                                else:
                                    file = discord.File(path)
                                    embed.set_image(url=f"attachment://{os.path.basename(path)}")
                                if "alraud" in article["url"]:
                                    if "http" in path:
                                        message = await dawla_channel.send(f"🎥[رابط تحميل الفيديو المرفق]({path})🎥",embed=embed,)
                                    else:
                                        message = await dawla_channel.send(embed=embed, file=file)
                                else:
                                    if "http" in path:
                                        message = await aq_channel.send(f"[رابط تحميل الفيديو المرفق]({path})",embed=embed,)
                                    else:    
                                        message = await aq_channel.send(embed=embed, file=file)
                                os.remove(path)
                    """ 
                else:
                    embed.set_image(url=article["img_url"])
                    if "alraud" in article["url"]:
                        message = await dawla_channel.send(embed=embed)
                    else:
                        message = await aq_channel.send(embed=embed)
                try:
                    print(article)
                    article_data = article["article_text"]
                    if article_data["text"]:
                        print(article_data["text"])
                        t = await message.create_thread(name=article["title"][:99])
                        for text in split_text_by_character_limit(article_data["text"],2000):
                            print(str(len(text)))
                            await t.send(content=mdformat.text(md=text,extensions=["gfm"]))
                        if article_data["images"]:
                            for image in article_data["images"]:
                                try:
                                    print(str(image))
                                    d = await down_media(str(image),embed=False)
                                    if d["file_obj"]:
                                        d['file_obj'].filename = "SPOILER_"+d['file_obj'].filename
                                        await t.send(file=d["file_obj"],)
                                    else:
                                        await t.send(d["path"]) 
                                    os.remove(d['path'])

                                except Exception as e:
                                    logger.error(e)
                                    os.remove(d['path'])

                        if article_data["videos"]:
                            for vid in article_data["videos"]:
                                d = await down_media(vid,embed=False)
                                if d["media_type"] == "video":
                                    await t.send(d['path'])
                                else:
                                    if d["media_type"] == "image":
                                        d['file_obj'].filename = "SPOILER_"+d['file_obj'].filename
                                        await t.send(file=["file_obj"])
                                os.remove(d['path'])

                except Exception as e:
                    print(f"errror in sending article_text {str(e)}")
            except Exception as e:

                logger.error(e)
async def setup(bot):
    await bot.add_cog(BackgroundTasks(bot))
