from bs4 import BeautifulSoup
import requests
from scrapecard import GetCardInfo
import csv

#url = 'http://ufcstats.com/statistics/events/completed'
url = 'http://ufcstats.com/statistics/events/completed?page=all'
source = requests.get(url).text

soup = BeautifulSoup(source, 'lxml')
body = soup.tbody

#Find the table with all the fight cards
tableRows = body.find_all('tr', class_='b-statistics__table-row')

csv_file = open('fight_card_info.csv', 'w', newline='')

csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Title', 'Date', 'Location', 'Link'])

#skip the empty rows and pass the links for each fight card to GetCardInfo()
for fightCard in tableRows:
    if fightCard.text.isspace()==True: continue

    link = fightCard.a.get('href', None)
    cardInfo = GetCardInfo(link)
    print(cardInfo)

    csv_writer.writerow([cardInfo['Title'], cardInfo['Date'], cardInfo['Location'], link])

csv_file.close()
