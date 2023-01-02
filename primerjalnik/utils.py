import os, socket, logging, requests
from apiflask import APIFlask, Schema, abort
from apiflask.fields import Integer, String, Boolean
from apiflask.validators import Length, OneOf
from bs4 import BeautifulSoup

LOGSTASH_IP = str(os.environ["LOGSTASH_IP"])
LOGSTASH_PORT = int(os.environ["LOGSTASH_PORT"])

class LogHandler(logging.Handler):
    def emit(self, record):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(bytes(self.format(record), "utf-8"), (LOGSTASH_IP, LOGSTASH_PORT))
        except:
            pass

class ProductIn(Schema):
    searched_product = String()
    store = String()

class ProductsOut(Schema):
    id = Integer()
    img_link = String()
    link = String()
    price = String()
    store_img = String()
    title = String()

class LiveOut(Schema):
    live = Boolean()

class ReadyOut(Schema):
    ready = Boolean()

def get_info(product, limit=300): 
    url = 'https://sl.wikipedia.org/w/api.php'
    params = {
                'action': 'parse',
                'page': product,
                'format': 'json',
                'prop':'text',
                'redirects':''
            }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        raw_html = data['parse']['text']['*']
        soup = BeautifulSoup(raw_html,'html.parser')
        soup.find_all('p')
        text = ''
        
        for p in soup.find_all('p'):
            text += p.text
        return text[:limit]
    
    except:
        try:
            url = 'https://en.wikipedia.org/w/api.php'
            response = requests.get(url, params=params)
            data = response.json()

            raw_html = data['parse']['text']['*']
            soup = BeautifulSoup(raw_html,'html.parser')
            soup.find_all('p')
            text = ''
            
            for p in soup.find_all('p'):
                text += p.text
            return text[:limit]
        except:
            return ""