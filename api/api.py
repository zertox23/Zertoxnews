from typing import Union
from fastapi import FastAPI, HTTPException
from scraper import Scraper
from models import WebsiteData
from dotenv import load_dotenv
import os
import time
import json
import uvicorn
from urllib.parse import urlparse


load_dotenv()
app = FastAPI()





json_file_path = "scrapes.json"


my_ip = os.environ.get("my_ip")


@app.get("/api/user_added")
async def user_added():
    s = Scraper(my_ip)
    data = await s.get_user_added()
    data = {"UserAdded": data}
    return data


@app.post("/api/test_scrape")
async def test_website(data: WebsiteData):
    s = Scraper(my_ip)
    data = await s.test_new_web(scrapes=data.data)
    return {"data": data}


@app.get("/api/sources")
def sources():
    source_list = []

    with open(json_file_path, "r") as f:
        l = json.load(f)
        print(list(l.keys()))
        source_list.extend([urlparse(url).netloc for url in list(l.keys())])
    return {"sources": source_list}



@app.post("/api/add_source/")
async def add_website(data: WebsiteData):
    data: dict = data.data
    try:
        # Load the existing JSON data
        if os.path.exists(json_file_path):
            with open(json_file_path, "r", encoding="utf-8") as file:
                existing_data = json.load(file)
        else:
            existing_data = {}

        # Check if the["url"] already exists
        print(list(data.keys())[0])
        if list(data.keys())[0] in existing_data:
            return {
                "message": "Website already exists.",
                "existing_data": existing_data[list(data.data.keys())[0]],
            }

        # Update the existing data with the new website
        existing_data[list(data.keys())[0]] = data[list(data.keys())[0]]

        # Save the updated data back to the JSON file
        with open(json_file_path, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, indent=4, ensure_ascii=False)

        return {
            "message": "Website added successfully.",
            "added_data": existing_data[list(data.keys())[0]],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    config = uvicorn.Config("api:app", port=2222, log_level="info", host="0.0.0.0")
    server = uvicorn.Server(config)
    server.run()
