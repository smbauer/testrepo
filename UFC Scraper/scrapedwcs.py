import requests
from bs4 import BeautifulSoup
import sqlite3
from scrapecard import GetCardInfo

conn = sqlite3.connect('ufcstatsdb.sqlite')
cur = conn.cursor()

cur.execute('SELECT link FROM Fighter')
flist = cur.fetchall()

count = 0
#scroll through every fighter page in the db to find dwcs fights
#i think this is the right way to read the whole query one line at a time...
for url in flist:
    if url[0] is None: continue

    source = requests.get(url[0]).text
    soup = BeautifulSoup(source, 'lxml')

    #get the list of the fights for each fighter and check each for DWCS
    fights = soup.tbody.find_all('tr', class_='b-fight-details__table-row')

    for row in fights:
        tags = row.find_all('a')
        eName = tags[3].text.strip()
        eLink = tags[3].get('href',None)

        if 'DWCS' in eName:
            cur.execute('SELECT id FROM Event WHERE link = ? ', (eLink, ))
            event_id = cur.fetchone()
            if event_id is None:
                GetCardInfo(eLink)
            else: print('card already in db')


    count +=1
    #if count == 100: break
    if count%100 == 0: print('num scraped:', count)
#print('finished DWCS scraping')

cur.close()

if conn:
    conn.close()
    print('connection closed')
