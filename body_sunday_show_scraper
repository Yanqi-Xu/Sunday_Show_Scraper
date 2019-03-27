import requests, mechanize, csv
from bs4 import BeautifulSoup
from dateutil import rrule
from datetime import date, timedelta, datetime
import re

# Fix time
# Set time in url
start_date = date(2019, 2, 3)
end_date = date.today()

# Get the date of the most recent Sunday 
program_dates = list(rrule.rrule(rrule.WEEKLY, dtstart = start_date, until = end_date))
newest_cbs_program = program_dates[-1]

# Make 2019 3 10 into march-10-2019
this_date = newest_cbs_program.strftime('%B %d %y')
this_date_num= newest_cbs_program.strftime('%y %m %d')
x = re.split('\s', this_date)
y = re.split('\s', this_date_num)
url_date = x[0].format()+'-'+x[1].format()+'-20'+x[2].format()
# Append the newest program date to the URL
base_url_cbs = 'https://www.cbsnews.com/news/full-transcript-of-face-the-nation-on-'
# url_cbs = base_url_cbs + url_date
url_cbs = base_url_cbs + url_date

# Scrape the body of the show
br = mechanize.Browser()
br.open(url_cbs)
html = br.response().read()
# Turn into Beautiful Soup Object
soup = BeautifulSoup(html, "html.parser")

transcript_cbs = soup.find('div', {'class':'entry'}). findAll('p')
transcript_cbs = transcript_cbs[2:len(transcript_cbs)]

def rough_text(t):
	 return str(t).replace('<p>', '\n').replace('</p>,','\n').replace('\u2019','\'').replace('[','').replace(']','')

file = open('Sunday_Shows_Scraper/cbs'+datetime.date(newest_cbs_program).strftime('%m%d%y')+'.txt',"w")
file.write(rough_text(transcript_cbs))

parent_url_nbc = 'https://www.nbcnews.com/meet-the-press/meet-press-transcripts-n51976'
br.open(parent_url_nbc)
html_nbc_parent = br.response().read()

nbc_soup = BeautifulSoup(html_nbc_parent, 'html.parser')
# Get the url of the in the a href tag
url_nbc = nbc_soup.find('p').find('a').get('href')

br.open(url_nbc)
html_nbc_child = br.response().read()
nbc_show_soup = BeautifulSoup(html_nbc_child, 'html.parser')

transcript_nbc = nbc_show_soup.findAll('p', {'class':''})
def nbc_rough(t):
	return str(t).replace(', <p class=\"\">', '\n').replace('</p>','\n')

file = open('Sunday_Shows_Scraper/nbc'+datetime.date(newest_cbs_program).strftime('%m%d%y')+'.txt',"w")
file.write(nbc_rough(transcript_nbc))

url_cnn = 'http://www.cnn.com/TRANSCRIPTS/'+y[0].format()+y[1].format()+'/'+ y[2].format()+'/sotu.01.html'
br.open(url_cnn)
html_sotu=br.response().read()

cnn_soup = BeautifulSoup(html_sotu, 'html.parser')
transcript_sotu = cnn_soup.findAll('p', {'class':'cnnBodyText'})[-1]

file = open('Sunday_Shows_Scraper/sotu'+datetime.date(newest_cbs_program).strftime('%m%d%y')+'.txt',"w")
file.write(str(transcript_sotu).replace('<br>','\n').replace('<br/>','\n'))

# Here comes ABC
parent_url_abc = 'https://abcnews.go.com/Politics/week-transcript-archive/story?id=16614108'
br.open(parent_url_abc)
html_abc_parent = br.response().read()

abc_soup = BeautifulSoup(html_abc_parent, 'html.parser')
# Get the ahref attribute of the first tag that contains 'Full Transcript'
url_abc = abc_soup.find('p', text = re.compile('Full Transcript')).find('a').get('href')

br.open(url_abc)
html_abc_child = br.response().read()
abc_show_soup = BeautifulSoup(html_abc_child, 'html.parser')

transcript_abc = abc_show_soup.findAll('p')[2:]
file = open('Sunday_Shows_Scraper/abc'+datetime.date(newest_cbs_program).strftime('%m%d%y')+'.txt',"w")
file.write(str(transcript_abc).replace('<p>\\n','\n').replace('\\n</p>,', '\n')
	.replace('\\u2026','...').replace('\\u2013','--').replace('\\u2019','\''))

# Let's get Fox
parent_url_fox = 'https://www.foxnews.com/category/shows/fox-news-sunday'
br.open(parent_url_fox)
html_fox_parent = br.response().read()

fox_soup = BeautifulSoup(html_fox_parent, 'html.parser')
# Get the ahref attribute of the first h4 tag 
url_fox = "http://www.foxnews.com/" + fox_soup.find('h4').find('a').get('href')

br.open(url_fox)
html_fox_child = br.response().read()
fox_show_soup = BeautifulSoup(html_fox_child, 'html.parser')
transcript_fox = fox_show_soup.find('div', {'class':'article-body'}).findAll('p')[2:-1]

def rough_fox(t):
	str(t).replace('&amp;apos', '\'').replace('\u201c','\"').replace('\u2019','\'').replace('<p class="speakable">','')

file = open('Sunday_Shows_Scraper/fox'+datetime.date(newest_cbs_program).strftime('%m%d%y')+'.txt',"w")
file.write(rough_text(transcript_fox))
