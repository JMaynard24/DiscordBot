from RPGFiles import Player, Enemy, Item, Location, Tech
from RPGFiles.lookup import PLAYER, MONSTER, ITEM
from text_formatting import chat, idchat, rpgChat, blockify, smartCapitalize
from os.path import isfile

import os
import time
import operator


RPGTestMode = True


#-------------------------------------------------------------------------------


async def startRPG(message):
    if message.author.name not in PLAYER:
        newchar = Player.Player(message.author.name)
        newchar.id = message.author.id
        newchar.discorduser = message.author
        await newchar.setPlayer()
        await newchar.save()
        await rpgChat(message, "%s has joined the game at level 1!" % message.author.name)
        await idchat(newchar.id, 'Welcome to the world of Iodra. ' +
                                 'You awake in your cell in the Prison of Hope, a name that mocks all held within its walls. ' +
                                 'Imprisoned under ostensibly false charges, you seek one thing... Escape, at all costs. ' +
                                 'It would seem fate has favored you, for a guard has misplaced his weapon nearby... ' +
                                 '("-commands" for help! "-imstuck" if you get stuck!)')
    else:
        await idchat(PLAYER[message.author.name].id, "You are already in the game!")


#-------------------------------------------------------------------------------


async def initializeGame():
    await loadItems("RPGFiles/Items")
    await loadTech("RPGFiles/Tech")
    await loadLocations("RPGFiles/Locations")
    for user in os.listdir('RPGFiles/Players'):
        if user == 'Deleted':
            continue
        user = user[:-4]
        loadchar = Player.Player(user)
        await loadchar.load()
    print("PLAYER: %s\n" % [k for k in PLAYER])
    print("MONSTER: %s\n" % [k for k in MONSTER])
    print("ITEM: %s\n" % [k for k in Item.ITEM])
    print("TECH: %s\n" % [k for k in Tech.TECH])
    print("LOCATION: %s\n" % [k for k in Location.LOCATION])


#-------------------------------------------------------------------------------


async def leaderBoards(board, message):
    global leaderboardtimer
    newlist = {}
    badboard = False
    for player in PLAYER:
        if board == 'level':
            newlist[player] = PLAYER[player].level
        elif board == 'life':
            newlist[player] = PLAYER[player].maxlife
        elif board == 'mana':
            newlist[player] = PLAYER[player].maxmana
        elif board == 'focus':
            newlist[player] = PLAYER[player].maxfocus
        elif board == 'vigor':
            newlist[player] = PLAYER[player].vigor
        elif board == 'power':
            newlist[player] = PLAYER[player].power
        elif board == 'finesse':
            newlist[player] = PLAYER[player].finesse
        elif board == 'will':
            newlist[player] = PLAYER[player].will
        elif board == 'guard':
            newlist[player] = PLAYER[player].guard
        elif board == 'magic':
            newlist[player] = PLAYER[player].magic
        elif board == 'speed':
            newlist[player] = PLAYER[player].speed
        elif board == 'luck':
            newlist[player] = PLAYER[player].luck
        elif board == 'ides':
            newlist[player] = PLAYER[player].money
        elif board == 'kills':
            newlist[player] = PLAYER[player].kills
        elif board == 'deaths':
            newlist[player] = PLAYER[player].deaths
        elif board == 'timeouts':
            newlist[player] = PLAYER[player].timeouts
        elif board == 'runaways':
            newlist[player] = PLAYER[player].runaway
        elif board == 'killstreak':
            newlist[player] = PLAYER[player].killstreak
        else:
            await chat(message, "Leaderboards for that stat do not exist!")
            badboard = True
            break
    sortedlist = sorted(newlist.items(), key=operator.itemgetter(1))
    sortedlist.reverse()
    while len(sortedlist) < 5:
        sortedlist.append('No Data')
    if badboard is False:
        leaderboardtimer = time.time()
        await chat(message, blockify(("Top 5 players in %s are:\n" % board.title()) +
                                     ("1. %s\n" % (leaderBoardsSorting(sortedlist[0]))) +
                                     ("2. %s\n" % (leaderBoardsSorting(sortedlist[1]))) +
                                     ("3. %s\n" % (leaderBoardsSorting(sortedlist[2]))) +
                                     ("4. %s\n" % (leaderBoardsSorting(sortedlist[3]))) +
                                     ("5. %s" % (leaderBoardsSorting(sortedlist[4])))))


#-------------------------------------------------------------------------------


def leaderBoardsSorting(listtuple):
    string = ''
    for i in listtuple:
        if listtuple == 'No Data':
            string = 'No Data'
            continue
        else:
            if string.find(',') >= 0:
                string += str(i)
            else:
                string += (str(i) + ', ')
    return string


#-------------------------------------------------------------------------------


async def raidlobby(message, boss):
    await chat(message, "Raid Boss %s has come to fight! Use '-joinraid' to get ready to enter the battle!" % (boss))
    joinlist = []
    starttimer = time.time()
    warning1 = False
    warning2 = False
    warning3 = False
    lobby = True
    while lobby is True:
        for player in PLAYER:
            if PLAYER[player].lastmessage == '-joinraid':
                if PLAYER[player].inencounter is False:
                    if PLAYER[player] not in joinlist:
                        joinlist.append(PLAYER[player])
                        await chat(message, "You have joined the list to fight %s! You can leave with -leaveraid." % (boss))
                        PLAYER[player].lastmessage = ''
                        print(joinlist)
                    else:
                        await chat(message, "You are already in the list!")
                        PLAYER[player].lastmessage = ''
                else:
                    await chat(message, "You are already in an encounter!")
                    PLAYER[player].lastmessage = ''
            elif PLAYER[player] in joinlist and PLAYER[player].lastmessage == '-leaveraid':
                joinlist.remove(PLAYER[player])
                await chat(message, "You have left the list to fight %s..." % (boss))
                PLAYER[player].lastmessage = ''
                print(joinlist)
        if time.time() - 30 > starttimer and warning1 is False:
            await chat(message, "5 minutes left to join %s fight! Current # of players: %s" % (boss, len(joinlist)))
            warning1 = True
        if time.time() - 42 > starttimer and warning2 is False:
            await chat(message, "3 minutes left to join %s fight! Current # of players: %s" % (boss, len(joinlist)))
            warning2 = True
        if time.time() - 54 > starttimer and warning3 is False:
            await chat(message, "1 minute left to join %s fight! Current # of players: %s" % (boss, len(joinlist)))
            warning3 = True
        if time.time() - 60 > starttimer:
            await chat(message, "Time's up! The encounter with %s has begun!" % (boss))
            if len(joinlist) > 0:
                # await encounter(joinlist, message, False, Encounter.RAID, boss, False)
                lobby = False
            else:
                await chat(message, "Nobody showed up so %s got bored and left..." % (boss))
                lobby = False


#-------------------------------------------------------------------------------


async def pvplobby(message):
    await chat(message, "PvP Lobby Opened! Use -joinpvp to join!")
    joinlist = []
    lobby = True
    while lobby is True:
        for player in PLAYER:
            if PLAYER[player].lastmessage == '-joinpvp':
                if PLAYER[player].inencounter is False:
                    if PLAYER[player] not in joinlist:
                        joinlist.append(PLAYER[player])
                        await chat(message, "PvP Lobby %s/2" % (len(joinlist)))
                        PLAYER[player].lastmessage = ''
                        print(joinlist)
                    else:
                        await chat(message, "You are already in the lobby!")
                        PLAYER[player].lastmessage = ''
                else:
                    await chat(message, "You are already in an encounter!")
                    PLAYER[player].lastmessage = ''
            if len(joinlist) == 2:
                # await encounter(joinlist, message, False, Encounter.PVP, '', False)
                lobby = False


#-------------------------------------------------------------------------------


async def loadLocations(folder):
    for filename in os.listdir(folder):
        if filename == "WIP":
            continue
        fileobj = open("RPGFiles/Locations/%s" % filename)
        data = fileobj.readlines()
        fileobj.close()
        location = Location.Location(filename[:-4])
        loadEnemies = False
        currentEnemy = None
        for line in data:
            if line.strip() == '':
                continue
            elif line.strip() == 'ENEMYLIST':
                loadEnemies = True
                continue
            parsed = line.split(': ', 1)
            if loadEnemies and parsed[0] == 'name':
                name = eval(parsed[1])
                currentEnemy = Enemy.Enemy(name)
                await currentEnemy.setMonster()
            elif '.' in parsed[0]:
                attr, key = tuple(parsed[0].split('.', 1))
                val = parsed[1]
                if loadEnemies:
                    dct = getattr(currentEnemy, attr)
                else:
                    dct = getattr(location, attr)
                dct[key] = eval(val)
            elif parsed[0][-1] == '+':
                attr = parsed[0][:-1]
                val = parsed[1]
                lst = getattr(location, attr)
                lst.append(eval(val))
            else:
                attr = parsed[0]
                val = parsed[1]
                if loadEnemies:
                    setattr(currentEnemy, attr, eval(val))
                else:
                    setattr(location, attr, eval(val))


#-------------------------------------------------------------------------------


async def loadItems(folder):
    for filename in os.listdir(folder):
        if filename == "WIP":
            continue
        fileobj = open("RPGFiles/Items/%s" % filename)
        data = fileobj .readlines()
        fileobj .close()
        currentItem = None
        for line in data:
            if line.strip() == '':
                continue
            parsed = line.split(': ', 1)
            if parsed[0] == 'name':
                name = eval(parsed[1])
                currentItem = Item.Item(name)
                currentItem.typeof = filename[:-4]
            elif '.' in parsed[0]:
                attr, key = tuple(parsed[0].split('.', 1))
                val = parsed[1]
                dct = getattr(currentItem, attr)
                dct[key] = eval(val)
            else:
                attr = parsed[0]
                val = parsed[1]
                setattr(currentItem, attr, eval(val))
    for item in ITEM:
        if isfile("RPGFiles/Art/Icons/%s.png" % smartCapitalize(item)):
            ITEM[item].image = "RPGFiles/Art/Icons/%s.png" % smartCapitalize(item)


#-------------------------------------------------------------------------------


async def loadTech(folder):
    for filename in os.listdir(folder):
        if filename == "WIP":
            continue
        fileobj = open("RPGFiles/Tech/%s" % filename)
        data = fileobj.readlines()
        fileobj.close()
        currentItem = None
        for line in data:
            if line.strip() == '':
                continue
            parsed = line.split(': ', 1)
            if parsed[0] == 'name':
                name = eval(parsed[1])
                currentItem = Tech.Tech(name)
                currentItem.typeof = filename[:-4]
            elif '.' in parsed[0]:
                attr, key = tuple(parsed[0].split('.', 1))
                val = parsed[1]
                dct = getattr(currentItem, attr)
                dct[key] = eval(val)
            else:
                attr = parsed[0]
                val = parsed[1]
                setattr(currentItem, attr, eval(val))


#-------------------------------------------------------------------------------


rpgSymbol = "-"
rpgCommands = ['examine ', 'use ', 'shop', 'trainer', 'travel', 'location', 'loc', 'commands', 'cmds', 'travel ',
               'surroundings', 'look', 'stats', 'inv', 'discard ', 'equip ',
               'meditate ', 'concentrate ', 'med ', 'con ', 'imstuck', 'enc', 'enc boss']


#-------------------------------------------------------------------------------


async def handleCommand(message):
    content = message.content.lower()
    if message.content == "-joinRPG":
        await startRPG(message)
        return
    elif message.content == "-lbs" or message.content == "-leaderboards":
        board = message.content[5:].lower()
        await chat(message, blockify("Choices:\n  level\n  life\n  mana\n  focus\n  vigor\n  power\n  finesse\n  will\n  guard\n  " +
                                     "magic\n  speed\n  luck\n  ides\n  kills\n  deaths\n  timeouts\n  runaways\n  killstreak\n"))
        return
    elif message.content[:5] == "-lbs " or message.content[:14] == "-leaderboards ":
        split = message.content.split(' ')
        board = split[1]
        await leaderBoards(board, message)
        return
    if message.author.name in PLAYER:
        if PLAYER[message.author.name].id == -1:
            PLAYER[message.author.name].id = message.author.id
        if PLAYER[message.author.name].id == message.author.id:
            if message.channel != '':
                PLAYER[message.author.name].lastchannel = str(message.channel)
            PLAYER[message.author.name].lastmessage = content
            for text in rpgCommands:
                text = rpgSymbol + text
                if message.content.find(text) != -1:
                    await PLAYER[message.author.name].handleCharacterCommand(RPGTestMode)
                    return
        else:
            await chat(message, ("You do not own %s!" % PLAYER[message.author.name].name))


#-------------------------------------------------------------------------------
