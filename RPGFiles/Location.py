from RPGFiles.lookup import LOCATION, MONSTER, ITEM, TECH, State
from text_formatting import idchat, bold, blockify, createCommandsBlock, smartCapitalize
from random import randint
from math import floor
from MathUtility import is_number

import copy
import asyncio


class Location:

    def __init__(self, name):
        LOCATION[name] = self
        self.image = None
        self.boss = None
        self.name = name
        self.traveltext = "Missing traveltext"
        self.surroundings = "Missing surroundings"
        self.encounterchance = {}
        self.hasshop = False
        self.hastrainer = False

        self.shopopening = 'Missing opening'
        self.shoprumor = []
        self.shopitem = []
        self.shopclosingbuy = 'Missing closing'
        self.shopclosingnobuy = 'Missing closing'

        self.traineropening = 'Missing opening'
        self.trainerrumor = []
        self.traineritem = []
        self.trainerclosing = 'Missing closing'


    def loadEnemy(self):
        encounterroll = randint(1, 100)
        for enemy in self.encounterchance:
            minchance, maxchance = self.encounterchance[enemy]
            if minchance <= encounterroll and maxchance >= encounterroll:
                return copy.deepcopy(MONSTER[enemy])


    def loadBoss(self):
        return copy.deepcopy(MONSTER[self.boss])


    async def shopping(self, player):
        if self.hasshop is False:
            await idchat(player.id, "There is no shop in %s!" % (bold(self.name)))
        elif player.state == State.SHOPPING:
            await idchat(player.id, "You are already shopping!")
        elif player.state == State.TRAINING:
            await idchat(player.id, "You can't shop while training!")
        elif player.state == State.ENCOUNTER:
            await idchat(player.id, "You can't shop during an encounter!")
        else:
            player.state = State.SHOPPING
            await idchat(player.id, "%s\nYou have %s Ides. What would you like to do? (-commands)" % (self.shopopening, player.money))
            player.lastmessage = ''
            rumorcount = 0
            buysomething = False
            while True:
                await asyncio.sleep(1)
                if player.lastmessage == "-commands" or player.lastmessage == "-cmds":
                    await idchat(player.id, blockify(createCommandsBlock(['Shopping', 'Inventory', 'Other', 'Debug'])))
                    player.lastmessage = ''
                elif player.lastmessage[:5] == "-buy ":
                    itemname = smartCapitalize(player.lastmessage[5:])
                    splititem = itemname.split(' ')
                    amount = splititem[len(splititem) - 1]
                    if is_number(amount) and int(amount) > 0:
                        amount = int(amount)
                        itemname = ''
                        i = 0
                        j = len(splititem) - 2
                        for text in splititem:
                            if i < j:
                                itemname += text + ' '
                            elif i == j:
                                itemname += text
                            i += 1
                    else:
                        amount = 1
                    if itemname not in ITEM:
                        await idchat(player.id, "Such a thing has nary been spotted in Iodra.")
                    else:
                        itemfound = False
                        for item in self.shopitem:
                            if item == itemname:
                                check = await player.checkinventoryslots()
                                if check >= amount:
                                    if player.money > ITEM[itemname].price * amount:
                                        player.money -= ITEM[itemname].price * amount
                                        num = amount
                                        while num > 0:
                                            player.inventory.insert(0, ITEM[itemname])
                                            num -= 1
                                        await idchat(player.id, "You bought %s x%s for %s ides" % (bold(itemname), amount, ITEM[itemname].price * amount))
                                        await player.save()
                                        buysomething = True
                                    else:
                                        await idchat(player.id, "You don't have enough ides!")
                                elif check < amount:
                                    await idchat(player.id, "You don't have enough space for %s x%s!" % (bold(itemname), amount))
                                itemfound = True
                                break
                        if itemfound is False:
                            await idchat(player.id, "The shop doesn't sell %s!" % (bold(itemname)))
                    player.lastmessage = ''
                elif player.lastmessage[:6] == "-sell ":
                    itemname = smartCapitalize(player.lastmessage[6:])
                    splititem = itemname.split(' ')
                    amount = splititem[len(splititem) - 1]
                    if is_number(amount) and int(amount) > 0:
                        amount = int(amount)
                        itemname = ''
                        i = 0
                        j = len(splititem) - 2
                        for text in splititem:
                            if i < j:
                                itemname += text + ' '
                            elif i == j:
                                itemname += text
                            i += 1
                    else:
                        amount = 1
                    sold = False
                    num = 0
                    for item in player.inventory:
                        if item.name == itemname:
                            num += 1
                    if itemname not in ITEM:
                        await idchat(player.id, "Such a thing has nary been spotted in Iodra.")
                    elif num >= amount:
                        item = ITEM[itemname]
                        player.money += floor(item.price * amount / 2)
                        await idchat(player.id, "You sold %s x%s for %s ides!" % (bold(itemname), amount, floor(item.price * amount / 2)))
                        num = amount
                        while num > 0:
                            player.inventory.remove(item)
                            num -= 1
                        sold = True
                        await player.save()
                    elif itemname in [player.weapon.name, player.shield.name, player.armor.name, player.charm.name]:
                        await idchat(player.id, "You can't sell something you have equipped!")
                    elif sold is False:
                        await idchat(player.id, "You do not have %s x%s" % (bold(itemname), amount))
                    player.lastmessage = ''
                elif player.lastmessage[:9] == "-examine ":
                    itemname = smartCapitalize(player.lastmessage[9:])
                    if itemname not in ITEM:
                        await idchat(player.id, "Such a thing has nary been spotted in Iodra.")
                    else:
                        inventorylist = [item.name for item in player.inventory]
                        examinelist = self.shopitem + [player.weapon.name, player.armor.name, player.shield.name, player.charm.name] + inventorylist
                        if itemname in examinelist:
                            types = ['Weapons', 'Shields', 'Charms', 'Items']
                            if ITEM[itemname].typeof in types:
                                type = ITEM[itemname].typeof[:len(ITEM[itemname].typeof) - 1].capitalize()
                            else:
                                type = ITEM[itemname].typeof.capitalize()
                            text_to_send = type + '\n' + ITEM[itemname].description
                            await idchat(player.id, blockify(text_to_send))
                        else:
                            await idchat(player.id, "You can't find the item to examine...")
                    player.lastmessage = ''
                elif player.lastmessage == "-list all":
                    text_to_send = ''
                    for listname in ['weapons', 'shields', 'armor', 'charms', 'items']:
                        shopdict = {}
                        typestring = listname.capitalize()
                        for item in self.shopitem:
                            if item in ITEM and ITEM[item].typeof == typestring:
                                shopdict[item] = ITEM[item].price
                        liststring = typestring + '\n'
                        for item in shopdict:
                            liststring += ('  %s: %s\n' % (item, shopdict[item]))
                        text_to_send += liststring
                    await idchat(player.id, blockify(text_to_send))
                    player.lastmessage = ''
                elif player.lastmessage[:6] == "-list ":
                    listname = player.lastmessage[6:].lower()
                    shopdict = {}
                    if listname in ['weapons', 'shields', 'armor', 'charms', 'items']:
                        typestring = listname.capitalize()
                        for item in self.shopitem:
                            if item in ITEM and ITEM[item].typeof == typestring:
                                shopdict[item] = ITEM[item].price
                        liststring = ''
                        for item in shopdict:
                            liststring += ('%s: %s\n' % (item, shopdict[item]))
                        await idchat(player.id, blockify(liststring))
                    else:
                        await idchat(player.id, "That list does not exist!")
                    player.lastmessage = ''
                elif player.lastmessage == "-rumors":
                    await idchat(player.id, "%s" % (self.shoprumor[rumorcount]))
                    if rumorcount < len(self.shoprumor) - 1:
                        rumorcount += 1
                    player.lastmessage = ''
                elif player.lastmessage == '-leave':
                    if buysomething is False:
                        await idchat(player.id, "%s" % (self.shopclosingnobuy))
                    elif buysomething is True:
                        await idchat(player.id, "%s" % (self.shopclosingbuy))
                    break
            player.state = State.NORMAL



    async def training(self, player):
        if self.hastrainer is False:
            await idchat(player.id, "There is no trainer in %s!" % (bold(self.name)))
        elif player.state == State.SHOPPING:
            await idchat(player.id, "You can't train while shopping!")
        elif player.state == State.ENCOUNTER:
            await idchat(player.id, "You can't train during an encounter!")
        elif player.state == State.TRAINING:
            await idchat(player.id, "You are already training!")
        else:
            player.state = State.TRAINING
            await idchat(player.id, "%s\nYou have %s Potential! What would you like to do? (-commands)" % (self.traineropening, player.potential))
            player.lastmessage = ''
            rumorcount = 0
            while True:
                await asyncio.sleep(1)
                if player.lastmessage == "-commands" or player.lastmessage == "-cmds":
                    await idchat(player.id, blockify(createCommandsBlock(['Training', 'Inventory', 'Other', 'Debug'])))
                    player.lastmessage = ''
                elif player.lastmessage[:7] == "-train ":
                    if player.lastmessage[7:].find(' ') != -1:
                        cmd = player.lastmessage[7:].split(' ')
                        attribute = cmd[0]
                        value = cmd[1]
                        attribute = attribute.lower()
                        if is_number(value) is True and int(value) > 0:
                            value = int(value)
                            if attribute in ['vigor', 'power', 'finesse', 'guard', 'will', 'magic', 'luck', 'speed'] and value <= player.potential:
                                if attribute == 'vigor':
                                    player.vigor += value
                                    player.maxlife += (value * 4)
                                    player.life += (value * 4)
                                    player.respecpoints += value
                                    player.potential -= value
                                    await idchat(player.id, "You gained %s Vigor and %s Life!" % (value, (value * 4)))
                                elif attribute == 'power':
                                    player.power += value
                                    player.respecpoints += value
                                    player.potential -= value
                                    await idchat(player.id, "You gained %s Power!" % (value))
                                elif attribute == 'finesse':
                                    player.finesse += value
                                    player.maxfocus += value
                                    player.focus += value
                                    player.respecpoints += value
                                    player.potential -= value
                                    await idchat(player.id, "You gained %s Finesse and %s Focus!" % (value, value))
                                elif attribute == 'guard':
                                    player.guard += value
                                    player.respecpoints += value
                                    player.potential -= value
                                    await idchat(player.id, "You gained %s Guard!" % (value))
                                elif attribute == 'will':
                                    player.will += value
                                    player.respecpoints += value
                                    player.potential -= value
                                    await idchat(player.id, "You gained %s Will!" % (value))
                                elif attribute == 'speed':
                                    player.speed += value
                                    player.respecpoints += value
                                    player.potential -= value
                                    await idchat(player.id, "You gained %s Speed!" % (value))
                                elif attribute == 'magic':
                                    player.magic += value
                                    player.maxmana += value
                                    player.mana += value
                                    player.respecpoints += value
                                    player.potential -= value
                                    await idchat(player.id, "You gained %s Magic and %s Mana!" % (value, value))
                                elif attribute == 'luck':
                                    player.luck += value
                                    player.respecpoints += value
                                    player.potential -= value
                                    await idchat(player.id, "You gained %s Luck!" % (value))
                                await idchat(player.id, "You have %s Potential remaining!" % (player.potential))
                            elif value > player.potential:
                                await idchat(player.id, "You don't have enough potential for that!")
                            else:
                                await idchat(player.id, "You need to input an attribute and a number of points greater than zero (example: -train power 3 )!")
                        else:
                            await idchat(player.id, "You need to input an attribute and a number of points greater than zero (example: -train power 3 )!")
                    else:
                        await idchat(player.id, "You need to input an attribute and a number of points greater than zero (example: -train power 3 )!")
                    player.lastmessage = ''
                    await player.save()
                elif player.lastmessage[:7] == "-learn ":
                    if self.name == 'Prison of Hope':
                        await idchat(player.id, "I am afraid my frailty prevents me from teaching you some of my greater techniques.")
                    else:
                        itemname = smartCapitalize(player.lastmessage[7:])
                        if itemname not in ITEM:
                            await idchat(player.id, "%s is not a spell nor skill.")
                        else:
                            itemfound = False
                            for item in self.traineritem:
                                if item == itemname:
                                    if item not in player.skills and item not in player.spells:
                                        if (TECH[itemname].prereq in player.skills or TECH[itemname].prereq in player.skills) or TECH[itemname].prereq is None:
                                            if player.potential >= TECH[itemname].potentialcost:
                                                player.potential -= TECH[itemname].potentialcost
                                                player.respecpoints += TECH[itemname].potentialcost
                                                if TECH[itemname].type == 'Spell':
                                                    player.spells.append(TECH[itemname])
                                                else:
                                                    player.skills.append(TECH[itemname])
                                                await idchat(player.id, "You learned %s for %s Potential!" % (bold(itemname), TECH[itemname].potentialcost))
                                                player.save()
                                                await idchat(player.id, "You have %s Potential left!" % (player.potential))
                                            else:
                                                await idchat(player.id, "You don't have enough Potential!")
                                        else:
                                            await idchat(player.id, "You need to learn %s before I can teach you %s." % (bold(TECH[itemname].prereq), bold(itemname)))
                                    else:
                                        await idchat(player.id, "I can't teach you what you already know!")
                                    itemfound = True
                                    break
                            if itemfound is False:
                                await idchat(player.id, "Sorry, I can't teach %s to you." % (bold(itemname)))
                    player.lastmessage = ''
                elif player.lastmessage[:9] == "-examine ":
                    tech = smartCapitalize(player.lastmessage[9:])
                    if tech not in TECH:
                        await idchat(player.id, "%s is neither a spell nor skill." % (itemname))
                    else:
                        techlist = [item.name for item in player.skills] + [item.name for item in player.spells]
                        examinelist = self.traineritem + techlist
                        if itemname in examinelist:
                            await idchat(player.id, blockify(TECH[itemname].description))
                        else:
                            await idchat(player.id, "No one around knows that spell or skill...")
                    player.lastmessage = ''
                elif player.lastmessage[:6] == "-list ":
                    if self.name == 'Prison of Hope':
                        await idchat(player.id, "I am afraid my frailty prevents me from teaching you some of my greater techniques.")
                    elif player.lastmessage == "-list all":
                        text_to_send = ''
                        for listname in ['spells', 'skills']:
                            trainerdict = {}
                            typestring = listname.capitalize()
                            for item in self.traineritem:
                                if item in TECH and TECH[item].typeof == typestring:
                                    trainerdict[item] = TECH[item].potentialcost
                            liststring = typestring + '\n'
                            for item in trainerdict:
                                liststring += ('  %s: %s\n' % (item, trainerdict[item]))
                            text_to_send += liststring
                        await idchat(player.id, blockify(text_to_send))
                        player.lastmessage = ''
                    else:
                        listname = player.lastmessage[6:].lower()
                        trainerdict = {}
                        if listname in ['spells', 'skills']:
                            typestring = listname.capitalize()
                            for item in self.traineritem:
                                if item in TECH and TECH[item].typeof == typestring:
                                    trainerdict[item] = TECH[item].potentialcost
                            liststring = ''
                            for item in trainerdict:
                                liststring += ('%s: %s\n' % (item, trainerdict[item]))
                            await idchat(player.id, blockify(liststring))
                        else:
                            await idchat(player.id, "That list does not exist!" % (liststring))
                    player.lastmessage = ''
                elif player.lastmessage == "-rumors":
                    await idchat(player.id, "%s" % (self.trainerrumor[rumorcount]))
                    if rumorcount < len(self.trainerrumor) - 1:
                        rumorcount += 1
                    player.lastmessage = ''
                elif player.lastmessage == "-respec":
                    await idchat(player.id, "Are you sure you wish to return all your potential? You will have to relearn all your spells and skills as well as retrain all of your attributes. Also, it's not cheap at 2500 ides (-accept|-decline).")
                    while True:
                        await asyncio.sleep(1)
                        if player.lastmessage == '-accept' and player.money >= 2500:
                            player.potential = player.potential + player.respecpoints
                            player.respecpoints = 0
                            player.maxlife = 40 + (player.level - 1) * 10
                            player.life = 40 + (player.level - 1) * 10
                            player.maxmana = 10
                            player.mana = 10
                            player.maxfocus = 10
                            player.focus = 10
                            player.vigor = 10
                            player.power = 10
                            player.finesse = 10
                            player.will = 10
                            player.guard = 10
                            player.magic = 10
                            player.speed = 10
                            player.luck = 10
                            player.skills = []
                            player.spells = []
                            await player.clearStatChanges()
                            player.money -= 2500
                            await player.save()
                            await idchat(player.id, "Your mind and body feel the same now as when you first picked up your sword and decided to carve your own fate. A world of potential is laid before you. (Don't forget to spend your points!)")
                            break
                        elif player.lastmessage == '-accept':
                            await idchat(player.id, "You cannot afford this special training.")
                            break
                        elif player.lastmessage == '-decline':
                            await idchat(player.id, "Ahh, maybe another time then.")
                            break
                    player.lastmessage = ''
                elif player.lastmessage == '-leave':
                    await idchat(player.id, "%s" % (self.trainerclosing))
                    break
            player.state = State.NORMAL
