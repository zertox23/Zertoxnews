import aiohttp
from dotenv import load_dotenv
import os
load_dotenv()

class Api:
    def __init__(self,api_url=str(os.environ.get("api_url"))):
        self.api_url = api_url
        return None
    
    async def get_all(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url+"/api/latest_news") as r:
                return await r.json()

    async def sources(self) -> list:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url+"/api/sources") as r:
                d = await r.json()
                if d:
                    return d["sources"]
                else:
                    return d