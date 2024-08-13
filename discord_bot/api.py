import aiohttp
from dotenv import load_dotenv
import os
import time
import json

load_dotenv()


class Api:
    def __init__(self, api_url=str(os.environ.get("api_url"))):
        self.api_url = api_url
        return None

    async def get_all(self) -> dict:
#        async with aiohttp.ClientSession() as session:
            #async with session.get(self.api_url + "/api/latest_news") as r:

        x = {}
        y = await self.get_all_user_data(x)
        return y

    async def get_all_user_data(self, all_data: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url + "/api/user_added") as r:
                js = await r.json()
                for site in js["UserAdded"]:

                    all_data[site] = js["UserAdded"][site]
                with open("x.py", "w") as f:
                    f.write(
                        str("JS:" + str(js))
                        + "\n\n"
                        + str(site)
                        + "\n\n"
                        + str(all_data)
                    )
                return all_data

    async def sources(self) -> list:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url + "/api/sources") as r:
                d = await r.json()
                if d:
                    return d["sources"]
                else:
                    return d

    async def test_web(self, data: dict) -> json:
        payload = {"data": data}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url + "/api/test_scrape",
                json=payload,
            ) as r:
                if r.headers["Content-Type"].startswith("application/json"):
                    jso = await r.json()
                    return jso
                else:
                    return await r.text()

    async def add_new_source(self, data: dict) -> json:
        payload = {"data": data}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url + "/api/add_source/", json=payload
            ) as r:
                jso = await r.json()
                return jso
