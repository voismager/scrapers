from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

def read_html(url) -> BeautifulSoup:
    with urlopen(Request(url, headers={'User-Agent': "Magic Browser"})) as resp:
        text = resp.read().decode("utf8")
        return BeautifulSoup(text, 'html.parser')