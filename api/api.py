from typing import Union
from fastapi import FastAPI,HTTPException
from scraper import Scraper
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import time
import json
import uvicorn
from urllib.parse import urlparse



load_dotenv()
app = FastAPI()

class WebsiteData(BaseModel):
    data:dict
json_file_path = "scrapes.json"


my_ip = os.environ.get("my_ip")
@app.get("/api/latest_news")
def latest_news():

    s = Scraper(my_ip)
    #s.get_all_news()
    zalaqa = s.get_last_zalaqa_news()
    amaq = s.get_last_amaq_news()
    dawla= s.get_last_dawla_news()
    shahada = s.get_last_news()
    almirsad = s.get_last_almirsad_news()
    data = {"ZalaqaInfoGraphics":zalaqa,"AmaqAgency":amaq,"DawlaNews":dawla,"ShahadaAgency":shahada,"AlmirsadAgency":almirsad}
    
    return data

@app.get("/api/shahada_agency")
def shahada_agency():
    s = Scraper(my_ip)
    shahada = s.get_last_news()
    data = {"ShahadaAgency":shahada}
    return data


@app.get("/api/amaq_agency")
def amaq_agency():
    s = Scraper(my_ip)
    amaq = s.get_last_amaq_news()
    data = {"AmaqAgency":amaq}
    return data

@app.get("/api/dawla_agency")
def dawla_agency():
    s = Scraper(my_ip)
    dawla = s.get_last_dawla_news()
    data = {"DawlaAgency":dawla}
    return data

@app.get("/api/user_added")
def user_added():
    s = Scraper(my_ip)
    data = s.get_user_added()
    data = {"UserAdded":data}
    return data

@app.post("/api/test_scrape")
async def test_website(data: WebsiteData):
    s = Scraper(my_ip)
    with open("test.py","w") as f:
        f.write(str(data.data))

    data = s.test_new_web(scrapes=data.data)
    return {"data":data}

@app.get("/api/sources")
def sources():
    source_list = ["amaq_agency","dawla_news","zalaqa_news","shahada_agency","almirsad_news"]
    with open(json_file_path,"r") as f:
        l = json.load(f)
        source_list.extend([urlparse(url).netloc for url in list(l.keys())])
    return {"sources":source_list}



@app.get("/api/almirsad_agency")
def almirsad_agency():
    s = Scraper(my_ip)
    d = s.get_last_almirsad_news()
    data = {"AlmirsadAgency":d}
    return data



# Pydantic model for the data


@app.post("/api/add_source/")
async def add_website(data: WebsiteData):
    data:dict = data.data
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
            return {"message": "Website already exists.", "existing_data": existing_data[list(data.data.keys())[0]]}
        
        # Update the existing data with the new website
        existing_data[list(data.keys())[0]] = data[list(data.keys())[0]]

        # Save the updated data back to the JSON file
        with open(json_file_path, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, indent=4, ensure_ascii=False)

        return {"message": "Website added successfully.", "added_data": existing_data[list(data.keys())[0]]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    config = uvicorn.Config("api:app", port=2222, log_level="info",host="0.0.0.0")
    server = uvicorn.Server(config)
    server.run()


