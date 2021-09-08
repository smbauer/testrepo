import  requests
from bs4 import BeautifulSoup
from scrapefighter import GetFighterInfo

#break up strikes, tds (x of y) into (landed,attempted)
def ParseStats(statsList):
    tempList = []

    #might be able to improve things with list comprehension or try/except
    for piece in statsList:
        if ' of ' not in piece:
            tempList.append(piece)
        else:
            piece = piece.split(' of ')
            tempList.append(piece[0])
            tempList.append(piece[1])

    statsList = tempList

    return statsList

#hard code url for testing, eventually pass in function or something
url = 'http://ufcstats.com/fight-details/7de9867b7cc2b1b1'
source = requests.get(url).text

soup = BeautifulSoup(source, 'lxml')

#select the section with the participant info
person = soup.find_all('div', class_='b-fight-details__person')

######################
# should probably create a class for fighter
#########################

fighterA = {}
fighterB = {}

#parse the participant info to get the name, result and link to their page
#### repetitive, feels like i can probably write some sort of loop for this part?
fighterA['result'] = person[0].i.text.strip()
fighterA['name'] = person[0].a.text.strip()
fighterA['link'] = person[0].a.get('href', None)

fighterB['result'] = person[1].i.text.strip()
fighterB['name'] = person[1].a.text.strip()
fighterB['link'] = person[1].a.get('href', None)

############
fighterA['info'] = GetFighterInfo(fighterA['link'])
fighterB['info'] = GetFighterInfo(fighterB['link'])
############

#figure out who the winner was
if fighterA['result'] == 'W':
    winner = fighterA['name']
elif fighterB['result'] == 'W':
    winner = fighterB['name']
elif fighterA['result'] == 'D':
    winner = 'Draw'
else:
    winner = 'No Contest'

#print('Fighter A:', fighterA['name'])
#print('Fighter B:', fighterB['name'])
#print('Winner:', winner)

#search the fight description to see if this is a title fight
description = soup.select('.b-fight-details__fight-head')[0].text

#print(description.strip())

if 'Title' in description:
    titleFight = 'Y'
else:
    titleFight = 'N'

#print('Title Fight?', titleFight)

#get fight details
content = soup.find('div', class_='b-fight-details__content')
content = content.text.splitlines()

details = []
for part in content:
    if part.strip() == '' : continue
    details.append(part.strip())

method = details[1]
round = int(details[3])
time = details[5]
#not sure if i should store this part or just #rounds (earlier fights have diff format)
format = details[7].split()
fightLength = int(format[0])
ref = details[9]
fightDetails = ' '.join(details[11:])

#print('Method of Victory: ', method)
#print('Round: ', round)
#print('Time: ', time)
#print('Scheduled Length: ', fightLength)
#print('Referee: ', ref)
#print('Details: ', fightDetails)

######################
# have all the info for the Fight table, can insert/update here
#######################

#get all the tables with the fight stats
tableList = soup.find_all('tbody')

tempTables = []
start = 0
tableNum = 0

#clean up each of the tables
for table in tableList:
    table = table.text.splitlines()
    for part in table:
        if part.strip() == '' : continue
        tempTables.append(part.strip())
    end = len(tempTables)
    tableList[tableNum] = tempTables[start:end]
    start = end
    tableNum += 1

#separate into individual tables so it's easier to work with
basicTable = tableList[0]       #basic stats summary
basicRoundsTable = tableList[1] #basic stats by round
ssTable = tableList[2]          #sig strikes breakdown
ssRoundsTable = tableList[3]    #sig strikes breakdown by round

#split basicTable into stats for each fighter
####should turn this into a loop when i change fighterA/B into [0]/[1]
fighterA['basicStatsFor'] = ParseStats(basicTable[0::2])
fighterB['basicStatsFor'] = ParseStats(basicTable[1::2])

#print('Fighter 1: ', fighterA['basicStatsFor'])
#print('Fighter 2: ', fighterB['basicStatsFor'])

fighterA['advStrStatsFor'] = ParseStats(ssTable[0::2])
fighterB['advStrStatsFor'] = ParseStats(ssTable[1::2])

#print('Fighter 1: ', fighterA['advStrStatsFor'])
#print('Fighter 2: ', fighterB['advStrStatsFor'])

fighterA['basicStatsAgainst'] = fighterB['basicStatsFor']
fighterB['basicStatsAgainst'] = fighterA['basicStatsFor']
fighterA['advStrStatsAgainst'] = fighterB['advStrStatsFor']
fighterB['advStrStatsAgainst'] = fighterA['advStrStatsFor']
