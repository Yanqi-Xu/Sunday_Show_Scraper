import requests, mechanize
from bs4 import BeautifulSoup


br = mechanize.Browser()
parent_url_nbc = 'https://www.nbcnews.com/meet-the-press/meet-press-transcripts-n51976'
br.open(parent_url_nbc)
html_nbc = br.response().read()

nbc_soup = BeautifulSoup(html_nbc, 'html.parser')

transcript_nbc = nbc_soup.find('a', {'class':'vilynx_listened'})

clean_transcript_nbc = transcript_nbc.get_text()

print clean_transcript

