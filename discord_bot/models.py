from pydantic import BaseModel
from typing import Optional
import discord


class DownFile(BaseModel):
    
    file_name: Optional[str] = None
    file_data: Optional[bytes] = None
    direct_link: Optional[str] = None
class DownMedia(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    media_type: Optional[str]
    file:any