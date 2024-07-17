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
import aiofiles
from chunkify import chunkify
import sqlalchemy.orm
from db import BotDb,DbStruct 
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy
import textwrap
import mdformat
import glob
from api import Api

load_dotenv()


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
    if current_ip.strip() == os.environ.get("my_ip").strip():
        
        return False
        
    if method.upper() == "GET" and ".mp4" not in url:
        try:
            r = requests.get(url, proxies={'http':tor_proxy}, headers={'User-agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                img_data = r.content
                image_name = str(uuid.uuid4()) + '.jpg'
                image_path = os.path.join(folder, image_name)
                with open(image_path, 'wb') as f:
                    f.write(img_data)

                return str(image_path)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return False
    elif ".mp4" in url:
        r = requests.get(url, proxies={'http':tor_proxy}, headers={'User-agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            video_data =  r.content                    
            d = requests.post('https://store1.gofile.io/contents/uploadfile', files={"file": (f"{uuid.uuid4()}.mp4",video_data)},proxies={'http':tor_proxy})
            if d.status_code == 200:
                response = d.json()
                download_page = response["data"]["downloadPage"]
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
    print(url)
    path = await download_img_through_tor(url=url, folder=os.getcwd() + "/imgs")
    print(path)
    if path:
        if "http" in path:
            pass
        else:
            if embed:
                embed.set_image(url=f"attachment://{os.path.basename(path)}")

    if "http" in path:
        media = "video"
    else:
        media = "image"
    if "http" in path:
        media = "video"
    else:    
        media = "image"

    return {"media_type":media,"path":path}

class BackgroundTasks(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.db = BotDb().session
        self.bot = bot
        self.get_latest_news.start()
    
    async def send(self,channels:list,message:str=None,embed:discord.Embed=None,file:str= None):
        
        messages = []
        for channel in channels:
            kwargs = {}
            if message:
                kwargs['content'] = message
            if embed:
                kwargs['embed'] = embed
            if file:
                kwargs['file'] = discord.File(file)
            
            messages.append(await channel.send(**kwargs))
        
        return messages
    @tasks.loop(minutes=15)
    async def get_latest_news(self):
        def looparticles(articles: list,sending_articles: list,db:sqlalchemy.orm.Session):
           
            for article in articles:
                articles_db = db.query(DbStruct.articles.url).all()
                if article["url"] in [x[0] for x in articles_db]:
                    pass
                else:
                    sending_articles.append(article)
                    if not article["article_text"]:
                        obj = DbStruct.articles(img_url=article["img_url"],title=article["title"],url=article["url"],author=article["author"],brief=article["brief"],article=None)
                    else:
                        if article["article_text"]["text"]:
                            text  = article["article_text"]["text"]
                            obj = DbStruct.articles(img_url=article["img_url"],title=article["title"],url=article["url"],author=article["author"],brief=article["brief"],article=mdformat.text(md=text,extensions=["gfm"]))
                        else:
                            obj = DbStruct.articles(img_url=article["img_url"],title=article["title"],url=article["url"],author=article["author"],brief=article["brief"],article=None)

                    db.add(obj)
#                    db.commit()
            
            return sending_articles

        
        sending_articles = []

        api_resp = await Api().get_all()
        for key, value in api_resp.items():
                sending_articles = looparticles(articles=value,sending_articles=sending_articles,db=self.db)
            
        sending_articles.reverse()
        for article in sending_articles:
            print(len(sending_articles))
            print(str(article["source"]).capitalize())
            send_channels = self.db.query(DbStruct.channels).filter(DbStruct.channels.source == str(article["source"])).all()
            send_channels = [int(x.channel_id) for x in send_channels]
            send_channels_list = []
            for id in send_channels:
                try:
                    channel = self.bot.get_channel(id)
                    print(channel)
                    send_channels_list.append(channel)
                except Exception as e:
                    logger.error(str(e))

            print(send_channels_list)


#        try:
            article["title"] = article["title"][:255]
            desc = f"{article['brief']}"
            embed = discord.Embed(title=article["title"], description=desc)
            embed.url = article["url"]
            embed.set_author(name=article["author"])
            embed.set_footer(text=f"كُتب في {article['date']}")
            print("onion" in article["img_url"] or article["source"] in ["zalaqa_news"])
            if "onion" in article["img_url"] or article["source"] in ["zalaqa_news"]:
                d = await down_media(article["img_url"],embed=embed)
                if d["path"]:
                    
                    if d["media_type"] == "video":           
                        messages = await self.send(channels=send_channels_list,message=f"🎥[رابط تحميل الفيديو المرفق]({d['path']})🎥",embed=embed)
                    elif d["media_type"] == "image":
                            messages = await self.send(channels=send_channels_list,embed=embed, file=d['path'])
                    
                    os.remove(d['path'])

            else:
                print("in else")
                embed.set_image(url=article["img_url"])
                messages = await self.send(channels=send_channels_list,embed=embed)

            article_data = article["article_text"]
            try:

                if article_data["text"]:
                    try:
                        article_text = split_text_by_character_limit(article_data["text"],2000)
                    except:
                        article_text = [None]
                    for message in messages:
                #           try:
                            t = await message.create_thread(name=article["title"][:99])
                            for text in article_text:
                                
                                await t.send(content=mdformat.text(md=text,extensions=["gfm"]))
                            if article_data["images"]:
                                for image in article_data["images"]:
    #                                   try:
                                        d = await down_media(str(image),embed=False)
                                        if d["path"]:
                                            file = discord.File(d['path'],filename="SPOILER_"+str(uuid.uuid4())+".jpg")
                                            await t.send(file=file)
                                        else:
                                            await t.send(d["path"]) 

    #                                    except Exception as e:
                #                          logger.error(e)

                            if article_data["videos"]:
                                for vid in article_data["videos"]:
                                    d = await down_media(vid,embed=False)
                                    if d["media_type"] == "video":
                                        await t.send(d['path'])
                                    else:
                                        if d["media_type"] == "image":
                                            d = discord.File(d['path']).filename = "SPOILER_"+d['path'].filename
                                            await t.send(file=d)
            except Exception as e:
                logger.error(e)

            #files = glob.glob("/imgs/" + '*')
            #for file in files:
                #try:
            #        os.remove(file)
                #except Exception as e:
                #    logger.error(e) 
        #except Exception as e:
        #        logger.error(e) 

async def setup(bot):
    await bot.add_cog(BackgroundTasks(bot))
