from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, DateTime,LargeBinary
from sqlalchemy.orm import declarative_base
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

class BotDb:
    def __init__(self) -> None:
        engine = create_engine("sqlite:///database.db")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        self.session = Session() 
        