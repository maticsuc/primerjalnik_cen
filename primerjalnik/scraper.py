import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}

def get_store_image(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    img_src = urljoin(url, soup.find("img", {"class":"icon"})['src'])

    return img_src

def get_products(searched_product):
    base_url = "https://www.mimovrste.com/"

    img_src = get_store_image(base_url)
    
    search_url = "iskanje?s="

    for w in searched_product.split(" "):
        search_url += w + "%20"

    final_url = base_url + search_url

    page = requests.get(final_url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    found_products = soup.find_all("div", {"class":"pbcr"})

    products = dict()

    for i, product in enumerate(found_products):
        title = product.find("span", {"class":"pbcr__title"}).text.strip()
        price = product.find("span", {"class":"pbcr__price"}).text.strip()[:-2]
        link = urljoin(base_url, product.find("a", {"class":"pbcr__title-wrap pbcr__link"})['href'])
        img_link = urljoin(base_url, product.find("img", {"class":"lazyload gallery-list__image"})['src'])
        
        products[str(i)] = {"title": title, "price": price, "link": link, "img_link":img_link, "store_img": img_src}

    return products

if __name__ == '__main__':
    get_products("iphon 11")