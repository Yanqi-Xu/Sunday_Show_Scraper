import requests, mechanize, csv
from bs4 import BeautifulSoup
from dateutil import rrule
from datetime import date, timedelta, datetime
import re

def new_program_date():
	"""Get the most recent program date as a date"""
	start_date = date(2019, 2, 3)
	end_date = date.today()
    # Get the date of the most recent Sunday 
	program_dates = list(rrule.rrule(rrule.WEEKLY, dtstart = start_date, until = end_date))
	return	program_dates[-1]

# Make 2019 3 10 into march-10-2019
this_date = new_program_date().strftime('%B %d %y')
this_date_num= new_program_date().strftime('%y %m %d')
x = re.split('\s', this_date)
y = re.split('\s', this_date_num)
url_date = x[0].format()+'-'+x[1].format()+'-20'+x[2].format()

def new_program_date():
	"""Get the most recent program date as a date"""
	start_date = date(2019, 2, 3)
	end_date = date.today()
    # Get the date of the most recent Sunday 
	program_dates = list(rrule.rrule(rrule.WEEKLY, dtstart = start_date, until = end_date))
	return	program_dates[-1]

def visit(url):
	"""Visit a page and return a Beautiful Soup Object"""
	br = mechanize.Browser()
	br.open(url)
	html_child = br.response().read()
	return BeautifulSoup(html_child, 'html.parser')

def rough_cbs():
	# Append the newest program date to the URL
	base_url_cbs = 'https://www.cbsnews.com/news/full-transcript-of-face-the-nation-on-'
	# url_cbs = base_url_cbs + url_date
	url_cbs = base_url_cbs + url_date
	transcript_cbs = visit(url_cbs).find('div', {'class':'entry'}). findAll('p')
	transcript_cbs = transcript_cbs[2:len(transcript_cbs)]
	return str(transcript_cbs).replace('<p>', '\n').replace('</p>,','\n').replace('\u2019','\'').replace('\\xe0','a').replace('[','').replace(']','')

file = open('Sunday_Shows_Scraper/cbs'+new_program_date().strftime('%m%d%y')+'.txt',"w")
file.write(rough_cbs())

def rough_nbc():
	"""Go to the Meet the Press transcript page, Get the rough text"""
	parent_url_nbc = 'https://www.nbcnews.com/meet-the-press/meet-press-transcripts-n51976'
	url_nbc = visit(parent_url_nbc).find('p').find('a').get('href')
	transcript_nbc = visit(url_nbc).findAll('p', {'class':''})
	return str(transcript_nbc).replace(', <p class=\"\">', '\n').replace('</p>','\n').replace('<p class=""','')

file = open('Sunday_Shows_Scraper/nbc'+new_program_date().strftime('%m%d%y')+'.txt',"w")
file.write(rough_nbc())

def rough_cnn():
	url_cnn = 'http://www.cnn.com/TRANSCRIPTS/'+y[0].format()+y[1].format()+'/'+ y[2].format()+'/sotu.01.html'
	transcript_sotu = visit(url_cnn).findAll('p', {'class':'cnnBodyText'})[-1]
	return str(transcript_sotu).replace('<br>','\n').replace('<br/>','\n')


file = open('Sunday_Shows_Scraper/sotu'+new_program_date().strftime('%m%d%y')+'.txt',"w")
file.write(rough_cnn())

# Here comes ABC
def rough_abc():
	parent_url_abc = 'https://abcnews.go.com/Politics/week-transcript-archive/story?id=16614108'
	# Get the ahref attribute of the first tag that contains 'Full Transcript'
	url_abc = visit(parent_url_abc).find('p', text = re.compile('Full Transcript')).find('a').get('href')
	transcript_abc = visit(url_abc).findAll('p')[2:]
	return str(transcript_abc).replace('<p>\\n','\n').replace('\\n</p>,', '\n').replace('\\u2026','...').replace('\\u2013','--').replace('\\u2019','\'')

file = open('Sunday_Shows_Scraper/abc'+new_program_date().strftime('%m%d%y')+'.txt',"w")
file.write(rough_abc())

# Let's get Fox
def rough_fox():
	parent_url_fox = 'https://www.foxnews.com/category/shows/fox-news-sunday'
	# Get the ahref attribute of the first h4 tag 
	url_fox = "http://www.foxnews.com/" + visit(parent_url_fox).find('h4').find('a').get('href')
	transcript_fox = visit(url_fox).find('div', {'class':'article-body'}).findAll('p')[2:-1]
	return str(transcript_fox).replace('&amp;apos', "'").replace('<p>', '\n').replace('</p>,','\n').replace('\u201c','\"').replace('\u2019','\'').replace('<p class="speakable">','')


file = open('Sunday_Shows_Scraper/fox'+new_program_date().strftime('%m%d%y')+'.txt',"w")
file.write(rough_fox())
