import aiohttp

class Api:
    def __init__(self,api_url="http://127.0.0.1:2222"):
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