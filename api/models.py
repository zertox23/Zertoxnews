from pydantic import BaseModel
from typing import Optional
import discord


class ResponseObj(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    request:any = None
    content:bytes = None 

class DownFile(BaseModel):
    
    file_name: Optional[str] = None
    file_data: Optional[bytes] = None
    direct_link: Optional[str] = None

class WebsiteData(BaseModel):
    data: dict