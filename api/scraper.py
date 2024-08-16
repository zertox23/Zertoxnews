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
from models import ResponseObj
from loguru import logger


logger.add("logs_.log")


IP_DIDNT_CHANGE = "IP didn't change, sorry try later" 


global data
data = []

async def fetch_og_metadata(url):
    print(url)
    response = await send_request_through_tor(url, method="GET")
    if response.request != IP_DIDNT_CHANGE:
        if response:
            print(response.request.status)
            if response.request.status != 404:
                content = response.content
                soup = BeautifulSoup(content, "html.parser")
                og_title = soup.find("meta", property="og:title")
                og_description = soup.find("meta", property="og:description")
                og_image = soup.find("meta", property="og:image")
                og_url = soup.find("meta", property="og:url")

                title = (og_title["content"] if og_title else "None",)
                if title != None or "None":
                    title = title[0]
                description = (og_description["content"] if og_description else "None",)
                if description != None or "None":
                    description = description[0]
                image = (og_image["content"] if og_image else "None",)
                if image != None or "None":
                    image = image[0]
                url = og_url["content"] if og_url else url
                domain = urlparse(url).netloc
                article = Article(
                    title=title if title != "None" or None else "None",
                    img_url=image if image != "None" or None else "None",
                    url=url if url != "None" or None else "None",
                    author=domain if domain != "None" or None else "None",
                    brief=description if description != "None" or None else "None",
                    article_text=None,
                    source=domain if domain != "None" or None else "None",
                    date="مجهول",
                )
                return article
            else:
                return None


class Scraper:
    def __init__(self, sys_ip: str) -> None:
        self.sys_ip = sys_ip

    def scrape_images_and_videos(self, main_item, url):
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

        image_attributes = ["src", "data-src"]
        video_attributes = ["src", "data-src", "data-video", "data-video-src"]

        image_urls = extract_media_urls("img", image_attributes)
        video_urls = extract_media_urls("video", video_attributes)
        return image_urls, video_urls

    async def get_user_added(self):
        articles = {}
        print(os.system("ls"))
        with open("scrapes.json", "r") as f:
            scrapes = json.load(f)
        for url in scrapes:
                domain = urlparse(url).netloc
                articles[domain] = []
                r = await send_request_through_tor(url=url.strip(), method="GET")
                r.request.raise_for_status()  # Raise an error for HTTP response codes 4xx/5xx
                # Parse the response content
                soup = BeautifulSoup(r.content, "html.parser")

                # Find the articles parent element
                parent_element = scrapes[url]["articles_parent"]
                results = soup.find(
                    parent_element["element"], attrs=parent_element["attrs"]
                )

                if results is None:
                    print(f"Warning: No parent element found for URL {url}")
                    continue

                # Write the results to a file for debugging
                # Find all article objects
                article_obj = scrapes[url]["article_obj"]
                article_elements = results.find_all(
                    article_obj["element"], attrs=article_obj["attrs"]
                )

                if not article_elements:
                    print(f"Warning: No article elements found for URL {url}")


                # Process each article
                for result in article_elements[:6]:
                    try:
                        href = result.find("a")["href"]
                        if not str(href).startswith("http"):
                            href = "http://" + domain + href

                        if href:
                            article_data = await fetch_og_metadata(str(href))
                            if article_data:
                                articles[domain].append(article_data)
                    except (TypeError, KeyError) as e:
                        logger.error(e)
                    except Exception as e:
                        logger.error(e)

        return articles

    async def test_new_web(self, scrapes):
        articles = {}
        detailed_data = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "articles_found": 0,
            "articles_processed": 0,
            "errors": [],
        }

        for url in scrapes:
            domain = urlparse(url).netloc
            articles[domain] = []
            detailed_data["total_requests"] += 1

            try:
                # Attempt to send a request to the URL
                r = await send_request_through_tor(url=url.strip(), method="GET")
                r.request.raise_for_status()  # Raise an error for HTTP response codes 4xx/5xx

                detailed_data["successful_requests"] += 1

                # Parse the response content
                soup = BeautifulSoup(r.content, "html.parser")

                # Find the articles parent element
                parent_element = scrapes[url]["articles_parent"]
                results = soup.find(
                    parent_element["element"], attrs=parent_element["attrs"]
                )

                if results is None:
                    print(f"Warning: No parent element found for URL {url}")
                    continue

                # Write the results to a file for debugging
                # Find all article objects
                article_obj = scrapes[url]["article_obj"]
                article_elements = results.find_all(
                    article_obj["element"], attrs=article_obj["attrs"]
                )

                if not article_elements:
                    print(f"Warning: No article elements found for URL {url}")

                detailed_data["articles_found"] += len(article_elements)

                # Process each article
                for result in article_elements[:6]:
                    try:
                        href = result.find("a")["href"]
                        if not str(href).startswith("http"):
                            href = "http://" + domain + href

                        if href:
                            article_data = await fetch_og_metadata(str(href))
                            if article_data:
                                articles[domain].append(article_data)
                                detailed_data["articles_processed"] += 1
                    except (TypeError, KeyError) as e:
                        detailed_data["errors"].append(
                            f"Error processing article link for URL {url}: {e}"
                        )
                    except Exception as e:
                        detailed_data["errors"].append(
                            f"Unexpected error processing article for URL {url}: {e}"
                        )

            except requests.RequestException as e:
                detailed_data["failed_requests"] += 1
                detailed_data["errors"].append(f"Request error for URL {url}: {e}")
            except Exception as e:
                detailed_data["errors"].append(
                    f"Unexpected error processing URL {url}: {e}"
                )

        return {"articles": articles, "detailed_data": detailed_data}
