from bs4 import BeautifulSoup
import requests
import sqlite3

#Return Card Title, Date and Location
def GetCardInfo(url):
    source = requests.get(url).text

    soup = BeautifulSoup(source, 'lxml')

    #Get the Title of the card
    cardTitle = soup.find('span', class_='b-content__title-highlight').text
    cardTitle = cardTitle.strip()

    #Get the Date and Location of the card
    cardDetails = soup.find_all('li', class_='b-list__box-list-item')

    #Have to parse the text b/c of poor formatting w/ spaces and newlines
    dateInfo = cardDetails[0].text.split()
    locationInfo = cardDetails[1].text.split()

    #Remove the Date: and Location: headings from the lists
    del dateInfo[0]
    del locationInfo[0]

    #Put the Date and Location pieces back together in a string
    date = ' '.join(dateInfo)
    location = ' '.join(locationInfo)

    #Loop through list of fights and get the links, weight class and #fights
    tableRows = soup.tbody.find_all('tr', class_='b-fight-details__table-row')

    totalFights = len(tableRows)

    cur.execute('''INSERT OR IGNORE INTO Event
        (name, date, location, num_fights, link)
        VALUES ( ?, ?, ?, ?, ? )''',
        ( cardTitle, date, location, totalFights, url ) )

    conn.commit()

    for fight in tableRows:
        #get links
        link = fight.get('data-link',None)

        #find the weight class for each fight
        columnList = fight.find_all('td')
        weightClass = columnList[6].text.strip()

        #**********************************************
        #*********call scrapefight() function around here
        #**********************************************

    cardInfo = {'Title': cardTitle, 'Date': date, 'Location': location, 'TotalFights': totalFights}

    return cardInfo

conn = sqlite3.connect('ufcstatsdb.sqlite')
cur = conn.cursor()

# Make some fresh tables using executescript()
cur.executescript('''
DROP TABLE IF EXISTS Event;

CREATE TABLE Event (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE,
    date    TEXT,
    location TEXT,
    num_fights INTEGER,
    link    TEXT UNIQUE
);
''')

#url = 'http://ufcstats.com/event-details/6e2b1d631832921d'

#cardInfo = GetCardInfo(url)

url = 'http://ufcstats.com/statistics/events/completed'
#url = 'http://ufcstats.com/statistics/events/completed?page=all'
source = requests.get(url).text

soup = BeautifulSoup(source, 'lxml')
body = soup.tbody

#Find the table with all the fight cards
tableRows = body.find_all('tr', class_='b-statistics__table-row')

#skip the empty rows and pass the links for each fight card to GetCardInfo()
for fightCard in tableRows:
    if fightCard.text.isspace()==True: continue

    link = fightCard.a.get('href', None)
    cardInfo = GetCardInfo(link)

    print("Title:", cardInfo['Title'])
    print("Date:", cardInfo['Date'])
    print("Location:", cardInfo['Location'])
    print("Number of Fights:", cardInfo['TotalFights'])
    print("Link:", url)
    print()
