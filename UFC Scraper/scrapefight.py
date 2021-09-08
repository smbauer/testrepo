import  requests
from bs4 import BeautifulSoup
from scrapefighter import GetFighterInfo
import sqlite3

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

def GetFightInfo(fightInfo):
    #hard code url for testing, eventually pass in function or something
    #url = 'http://ufcstats.com/fight-details/7de9867b7cc2b1b1'
    source = requests.get(fightInfo['link']).text

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
#    fighterA['info'] = GetFighterInfo(fighterA)
#    fighterB['info'] = GetFighterInfo(fighterB)
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

#    print('Fighter A:', fighterA['name'])
#    print('Fighter B:', fighterB['name'])
#    print('Winner:', winner)

    #search the fight description to see if this is a title fight
    description = soup.select('.b-fight-details__fight-head')[0].text

    #print(description.strip())

    if 'Title' in description:
        titleFight = 1
    else:
        titleFight = 0

    #print('Title Fight?', titleFight)

    #get fight details
#    content = soup.find('div', class_='b-fight-details__content')
    contentParts = soup.find_all('p', class_='b-fight-details__text')
    firstParts = contentParts[0].select('p > i')
    secondPart = contentParts[1].text.split()

    method = firstParts[0].text.split()
    fightInfo['method'] = ' '.join(method[1:len(method)])

    round = firstParts[1].text.split()
    fightInfo['round'] = int(round[1])

    time = firstParts[2].text.split()
    fightInfo['time'] = time[1]

    format = firstParts[3].text.split()
    fightInfo['format'] = ' '.join(format[1:len(format)])
    fightInfo['fightLength'] = int(format[2])

    referee = firstParts[4].text.split()
    fightInfo['referee'] = ' '.join(referee[1:len(referee)])

    fightInfo['details'] = ' '.join(secondPart[1:len(secondPart)])

#    print(len(part1))
#    print('part1:', part1)
#    print('part2:', secondPart)

#    content = content.text.splitlines()

#    details = []
#    for part in content:
#        if part.strip() == '' : continue
#        details.append(part.strip())

#    method = details[1]
#    round = int(details[3])
#    time = details[5]
#    #not sure if i should store this part or just #rounds (earlier fights have diff format)
#    format = details[7].split()
#    fightLength = int(format[0])
#    ref = details[9]
#    fightDetails = ' '.join(details[11:])

    print('Method of Victory: ', fightInfo['method'])
    print('Round: ', fightInfo['round'])
    print('Time: ', fightInfo['time'])
    print('Scheduled Length: ', fightInfo['fightLength'])
    print('Referee: ', fightInfo['referee'])
    print('Details: ', fightInfo['details'])

    ######################
#    cur.execute('SELECT id FROM Event WHERE name = ? ', (fightInfo['event'], ))
#    event_id = cur.fetchone()[0]

#    cur.execute('SELECT id FROM Weightclass WHERE name = ? ', (fightInfo['weightClass'], ))
#    weightclass_id = cur.fetchone()[0]

#    cur.execute('''INSERT OR IGNORE INTO Fight
#        (event_id, fight_num, weightclass_id, winner, title_fight, method, round,
#         time, time_format, details, referee, link)
#        VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )''',
#        ( event_id, fightInfo['fightNum'], weightclass_id, winner, titleFight, method,
#         round, time, format, fightDetails, referee, fightInfo['link']  ) )

#    conn.commit()
    #######################

    try:
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

        #print(ssTable)

        #split basicTable into stats for each fighter
        ####should turn this into a loop when i change fighterA/B into [0]/[1]
        fighterA['basicStatsFor'] = ParseStats(basicTable[2::2])
        fighterB['basicStatsFor'] = ParseStats(basicTable[3::2])

        fighterA['advStrStatsFor'] = ParseStats(ssTable[6::2])
        fighterB['advStrStatsFor'] = ParseStats(ssTable[7::2])

    except:
        error = soup.find('section', class_='b-fight-details__section').text.strip()
        fightInfo['details'] = error
        print('exception:', fightInfo['details'])

        fighterA['basicStatsFor'] = [None]*12
        fighterA['advStrStatsFor'] = [None]*12
        fighterB['basicStatsFor'] = [None]*12
        fighterB['advStrStatsFor'] = [None]*12


    #print('length of basic stats:', len(fighterA['basicStatsFor']))
    #print('length of adv stats:', len(fighterA['advStrStatsFor']))
    #print('Fighter 1: ', fighterA['basicStatsFor'])
    #print('Fighter 2: ', fighterB['basicStatsFor'])
    #print('Fighter 1: ', fighterA['advStrStatsFor'])
    #print('Fighter 2: ', fighterB['advStrStatsFor'])

    fighterA['basicStatsAgainst'] = fighterB['basicStatsFor']
    fighterB['basicStatsAgainst'] = fighterA['basicStatsFor']
    fighterA['advStrStatsAgainst'] = fighterB['advStrStatsFor']
    fighterB['advStrStatsAgainst'] = fighterA['advStrStatsFor']

fightInfo = {}
fightInfo['link'] = 'http://ufcstats.com/fight-details/635fbf57001897c7'
#fightInfo['link'] = 'http://ufcstats.com/fight-details/81b16b26774be5d1'
GetFightInfo(fightInfo)
