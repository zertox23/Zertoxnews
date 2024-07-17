from typing import Union
from fastapi import FastAPI
from scraper import Scraper
from dotenv import load_dotenv
import os
import time
import uvicorn


load_dotenv()
app = FastAPI()
my_ip = os.environ.get("my_ip")
@app.get("/api/latest_news")
def latest_news():

    s = Scraper(my_ip)
    #s.get_all_news()
    zalaqa = s.get_last_zalaqa_news()
    amaq = s.get_last_amaq_news()
    dawla= s.get_last_dawla_news()
    shahada = s.get_last_news()
    data = {"ZalaqaInfoGraphics":zalaqa,"AmaqAgency":amaq,"DawlaNews":dawla,"ShahadaAgency":shahada}
    
    return data

@app.get("/api/shahada_agency")
def latest_news():
    s = Scraper(my_ip)
    shahada = s.get_last_news()
    data = {"ShahadaAgency":shahada}
    return data


@app.get("/api/amaq_agency")
def latest_news():
    s = Scraper(my_ip)
    amaq = s.get_last_amaq_news()
    data = {"AmaqAgency":amaq}
    return data

@app.get("/api/dawla_agency")
def latest_news():
    s = Scraper(my_ip)
    dawla = s.get_last_dawla_news()
    data = {"DawlaAgency":dawla}
    return data

@app.get("/api/sources")
def sources():
    return {"sources":["amaq_agency","dawla_news","zalaqa_news","shahada_agency"]}
if __name__ == "__main__":
    config = uvicorn.Config("api:app", port=2222, log_level="info")
    server = uvicorn.Server(config)
    server.run()

