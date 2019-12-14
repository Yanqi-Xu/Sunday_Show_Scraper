import requests, mechanize, csv, operator, gspread,re
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup
from dateutil import rrule
from datetime import date, timedelta, datetime
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('Sunday Shows Scraper-a4240ab48300.json', scope)

gc = gspread.authorize(credentials)

wks1 = gc.open("Sunday Shows Claimbuster Results").sheet1


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

networks = ['abc', 'cbs','nbc','cnn','fox']

def visit(url):
    """Visit a page and return a Beautiful Soup Object"""
    br = mechanize.Browser()
    br.open(url)
    html_child = br.response().read()
    return BeautifulSoup(html_child, 'html.parser')

def link_cbs():
    """ Get the url by appending the newest program date to the URL"""
    base_url_cbs = 'https://www.cbsnews.com/news/full-transcript-of-face-the-nation-on-'
    url_date = x[0].format()+'-'+x[1].format().lstrip('0')+'-20'+x[2].format()
    url_cbs = base_url_cbs + url_date
    return url_cbs

def rough_cbs(url_cbs):
    """Get the rough text of Face the Nation"""
    transcript_cbs = visit(url_cbs).find('div', {'class':'entry'}). findAll('p')
    transcript_cbs = transcript_cbs[2:len(transcript_cbs)]
    return str(transcript_cbs).replace('<p>', '\n').replace('</p>,','\n').replace('\\u2019','\'').replace('\\xe0','a').replace('[','').replace(']','')

def link_nbc():
    """Go to the Meet the Press transcript page, Get the first link, aka the page to the most recent program."""
    parent_url_nbc = 'https://www.nbcnews.com/meet-the-press/meet-press-transcripts-n51976'
    url_nbc = visit(parent_url_nbc).find('p').find('a').get('href')
    return url_nbc
def rough_nbc(url_nbc):
    transcript_nbc = visit(url_nbc).findAll('p', {'class':'endmarkEnabled'})
    return str(transcript_nbc).replace(', <p class="endmarkEnabled">', '\n').replace('</p>','\n').replace("\\\'","'")

url_cnn = 'http://www.cnn.com/TRANSCRIPTS/'+y[0].format()+y[1].format()+'/'+ y[2].format()+'/sotu.01.html'

def rough_cnn(url_cnn):
        transcript_sotu = visit(url_cnn).findAll('p', {'class':'cnnBodyText'})[-1]
        return str(transcript_sotu).replace('<br>','\n').replace('<br/>','\n')

def link_abc():
    parent_url_abc = 'https://abcnews.go.com/Politics/week-transcript-archive/story?id=16614108'
    # Get the ahref attribute of the first tag that contains 'Full Transcript'
    url_abc = visit(parent_url_abc).find('a', text = re.compile('Full Transcript')).get('href')
    return url_abc

def rough_abc(url_abc):
    transcript_abc = visit(url_abc).findAll('p')[2:]
    return''.join(text_abc.text for text_abc in transcript_abc)

# Let's get Fox
def link_fox():
    parent_url_fox = 'https://www.foxnews.com/category/shows/fox-news-sunday'
    # Get the ahref attribute of the first h4 tag
    url_fox = str(visit(parent_url_fox).find('h4').find("a").get('href'))
    return url_fox

def rough_fox(url_fox):   
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
        # show_host speaks the first line.
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

# chunks = [refine_speakers(identify_speaker(rough_nbc())[0]),identify_speaker(rough_nbc())[1]]
# speakers = chunks[0]
# speaker_chunks = chunks[1]

def make_list(rough_network):
	chunks = []
	chunks = [refine_speakers(identify_speaker(rough_network)[0]),identify_speaker(rough_network)[1]]
	speakers = chunks[0]
	statements = chunks[1]
	return speakers, statements


"""for speaker, chunk in zip(speakers,chunks):
    print(speaker,':', chunk)
    print('-----------------------------------------------------------------------------------------')"""
# with open('claims.csv', 'w') as csvfile:
#     writer = csv.writer(csvfile)
#     for i,j in zip(speakers, speaker_chunks):
#         writer.writerow([i,j])

def submit_claimbuster(network):
    """Submit chunks of text to the Claimbuster API for scoring and store response in a dictionary """
    speakers = make_list(network.func(network.link))[0]
    statements = make_list(network.func(network.link))[1]
    all_claims_responses = []
    print('Submitting claims to Claimbuster')
    num_errors = 0
    num_claims = 0
    buster_base = 'https://idir.uta.edu/factchecker/score_text/'
    buster_end = '?format=json'

    for speaker, chunk in zip(speakers, statements):
        if speaker != show_host:
            try:
                submissionLink = buster_base+chunk+buster_end
                api_response = requests.get(submissionLink).json() # submit to API with GET request

                for statement in api_response['results']:
                    insert = {}
                    insert['speaker'] = speaker
                    insert['claim'] = statement['text'].strip()
                    insert['score'] = round(float(statement['score']),3)
                    insert['date'] = db_date
                    insert['link'] = network.link
                    insert['network'] = network.network_name + ' - ' + network.show_name
                    num_claims+=1
                    all_claims_responses.append(insert)
                    if num_claims%100 == 0:
                        print(num_claims,'claims processed')

            except Exception as e:
                print('error',e)
                num_errors+=1
    return all_claims_responses

def write_sorted(network):
  sort = sorted(submit_claimbuster(network), key = lambda row: row['score'], reverse = True)[:5]
  for i, line in enumerate(sort, start =2):
    wks1.insert_row(list(line.values()),index = i)

class Networks:
  def __init__(self,network_name, show_name, link, func):
      self.network_name = network_name
      self.show_name = show_name
      self.link = link
      self.func = func
      self.run = write_sorted(self)

if __name__ == '__main__':
    fox = Networks('Fox', 'Fox News Sunday',link_fox(), rough_fox)
    cnn = Networks('CNN', 'State of the Union', url_cnn, rough_cnn)
    abc = Networks('ABC', 'This Week', link_abc(), rough_abc)
    nbc = Networks('NBC', 'Meet the Press', link_nbc(), rough_nbc)
    cbs = Networks('CBS', 'Face the Nation', link_cbs(), rough_cbs)
# with open('Sunday_Shows_Scraper/claimsnbc0902.csv', 'w') as csvfile:
#     writer = csv.DictWriter(csvfile, fields)
#     writer.writeheader()
#     writer.writerows(sort[:10])

# def write_sorted(rough_network):
# 	claimbust_dicts = submit_claimbuster(make_list(rough_network)[0], make_list(rough_network)[1])
# 	fields = claimbust_dicts[0].keys()
# 	sort = sorted(claimbust_dicts, key = lambda row: row['score'], reverse = True)[:4]
# 	for i, line in enumerate(sort, start =2):
#     wks1.insert_row(list(line.values()),index = i)

# rough_network = [rough_abc, rough_cbs, rough_nbc, rough_cnn, rough_fox]
# if __name__ = '__main__': 
# 	for item in rough_network:
# 		write_sorted(item)
