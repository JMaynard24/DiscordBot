from RPGFiles import Character, Item, Location, Tech
from RPGFiles.lookup import PLAYER, MONSTER, LOCATION, TECH, ITEM, State
from RPGFiles.Item import checkItems
from text_formatting import chat, channelchat, setRPGChannel, idchat
import RPGFiles.RPG as RPG
import os
import importlib


admin = [82921535681069056]


async def handleAdminCommand(message):
    if message.author.id in admin:
        content = message.content[1:]
        if content[:13] == "del location ":
            count = 0
            for player in PLAYER:
                if content[14:] in PLAYER[player].allowedlocations:
                    PLAYER[player].allowedlocations.remove(content[13:])
                    await PLAYER[player].save()
                    count += 1
            await chat(message, "You removed %s from %s players!" % (content[13:], count))
        elif content == "reloadRPG":
            for player in PLAYER:
                if PLAYER[player].state == State.ENCOUNTER:
                    await idchat(PLAYER[player].id, "The RPG was reloaded! You have been removed from the encounter.")
                elif PLAYER[player].state == State.SHOPPING:
                    await idchat(PLAYER[player].id, "The RPG was reloaded! You have been removed from the shop.")
                elif PLAYER[player].state == State.TRAINING:
                    await idchat(PLAYER[player].id, "The RPG was reloaded! You have been removed from the trainer.")
            LOCATION.clear()
            PLAYER.clear()
            MONSTER.clear()
            ITEM.clear()
            TECH.clear()
            print("\n\n")
            importlib.reload(RPG)
            importlib.reload(Character)
            importlib.reload(Item)
            importlib.reload(Location)
            importlib.reload(Tech)
            await RPG.initializeGame()
            await chat(message, "You reloaded the RPG!")
        elif content[:11] == "del player ":
            for player in PLAYER:
                if content[11:] == player:
                    for filename in os.listdir('RPGFiles/Players'):
                        if filename == player + '.txt':
                            if os.path.isfile('RPGFiles/Players/Deleted/%s.txt' % player):
                                os.remove('RPGFiles/Players/Deleted/%s.txt' % player)
                            os.rename('RPGFiles/Players/' + player + '.txt', "RPGFiles/Players/Deleted/" + player + '.txt')
                            await chat(message, "You deleted %s!" % (content[11:]))
                            del PLAYER[player]
                            break
            await chat(message, "%s was not found!" % (content[11:]))
        elif content == "check":
            await chat(message, "You are an admin!")
        elif content == "setmain":
            setRPGChannel(message.channel)
            await channelchat(message, "Set as main channel!")
        elif content == "checkid":
            await idchat(message.author.id, "%s" % message.channel.id)
        elif content == "checkitems":
            await idchat(message.author.id, "%s" % (checkItems()))
    else:
        await chat(message, "You are not an admin!")
