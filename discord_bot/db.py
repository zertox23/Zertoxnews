import datetime
from sqlalchemy import (
    create_engine,
    Column,
    BigInteger,
    String,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.dialects.mysql import LONGTEXT, LONGBLOB, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
MYSQL_URL = os.environ.get("MYSQL_URL")
print("MYSQL_URL=" + MYSQL_URL)

Base = declarative_base()


class DbStruct:
    class articles(Base):
        __tablename__ = "articles"
        id = Column(BigInteger, primary_key=True, autoincrement=True)
        title = Column(LONGTEXT, nullable=True)
        url = Column(LONGTEXT, nullable=True)
        date = Column(DateTime, default=datetime.datetime.now, nullable=True)
        author = Column(LONGTEXT, nullable=True)
        brief = Column(LONGTEXT, nullable=True)
        article = Column(LONGTEXT, nullable=True)
        media = relationship("ArticleMedia", back_populates="article")

        def __init__(
            self,
            title: str,
            url: str,
            author: str,
            brief: str,
            article: str,
            date: datetime.datetime = None,
        ):
            self.title = title
            self.url = url
            self.date = date if date else datetime.datetime.now()
            self.author = author
            self.brief = brief
            self.article = article

    class ArticleMedia(Base):
        __tablename__ = "articles_media"
        id = Column(BigInteger, primary_key=True, autoincrement=True)
        article_id = Column(BigInteger, ForeignKey("articles.id"), nullable=False)
        file_data = Column(
            LONGBLOB, nullable=False
        )  # Consider using Binary for actual file data
        media_type = Column(String(255), nullable=False)
        img_main = Column(BOOLEAN, nullable=True)
        article = relationship("articles", back_populates="media")

        def __init__(
            self, article_id: int, file_data: bytes, media_type: str, img_main: bool
        ):
            self.article_id = article_id
            self.file_data = file_data
            self.media_type = media_type
            self.img_main = img_main

    class channels(Base):
        __tablename__ = "channels"
        id = Column(BigInteger, primary_key=True, autoincrement=True)
        source = Column(String(255), nullable=False)
        channel_id = Column(BigInteger, nullable=False)

        def __init__(self, source: str, channel_id: int):
            self.source = source
            self.channel_id = channel_id

    class sources(Base):
        __tablename__ = "sources"
        id = Column(BigInteger, primary_key=True, autoincrement=True)
        source = Column(String(255), nullable=False)

        def __init__(self, source: str):
            self.source = source


class BotDb:
    def __init__(self) -> None:
        engine = create_engine(MYSQL_URL)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
