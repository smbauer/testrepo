import  requests
from bs4 import BeautifulSoup

def GetFighterInfo(url):

    source = requests.get(url).text

    soup = BeautifulSoup(source, 'lxml')

    record = soup.select('.b-content__title-record')[0].text
    record = record.split()[1]

    nickname = soup.select('.b-content__Nickname')[0].text.strip()

    basicInfo = soup.find('ul', class_='b-list__box-list').text
    basicInfo = basicInfo.splitlines()

    tempInfo = []

    for i in basicInfo:
        if i.strip() == '' : continue
        tempInfo.append(i.strip())

    fighter = {
        'nickname' : nickname,
        'record' : record,
        'height' : tempInfo[1],
        'weight' : tempInfo[3],
        'reach' : tempInfo[5],
        'stance' : tempInfo[7],
        'dob' : tempInfo[9]
        }

    return fighter
