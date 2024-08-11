import datetime
from sqlalchemy import create_engine, Column, BigInteger, String, DateTime,Text,BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os 

load_dotenv()
MYSQL_URL = os.environ.get("MYSQL_URL")
print("MYSQL_URL="+MYSQL_URL)

Base = declarative_base()

class DbStruct:
    class articles(Base):
        __tablename__ = "articles"
        id = Column(BigInteger, primary_key=True, autoincrement=True)
        img_url = Column(Text())
        title = Column(Text())
        url = Column(Text())
        date = Column(DateTime, default=datetime.datetime.now)
        author = Column(String(255))
        brief = Column(String(255))
        article = Column(Text())  
        
        def __init__(self, img_url: str, title: str, url: str, author: str, brief: str, article: str, date: datetime.datetime = None):
            self.img_url = img_url
            self.title  = title
            self.url = url
            self.date = date if date else datetime.datetime.now()
            self.author = author
            self.brief = brief
            self.article = article

    class channels(Base):
        __tablename__ = "channels"
        id = Column(BigInteger, primary_key=True, autoincrement=True)
        source = Column(String(255))
        channel_id = Column(BigInteger)

        def __init__(self, source: str, channel_id: int):
            self.source = str(source)
            self.channel_id = int(channel_id)

    class sources(Base):
        __tablename__ = "sources"
        id = Column(BigInteger, primary_key=True, autoincrement=True)
        source = Column(String(255))

        def __init__(self, source: str):
            self.source = source

class BotDb:
    def __init__(self) -> None:
        engine = create_engine(MYSQL_URL)        
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        self.session = Session() 
        

