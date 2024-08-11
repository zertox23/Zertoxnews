import requests
import requests_cache
from stem import Signal
from stem.control import Controller
from dotenv import load_dotenv
import os
import loguru
import uuid
import random
requests_cache.install_cache('api_cache',expire_after=900)
load_dotenv()
my_ip = os.environ.get("my_ip").strip()
proxy = str(os.environ.get("proxy"))

"""
def get_new_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='P@ss0987')
        controller.signal(Signal.NEWNYM)

"""

def send_request_through_tor(url:str,method:str):
#    if random.choice([1,2,3,4,5,6,7,8,9,10]) == 2:
#        get_new_ip()

    response = requests.get('http://icanhazip.com/', proxies={'http': proxy})
    print(response.text.strip(),my_ip)
    if response.text.strip() == my_ip:
        return False
    else:
        if method.upper() == "GET":    
            try:
                print(url)
                user_agent = {'User-agent': 'Mozilla/5.0'}
                r = requests.get(url=url,proxies={'http': proxy},headers=user_agent)
                return r
            except Exception as e:
                loguru.logger.error(e)
        elif method.upper() == "POST":
            try:
                return requests.post(url=url,proxies={'http': proxy})     
            except Exception as e:
                loguru.logger.error(e)

def download_img_through_tor(url:str,folder:str,method:str="GET"):
    tor_proxy = 'http://127.0.0.1:8118'  # Assuming Tor proxy is running locally

    # Get your current IP to verify Tor connection
    response = requests.get('http://icanhazip.com/', proxies={'http': tor_proxy})
    print("Current IP:",response.text.strip())
    if response.text.strip() == my_ip:
        print("Tor connection failed. IP address did not change.")
        return False
    else:
        if method.upper() == "GET":
            try:
                user_agent = {'User-agent': 'Mozilla/5.0'}
                r = requests.get(url=url, proxies={'http': tor_proxy},headers=user_agent)
                # Check if response is an image
                # Generate a unique filename for the image
                image_name = str(uuid.uuid4()) + '.jpg'
                image_path = os.path.join(folder, image_name)

                with open(image_path, 'wb') as f:
                    f.write(r.content)

                print(f"Image downloaded and saved: {image_path}")
                return image_path

            except Exception as e:
                print(f"Error occurred: {e}")
                return False
