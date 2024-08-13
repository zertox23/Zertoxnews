import aiohttp
import requests_cache
from stem import Signal
from stem.control import Controller
from dotenv import load_dotenv
import os
import loguru
import uuid
import random
from loguru import logger

from models import ResponseObj

logger.add("logs_.log")


ERROR_IN_IMAGE_DOWNLOAD = "Error occurred in image download"
ERROR_IN_VIDEO_DOWNLOAD = "Error occurred in video download"
ERROR_IN_DOWNLOAD_THROUGH_TOR = "Error in download_img_through_tor"
IP_DIDNT_CHANGE = "IP didn't change, sorry try later" 


requests_cache.install_cache("api_cache", expire_after=900)
load_dotenv()
my_ip = os.environ.get("my_ip").strip()
proxy = str(os.environ.get("proxy"))
DEBUG = bool(os.environ.get("DEBUG"))

"""
def get_new_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='P@ss0987')
        controller.signal(Signal.NEWNYM)

"""


async def send_request_through_tor(url: str, method: str):
    #    if random.choice([1,2,3,4,5,6,7,8,9,10]) == 2:
    #        get_new_ip()

    async with aiohttp.ClientSession() as s:
        async with s.get("http://icanhazip.com/", timeout=30,ssl=False) as response:
            text = await response.text()
            print(text.strip(), my_ip)
            if text.strip() != my_ip:
                return IP_DIDNT_CHANGE
            else:
                if method.upper() == "GET":
                    try:
                        print(url)
                        user_agent = {
                            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
                        }
                        async with s.get(url=url,  headers=user_agent,timeout=30,ssl=False) as r:
                            content = await r.content.read()
                            return ResponseObj(request=r,content=content) 
                    except Exception as e:
                        loguru.logger.error(e)
