import requests, mechanize
from bs4 import BeautifulSoup

url_cbs = 'https://www.cbsnews.com/news/full-transcript-of-face-the-nation-on-february-3-2019/'

br = mechanize.Browser()
br.open(url_cbs)
html = br.response().read()

soup = BeautifulSoup(html, "html.parser")

transcript = soup.find('div', {'class':'entry'})

clean_transcript = transcript.get_text()

print clean_transcript

