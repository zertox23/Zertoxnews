from typing import Union
from fastapi import FastAPI
from scraper import Scraper
from dotenv import load_dotenv
import os
import time
import uvicorn
import re
import json
from Types import Chirp

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

@app.get("/api/sources")
def sources():
    return {"sources":["amaq_agency","dawla_news","zalaqa_news","shahada_agency","almirsad_news"]}

if __name__ == "__main__":
    config = uvicorn.Config("api_run:app", port=2222, log_level="info")
    server = uvicorn.Server(config)
    server.run()


@app.get("/api/almirsad_agency")
def almirsad_agency():
    s = Scraper(my_ip)
    d = s.get_last_almirsad_news()
    data = {"AlmirsadAgency":d}
    return data




@app.post("/api/add_chirpwire")
def add_chirpwire(chirp:Chirp):
    print(chirp.url)
    if chirp.url:
        pattern = r'^https:\/\/chirpwire\.net\/[a-zA-Z0-9_-]+$'
        def is_valid_url(url):
            return re.match(pattern, url) is not None
        
        if is_valid_url(str(chirp.url)):
            try:
                with open("chirpwire.json","r") as f:
                    d = json.load(f)
                    l = d["chirpwire"]
                    if chirp.url not in l:
                        l.append(str(chirp.url))
                    d["chirpwire"] = l
                with open("chirpwire.json","w") as f:
                    json.dump(d,f)
                return True
            except:
                return "potato"
            
        else:
            return False

@app.get("/api/chirpwire")
def last_chirp():
    s = Scraper(my_ip)
    d = s.get_last_chirpwire_news()
    return {"ChirpwireNews":d}

@app.get("/api/tolo_agency")
def last_tolo():
    s = Scraper(my_ip)
    d = s.get_last_tolo_news()
    return {"tolo":d}