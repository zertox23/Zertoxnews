from bs4 import BeautifulSoup
from networking import send_request_through_tor
from Types import Article
import threading
import time
import markdownify
from urllib.parse import urljoin



class Scraper:
    def __init__(self,sys_ip:str) -> None:
        self.sys_ip = sys_ip
        self.shahada_agency_url = "https://shahadaagency.com"
        self.amaq_url  = "http://alraudzemjub7whxfmqxbmtt7lhz4qpqjydlrqzasbiymhk5bwkvxdid.onion/?cat=467"
        self.dawal_url = "http://alraudzemjub7whxfmqxbmtt7lhz4qpqjydlrqzasbiymhk5bwkvxdid.onion/?cat=485"
        self.zalaqa_url = "https://alezza.media/index.php?/category/33"

    def scrape_images_and_videos(self,main_item,url):
        """Scrapes images and videos from a webpage."""
        def extract_media_urls(tag, attributes):
            """Helper function to extract media URLs from a given tag and attributes."""
            media_tags = main_item.find_all(tag)
            media_urls = []
            for media in media_tags:
                for attribute in attributes:
                    src = media.get(attribute)
                    if src:
                        media_urls.append(urljoin(url, src))
                        media.extract()
                        break  
            return media_urls
        
        image_attributes = ['src', 'data-src']
        video_attributes = ['src', 'data-src', 'data-video', 'data-video-src']
        
        image_urls = extract_media_urls('img', image_attributes)
        video_urls = extract_media_urls('video', video_attributes)
        return image_urls, video_urls
    
    def get_all_news(self):
        data = []
        t = time.time()
        shahada = threading.Thread(target=self.get_last_news(), daemon=True)
        dawla = threading.Thread(target=self.get_last_dawla_news(), daemon=True)
        amaq = threading.Thread(target=self.get_last_amaq_news(),daemon=True)
        zalaqa = threading.Thread(target=self.get_last_zalaqa_news(),daemon=True)
        e = time.time() - t
        
        
    def get_last_news(self):
        articles = []
        r = send_request_through_tor(url=self.shahada_agency_url,method="GET")
        soup = BeautifulSoup(r.content,"html.parser")
        results = soup.find("div",class_="listing listing-grid listing-grid-1 clearfix columns-3")
        res = results.find_all("article")  
        for article in res:
            title = article.find('a',class_="post-title post-url")
            url = title['href']
            title = title.contents[0]
            author = article.find('i',class_="post-author author").text
            date = article.find('span',class_="time").text
            brief = article.find("div",class_="post-summary").text
            img = article.find("a",class_="img-holder")["data-src"]
            r = send_request_through_tor(url=url,method="GET")
            soup = BeautifulSoup(r.content,"html.parser")
            art = soup.find("article")
            images,videos = self.scrape_images_and_videos(art,url=self.shahada_agency_url)
            text= markdownify.markdownify(art.prettify())
            articles.append(Article(title=title,url=url,date=date,author=author,brief=brief,img_url=img,article_text={"text":text,"images":images,"videos":videos,},source="shahada_agency"))
        
        return articles
    
    def get_last_amaq_news(self):
        articles = []

        r = send_request_through_tor(url=self.amaq_url,method="GET")
        soup = BeautifulSoup(r.content,"html.parser")
        results = soup.find("ul",class_="posts-items")
        articles_res = results.find_all("li",class_="post-item tie-standard")
        for article in articles_res:
            title_tag = article.find("a",class_="post-thumb")
            title = title_tag["aria-label"]
            x = self.amaq_url
            url = x.replace("?cat=467",title_tag["href"])
            img = title_tag.find("img")["src"]
            x = self.amaq_url
            img = x.replace("?cat=467",f"/{img}")
            date = article.find("div",class_="day-month").find("span").text
            brief = ""
            r = send_request_through_tor(url=url,method="GET")
            soup = BeautifulSoup(r.content,"html.parser")
            art = soup.find("article")
            images,_ = self.scrape_images_and_videos(art,url=self.amaq_url.replace("?cat=467",""))                
            div = art.find("div",class_="entry-content entry clearfix")
            videos = ['']
            try:
                videos = [div.find("a",class_="shortc-button small button")["href"]]
            except:
                pass
            if '.mp4' in videos[0]:
                x = self.amaq_url 
                videos[0] = x.replace("?cat=467","")+videos[0]
                try:
                    div.find("a",class_="shortc-button small button").extract()
                except:
                    pass
            else:    
                videos = []
            try:
                div.find("a",class_="shortc-button small button").extract()
            except:
                pass
            text = markdownify.markdownify(art.prettify())    
            articles.append(Article(title=title,img_url=img,url=url,date=date,author="Amaq News Agency | وكاله اعماق الاخباريه",brief=brief,article_text={"text":text,"images":images,"videos":videos},source="amaq_agency"))
        
        return articles

    def get_last_dawla_news(self):
        articles = []

        r = send_request_through_tor(url=self.dawal_url,method="GET")
        soup = BeautifulSoup(r.content,"html.parser")
        results = soup.find("ul",class_="posts-items")
        articles_res = results.find_all("li",class_="post-item tie-standard")
        for article in articles_res:
            title_tag = article.find("a",class_="post-thumb")
            title = title_tag["aria-label"]
            x = self.dawal_url
            url = x.replace("?cat=485",title_tag["href"])
            img = title_tag.find("img")["src"]
            x = self.dawal_url
            img = x.replace("?cat=485",f"/{img}")
            date = article.find("div",class_="day-month").find("span").text
            brief = ""
            r = send_request_through_tor(url=url,method="GET")
            soup = BeautifulSoup(r.content,"html.parser")
            art = soup.find("article")
            images , videos = self.scrape_images_and_videos(art,url=self.dawal_url.replace("?cat=485",""))
            text = markdownify.markdownify(art.prettify())
            articles.append(Article(title=title,img_url=img,url=url,date=date,author="Dawla News | أخبار الدوله",brief=brief,article_text={"text":text,"images":images,"videos":videos},source="dawla_news"))
        
    
        return articles

    def get_last_zalaqa_news(self):
        articles = []
        r = send_request_through_tor(url=self.zalaqa_url.strip(),method="GET")
        soup = BeautifulSoup(r.content,"html.parser")
        results = soup.find("div",class_="content-grid pt-3")
        container  = results.find("ul",id="thumbnails")
        articles_res = container.find_all("li",class_="gdthumb crop")

        for article in articles_res:
            if len(articles) >= 6:
                return articles
            a = article.find("a")
            url = "https://alezza.media/"+a["href"]
            img = a.find("img")
            img = "https://alezza.media/"+img["pdf2tab"]
            date = "مجهول"
            articles.append(Article(title="انفوجرافيك الزلاقه",img_url=img,url=url,date=date,author="Zalaqa | الزلاقه",brief="",article_text={"text":"","images":[],"videos":[]},source="zalaqa_news"))
        
    


