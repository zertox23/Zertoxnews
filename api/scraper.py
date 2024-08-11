from bs4 import BeautifulSoup
from networking import send_request_through_tor
from Types import Article
import requests
import threading
import json
from urllib.parse import urlparse
import time
import markdownify
import os
from urllib.parse import urljoin


def fetch_og_metadata(url):
    print(url)
    response = send_request_through_tor(url,method="GET")
    print(response.status_code)
    if response.status_code != 404:
        soup = BeautifulSoup(response.content, 'html.parser')
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        og_image = soup.find('meta', property='og:image')
        og_url = soup.find('meta', property='og:url')

        title = og_title['content'] if og_title else None,
        if title:
            title = title[0]
        description =og_description['content'] if og_description else None,
        if description:
            description = description[0]
        image = og_image['content'] if og_image else None,
        if image:
            image = image[0]
        url= og_url['content'] if og_url else url
        domain = urlparse(url).netloc
        article =  Article(title=title,img_url=image,url=url,author=domain,brief=description,article_text=None,source=domain,date="مجهول")
        return article
    else:
        return None


class Scraper:
    def __init__(self,sys_ip:str) -> None:
        self.sys_ip = sys_ip
        self.shahada_agency_url = "https://shahadaagency.com"
        self.amaq_url  = "http://alraudzemjub7whxfmqxbmtt7lhz4qpqjydlrqzasbiymhk5bwkvxdid.onion/?cat=467"
        self.dawal_url = "http://alraudzemjub7whxfmqxbmtt7lhz4qpqjydlrqzasbiymhk5bwkvxdid.onion/?cat=485"
        self.zalaqa_url = "https://alezza.media/index.php?/category/33"
        self.almirsad_url = "https://almirsadar.com/"

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
        try:
            r = send_request_through_tor(url=self.shahada_agency_url, method="GET")
            soup = BeautifulSoup(r.content, "html.parser")
            results = soup.find("div", class_="listing listing-grid listing-grid-1 clearfix columns-3")
            res = results.find_all("article")
            for article in res:
                try:
                    title = article.find('a', class_="post-title post-url")
                    url = title['href']
                    title = title.contents[0]
                    author = article.find('i', class_="post-author author").text
                    date = article.find('span', class_="time").text
                    brief = article.find("div", class_="post-summary").text
                    img = article.find("a", class_="img-holder")["data-src"]
                    r = send_request_through_tor(url=url, method="GET")
                    soup = BeautifulSoup(r.content, "html.parser")
                    art = soup.find("article")
                    images, videos = self.scrape_images_and_videos(art, url=self.shahada_agency_url)
                    text = markdownify.markdownify(art.prettify())
                    articles.append(Article(title=title, url=url, date=date, author=author, brief=brief, img_url=img, article_text={"text": text, "images": images, "videos": videos}, source="shahada_agency"))
                except Exception:
                    continue  # Skip the current article and continue with the next one
        except Exception:
            return []  # Return an empty list if there's an error in fetching or parsing the page
        return articles

    def get_last_amaq_news(self):
        articles = []
        try:
            r = send_request_through_tor(url=self.amaq_url, method="GET")
            soup = BeautifulSoup(r.content, "html.parser")
            results = soup.find("ul", class_="posts-items")
            articles_res = results.find_all("li", class_="post-item tie-standard")
            for article in articles_res:
                try:
                    title_tag = article.find("a", class_="post-thumb")
                    title = title_tag["aria-label"]
                    x = self.amaq_url
                    url = x.replace("?cat=467", title_tag["href"])
                    img = title_tag.find("img")["src"]
                    x = self.amaq_url
                    img = x.replace("?cat=467", f"/{img}")
                    date = article.find("div", class_="day-month").find("span").text
                    brief = ""
                    r = send_request_through_tor(url=url, method="GET")
                    soup = BeautifulSoup(r.content, "html.parser")
                    art = soup.find("article")
                    images, _ = self.scrape_images_and_videos(art, url=self.amaq_url.replace("?cat=467", ""))
                    div = art.find("div", class_="entry-content entry clearfix")
                    videos = ['']
                    try:
                        videos = [div.find("a", class_="shortc-button small button")["href"]]
                    except:
                        pass
                    if '.mp4' in videos[0]:
                        x = self.amaq_url
                        videos[0] = x.replace("?cat=467", "") + videos[0]
                        try:
                            div.find("a", class_="shortc-button small button").extract()
                        except:
                            pass
                    else:
                        videos = []
                    try:
                        div.find("a", class_="shortc-button small button").extract()
                    except:
                        pass
                    text = markdownify.markdownify(art.prettify())
                    articles.append(Article(title=title, img_url=img, url=url, date=date, author="Amaq News Agency | وكاله اعماق الاخباريه", brief=brief, article_text={"text": text, "images": images, "videos": videos}, source="amaq_agency"))
                except Exception:
                    continue  # Skip the current article and continue with the next one
        except Exception:
            return []  # Return an empty list if there's an error in fetching or parsing the page
        return articles

    def get_last_dawla_news(self):
        articles = []
        try:
            r = send_request_through_tor(url=self.dawal_url, method="GET")
            soup = BeautifulSoup(r.content, "html.parser")
            results = soup.find("ul", class_="posts-items")
            articles_res = results.find_all("li", class_="post-item tie-standard")
            for article in articles_res:
                try:
                    title_tag = article.find("a", class_="post-thumb")
                    title = title_tag["aria-label"]
                    x = self.dawal_url
                    url = x.replace("?cat=485", title_tag["href"])
                    img = title_tag.find("img")["src"]
                    x = self.dawal_url
                    img = x.replace("?cat=485", f"/{img}")
                    date = article.find("div", class_="day-month").find("span").text
                    brief = ""
                    r = send_request_through_tor(url=url, method="GET")
                    soup = BeautifulSoup(r.content, "html.parser")
                    art = soup.find("article")
                    images, videos = self.scrape_images_and_videos(art, url=self.dawal_url.replace("?cat=485", ""))
                    text = markdownify.markdownify(art.prettify())
                    articles.append(Article(title=title, img_url=img, url=url, date=date, author="Dawla News | أخبار الدوله", brief=brief, article_text={"text": text, "images": images, "videos": videos}, source="dawla_news"))
                except Exception:
                    continue  # Skip the current article and continue with the next one
        except Exception:
            return []  # Return an empty list if there's an error in fetching or parsing the page
        return articles

    def get_last_zalaqa_news(self):
        articles = []
        try:
            r = send_request_through_tor(url=self.zalaqa_url.strip(), method="GET")
            soup = BeautifulSoup(r.content, "html.parser")
            results = soup.find("div", class_="content-grid pt-3")
            container = results.find("ul", id="thumbnails")
            articles_res = container.find_all("li", class_="gdthumb crop")

            for article in articles_res:
                try:
                    if len(articles) >= 6:
                        return articles
                    a = article.find("a")
                    url = "https://alezza.media/" + a["href"]
                    img = a.find("img")
                    img = "https://alezza.media/" + img["pdf2tab"]
                    date = "مجهول"
                    articles.append(Article(title="انفوجرافيك الزلاقه", img_url=img, url=url, date=date, author="Zalaqa | الزلاقه", brief="", article_text={"text": "", "images": [], "videos": []}, source="zalaqa_news"))
                except Exception:
                    continue  # Skip the current article and continue with the next one
        except Exception:
            return []  # Return an empty list if there's an error in fetching or parsing the page
        return articles
            
    def get_last_almirsad_news(self):
        articles = []
        try:
            r = send_request_through_tor(url=self.almirsad_url.strip(), method="GET")
            soup = BeautifulSoup(r.content, "html.parser")

            results = soup.find("div", class_="jeg_tabpost_content")

            tab = results.find("div", id="jeg_tabpost_3")
            res = tab.find_all("div", class_="jeg_postblock_content")

            for article in res:
                try:
                    a = article.find("a")
                    if a:
                        url = a["href"]

                    h3 = article.find("h3", class_="jeg_post_title")
                    title = h3.text
                    date = article.find("div", class_="jeg_meta_like")
                    if date:
                        date = date.text

                    img = None
                    r = send_request_through_tor(url=url.strip(), method="GET")
                    soup = BeautifulSoup(r.content, "html.parser")
                    imgdiv = soup.find("div", class_="jeg_featured featured_image")
                    a = imgdiv.find("a")
                    if a:
                        img = a["href"]

                    text = soup.find("div", class_="content-inner")
                    removeddiv = soup.find("div", class_="aioseo-author-bio-compact")  # a div that i don't need in the final text
                    removeddiv.extract()
                    text = markdownify.markdownify(text.prettify())
                    with open("almirsad.html", "w") as f:
                        f.write(soup.prettify())

                    with open("almirsad.md", "w") as f:
                        f.write(text)

                    articles.append(Article(title=title, url=url, date=date, img_url=img, author="almirsad | المرصد ميديا", brief="", article_text={"text": text, "images": [], "videos": []}, source="almirsad"))
                except Exception:
                    continue  # Skip the current article and continue with the next one
        except Exception:
            return []  # Return an empty list if there's an error in fetching or parsing the page
        return articles

    def get_user_added(self):
        articles = {}
        print(os.system("ls"))
        with open("scrapes.json","r") as f:
            scrapes = json.load(f)
        for url in scrapes:
                domain = urlparse(url).netloc
                articles[domain] = []
                r = send_request_through_tor(url=url.strip(), method="GET")
                soup = BeautifulSoup(r.content, "html.parser")
                results = soup.find(scrapes[url]["articles_parent"]["element"],attrs=scrapes[url]["articles_parent"]["attrs"])
                with open("data.html","w") as f:
                    f.write(str(results.prettify()))
                results = results.find_all(scrapes[url]["article_obj"]["element"],attrs=scrapes[url]["article_obj"]["attrs"])
                
                for result in results:
                    x = result.find('a')["href"]
                    if x:
                        if not str(x).startswith('http'):
                            x= domain+x
                            x= "http://"+x
                        articles[domain].append(fetch_og_metadata(str(x)))
        return articles

    def test_new_web(self, scrapes):
        articles = {}
        detailed_data = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "articles_found": 0,
            "articles_processed": 0,
            "errors": []
        }
        
        for url in scrapes:
            domain = urlparse(url).netloc
            articles[domain] = []
            detailed_data["total_requests"] += 1
            
            try:
                # Attempt to send a request to the URL
                r = send_request_through_tor(url=url.strip(), method="GET")
                r.raise_for_status()  # Raise an error for HTTP response codes 4xx/5xx
                
                detailed_data["successful_requests"] += 1
                
                # Parse the response content
                soup = BeautifulSoup(r.content, "html.parser")
                
                # Find the articles parent element
                parent_element = scrapes[url]["articles_parent"]
                results = soup.find(parent_element["element"], attrs=parent_element["attrs"])
                
                if results is None:
                    print(f"Warning: No parent element found for URL {url}")
                    continue
                
                # Write the results to a file for debugging
                with open("data.html", "w", encoding='utf-8') as f:
                    f.write(str(results.prettify()))
                
                # Find all article objects
                article_obj = scrapes[url]["article_obj"]
                article_elements = results.find_all(article_obj["element"], attrs=article_obj["attrs"])
                
                if not article_elements:
                    print(f"Warning: No article elements found for URL {url}")
                
                detailed_data["articles_found"] += len(article_elements)
                
                # Process each article
                for result in article_elements[:6]:
                    try:
                        href = result.find('a')["href"]
                        if not str(href).startswith('http'):
                            href = "http://"+domain+href

                        if href:
                            article_data = fetch_og_metadata(str(href))
                            if article_data:
                                articles[domain].append(article_data)
                                detailed_data["articles_processed"] += 1
                    except (TypeError, KeyError) as e:
                        detailed_data["errors"].append(f"Error processing article link for URL {url}: {e}")
                    except Exception as e:
                        detailed_data["errors"].append(f"Unexpected error processing article for URL {url}: {e}")
                
            except requests.RequestException as e:
                detailed_data["failed_requests"] += 1
                detailed_data["errors"].append(f"Request error for URL {url}: {e}")
            except Exception as e:
                detailed_data["errors"].append(f"Unexpected error processing URL {url}: {e}")
        
        return {"articles": articles, "detailed_data": detailed_data}

