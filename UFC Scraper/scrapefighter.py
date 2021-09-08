import  requests
from bs4 import BeautifulSoup

def GetFighterInfo(fighter):

    source = requests.get(fighter['link']).text

    soup = BeautifulSoup(source, 'lxml')

    fighterInfo = {}

    record = soup.select('.b-content__title-record')[0].text
    fighterInfo['record'] = record.split()[1]

    fighterInfo['nickname'] = soup.select('.b-content__Nickname')[0].text.strip()

    basicInfo = soup.find_all('li', class_='b-list__box-list-item')

    height = basicInfo[0].text.split()
    fighterInfo['height'] = ''.join(height[1:len(height)])

    weight = basicInfo[1].text.split()
    fighterInfo['weight'] = ' '.join(weight[1:len(weight)])

    reach = basicInfo[2].text.split()
    fighterInfo['reach'] = ''.join(reach[1:len(reach)])

    stance = basicInfo[3].text.split()
    fighterInfo['stance'] = ''.join(stance[1:len(stance)])

    dob = basicInfo[4].text.split()
    fighterInfo['dob'] = ' '.join(dob[1:len(dob)])

    #print(fighterInfo)

    cur.execute('''INSERT OR IGNORE INTO Fighter
        (name, nickname, height, reach, weight, stance, dob, record, link)
        VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ? )''',
        ( fighter['name'], fighterInfo['nickname'], fighterInfo['height'], fighterInfo['reach'],
        fighterInfo['weight'], fighterInfo['stance'], fighterInfo['dob'], fighterInfo['record'],
        fighter['link'] ) )

    conn.commit()

    return fighterInfo
