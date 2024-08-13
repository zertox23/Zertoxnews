from pydantic import BaseModel
from typing import Optional
import datetime


class Article(BaseModel):
    img_url: Optional[str] = "None"
    title: Optional[str] = "None"
    url: Optional[str] = "None"
    date: Optional[str] = "None"
    author: Optional[str] = "None"
    brief: Optional[str] = "None"
    article_text: Optional[dict] = "None"
    source: Optional[str] = "None"
