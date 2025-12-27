import requests
from bs4 import BeautifulSoup
def url_soupper(url):
    resp=requests.get(url)
    soup=BeautifulSoup(resp.text,'html.parser')
    return soup
