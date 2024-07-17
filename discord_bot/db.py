from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, DateTime,LargeBinary
from sqlalchemy.orm import declarative_base,mapped_column
from sqlalchemy.orm import sessionmaker
import datetime
import io

global base
Base = declarative_base()

class DbStruct:
    class articles(Base):
        __tablename__ = "articles"
        id = Column("id",Integer,autoincrement=True,primary_key=True)
        img_url = Column("img_url",String)
        title = Column("title",String)
        url = Column("url",String)
        date = Column("date",String)
        author = Column("author",String)
        brief = Column("brief",String)
        article = Column("article",String)
        
        def __init__(self,img_url:str,title:str,url:str,author:str,brief:str,article:str,date:datetime.datetime=datetime.datetime.now()):
            self.img_url = img_url
            self.title  = title
            self.url = url
            self.date = date
            self.author = author
            self.brief = brief
            self.article = article

    class channels(Base):
        __tablename__ = "channels"
        id = Column("id",Integer,autoincrement=True,primary_key=True)
        source = Column("source",String)
        channel_id= Column("channel_id",Integer)

        def __init__(self,source:str,channel_id:int):
            self.source = source
            self.channel_id = channel_id

    class sources(Base):
        __tablename__ = "sources"
        id = Column("id",Integer,autoincrement=True,primary_key=True)
        source= Column("source",String)

        def __init__(self,source:str):
            self.source = source

class BotDb:
    def __init__(self) -> None:
        engine = create_engine("mysql:///database.db")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        self.session = Session() 
        