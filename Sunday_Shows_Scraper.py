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
    return    program_dates[-1]

# Make 2019 3 10 into march-10-2019
this_date = new_program_date().strftime('%B %d %y')
this_date_num= new_program_date().strftime('%y %m %d')
db_date = new_program_date().strftime("%Y-%m-%d")
#print(db_date)
x = re.split('\s', this_date)
y = re.split('\s', this_date_num)


def new_program_date():
    """Get the most recent program date as a date"""
    start_date = date(2019, 2, 3)
    end_date = date.today()
    # Get the date of the most recent Sunday
    program_dates = list(rrule.rrule(rrule.WEEKLY, dtstart = start_date, until = end_date))
    return    program_dates[-1]

def visit(url):
    """Visit a page and return a Beautiful Soup Object"""
    br = mechanize.Browser()
    br.open(url)
    html_child = br.response().read()
    return BeautifulSoup(html_child, 'html.parser')

def rough_cbs():
    """Get the rough text of Face the Nation"""
    # Append the newest program date to the URL
    base_url_cbs = 'https://www.cbsnews.com/news/full-transcript-of-face-the-nation-on-'
    url_date = x[0].format()+'-'+x[1].format().strip('0')+'-20'+x[2].format()
    global url_cbs
    url_cbs = base_url_cbs + url_date
    transcript_cbs = visit(url_cbs).find('div', {'class':'entry'}). findAll('p')
    transcript_cbs = transcript_cbs[2:len(transcript_cbs)]
    return str(transcript_cbs).replace('<p>', '\n').replace('</p>,','\n').replace('\\u2019','\'').replace('\\xe0','a').replace('[','').replace(']','')

def rough_nbc():
    """Go to the Meet the Press transcript page, Get the rough text"""
    parent_url_nbc = 'https://www.nbcnews.com/meet-the-press/meet-press-transcripts-n51976'
    global url_nbc 
    url_nbc = visit(parent_url_nbc).find('p').find('a').get('href')
    transcript_nbc = visit(url_nbc).findAll('p', {'class':''})
    return str(transcript_nbc).replace(', <p class=\"\">', '\n').replace('</p>','\n').replace('<p class=""','')

def rough_cnn():
        global url_cnn
        url_cnn = 'http://www.cnn.com/TRANSCRIPTS/'+y[0].format()+y[1].format()+'/'+ y[2].format()+'/sotu.01.html'
        transcript_sotu = visit(url_cnn).findAll('p', {'class':'cnnBodyText'})[-1]
        return str(transcript_sotu).replace('<br>','\n').replace('<br/>','\n')

def rough_abc():
    parent_url_abc = 'https://abcnews.go.com/Politics/week-transcript-archive/story?id=16614108'
    # Get the ahref attribute of the first tag that contains 'Full Transcript'
    global url_abc
    url_abc = visit(parent_url_abc).find('p', text = re.compile('Full Transcript')).find('a').get('href')
    transcript_abc = visit(url_abc).findAll('p')[2:]
    return str(transcript_abc).replace('</p>, <p>','')

# Let's get Fox
def rough_fox():
    parent_url_fox = 'https://www.foxnews.com/category/shows/fox-news-sunday'
    # Get the ahref attribute of the first h4 tag
    global url_fox
    url_fox = "http://www.foxnews.com/" + visit(parent_url_fox).find('h4').find('a').get('href')
    transcript_fox = visit(url_fox).find('div', {'class':'article-body'}).findAll('p')[2:-1]
    return str(transcript_fox).replace('&amp;apos', "'").replace('<p>', '\n').replace('</p>,','\n').replace('\u201c','\"').replace('\u2019','\'').replace('<p class="speakable">','')

def identify_speaker(stringscript):
    """Separate speakers and their statements with Regex"""
    statements = []
    speakers = []
    global show_host
    show_host = ''
    # Clean transcript first for extraneous text
    stringscript = re.sub('REPRESENTATIVE ', '', stringscript)
    stringscript = re.sub('SENATOR ', '', stringscript)            #Face the Nation
    stringscript = re.sub('DR. ', '', stringscript)                #Face the Nation
    stringscript = re.sub('SEN. ', '', stringscript)                 #Fox, NBC, CNN
    stringscript = re.sub('REP. ', '', stringscript)
    stringscript = re.sub('PRESIDENT ', '', stringscript)
    stringscript = re.sub('VICE PRESIDENT', '', stringscript)
    stringscript = re.sub('FMR.', '', stringscript)
    stringscript = re.sub('RRES. ', '', stringscript)
    stringscript = re.sub('(INDISTINCT)', '[[INDISTINCT]]', stringscript)
    stringscript = re.sub(' \([a-zA-Z]+.*\)','', stringscript)    #clean up (ANNOUNCEMENTS), Face the Nation
    statements_list = list(re.finditer('([A-Z][A-Z].{1,110}[A-Z]?( "[a-zA-Z\s]*")?([A-Z]|"|\)):)|(SY:)', stringscript))
    for speaker_index, name in enumerate(statements_list):
        names = name.group()[0:-1]
        if ',' in names:
             names = names[:names.find(',')]
        if '. ' in names:
            names = names[names.find('. ')+1:]
        names = re.sub("^\s+|\s+$", "", names)
        if speaker_index == 0:
           show_host = names
        if speaker_index < len(statements_list)-1:
           speakers.append(names)
           this_speaker_end = name.end()
           next_speaker_start = statements_list[speaker_index+1].start()
           statement = stringscript[this_speaker_end: next_speaker_start]
           statement = statement.strip()
           statements.append(statement)
        else:
            break

    return speakers, statements

def refine_speakers(speakers):
    """ABC, FOX and CNN usually only use last names on second references, fix them"""
    speakers_unique = []
    for spkr in speakers:
        if ' ' in spkr:
            speakers_unique.append(spkr)
    speakers_unique = list(set(speakers_unique))
    for i, spkr1 in enumerate(speakers):
        for singlespeaker in speakers_unique:
            if singlespeaker.split()[-1] == spkr1:
                speakers[i] = singlespeaker
    return speakers

chunks = [refine_speakers(identify_speaker(rough_cbs())[0]),identify_speaker(rough_cbs())[1]]
speakers = chunks[0]
speaker_chunks = chunks[1]

"""for speaker, chunk in zip(speakers,chunks):
    print(speaker,':', chunk)
    print('-----------------------------------------------------------------------------------------')"""

with open('claimscbs.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
     for i,j in zip(speakers, speaker_chunks):
         writer.writerow([i,j])



