from RPGFiles.Character import Character
from RPGFiles.lookup import LOCATION, ITEM, PLAYER, ENCOUNTERS, TECH, State, EncType, townlocationlist, hostilelocationlist
from text_formatting import idchat, rpgChat, bold, blockify, smartCapitalize, createCommandsBlock, allCommands
from random import randint
from os.path import isfile

import RPGFiles.Encounter as Encounter
import image_editor
import os
import operator
import asyncio


class Player(Character):

    def __init__(self, name):
        super().__init__(name)
        self.id = -1
        self.potential = 0
        self.respecpoints = 0
        self.money = 0
        self.exp = 0
        self.trainingpoints = 0
        self.kills = 0
        self.deaths = 0
        self.timeouts = 0
        self.runaway = 0
        self.location = getLocation('Prison of Hope')
        self.lasttown = getLocation('Tarrow')
        self.weapon = getItem('Worn Sword')
        self.shield = getItem('Barrel Lid')
        self.armor = getItem('Prison Garb')
        self.charm = getItem('Pendant')
        self.lastmessage = ''
        self.lastchannel = ''
        self.encountertimer = 0
        self.encountersinsamearea = 0
        self.killstreak = 0
        self.challenger = ''
        self.state = State.NORMAL
        self.forcebreak = False
        self.bossesbeaten = []
        self.raidbossesbeaten = []
        self.allowedlocations = ['Prison of Hope']
        self.inventory = []
        self.tempslot = []
        self.inventorymax = 8

    async def handleCharacterCommand(self, RPGTestMode):
        if self.lastmessage[:9] == '-examine ':
            item = smartCapitalize(self.lastmessage[9:])
            await self.examineItem(item, PLAYER)
        elif self.lastmessage[:5] == '-use ' and self.state != State.ENCOUNTER:
            item = smartCapitalize(self.lastmessage[5:])
            await self.useItem(item)
        elif self.lastmessage == '-shop':
            await self.location.shopping(self)
        elif self.lastmessage == '-trainer':
            await self.location.training(self)
        elif self.lastmessage == '-travel':
            await self.displayTravel()
        elif self.lastmessage == '-location' or self.lastmessage == '-loc':
            await idchat(self.id, ("You are at %s!" % (bold(PLAYER[self.name].location.name))))
        elif self.lastmessage == '-commands all' or self.lastmessage == '-cmds all':
            await allCommands()
        elif self.lastmessage == '-commands' or self.lastmessage == '-cmds':
            if self.state == State.ENCOUNTER:
                await idchat(self.id, blockify(createCommandsBlock(['Battle', 'Inventory', 'Other', 'Debug'])))
            elif self.state != State.SHOPPING and self.state != State.TRAINING and self.state != State.ENCOUNTER:
                await idchat(self.id, blockify(createCommandsBlock(['Inventory', 'Travel', 'Instance', 'Other', 'Debug'])))
        elif self.lastmessage[:8] == '-travel ':
            if self.state == State.NORMAL:
                location = smartCapitalize(self.lastmessage[8:])
                if location in PLAYER[self.name].allowedlocations and location != PLAYER[self.name].location:
                    await self.travel(location)
                elif location == PLAYER[self.name].location:
                    await idchat(self.id, ("You are already at %s!" % (bold(location))))
                else:
                    await idchat(self.id, ("You don't know how to get to %s!" % (bold(location))))
            elif PLAYER[self.name].state == State.SHOPPING:
                await idchat(self.id, ("You can't travel while in the shop!"))
            elif PLAYER[self.name].state == State.TRAINING:
                await idchat(self.id, ("You can't travel while training!"))
            else:
                await idchat(self.id, ("You can't travel during an encounter!"))
        elif self.lastmessage == '-surroundings' or self.lastmessage == '-look':
            await idchat(self.id, "%s" % (self.location.surroundings))
        elif self.lastmessage == '-stats':
            await self.displayStats()
        elif self.lastmessage == '-inv' or self.lastmessage == '-inventory':
            await self.displayInventory()
        elif self.lastmessage[:9] == '-discard ':
            itemname = smartCapitalize(self.lastmessage[9:])
            await self.discarditem(itemname)
        elif self.lastmessage[:7] == '-equip ':
            itemname = smartCapitalize(self.lastmessage[7:])
            await self.equipitem(itemname)
        elif self.lastmessage == '-encounter' or self.lastmessage == '-enc':
            if self.location.name in hostilelocationlist:
                if self.state == State.SHOPPING:
                    await idchat(self.id, ("You are busy shopping!"))
                elif self.state == State.TRAINING:
                    await idchat(self.id, ("You are busy training!"))
                else:
                    enc = Encounter.Encounter()
                    await enc.setup([self], EncType.NORMAL)
            else:
                await idchat(self.id, ("You can't get in encounters in %s!" % bold(self.location.name)))
        elif self.lastmessage == '-encounter boss' or self.lastmessage == '-enc boss':
            if self.location.name in hostilelocationlist:
                if self.state == State.SHOPPING:
                    await idchat(self.id, ("You are busy shopping!"))
                elif self.state == State.TRAINING:
                    await idchat(self.id, ("You are busy training!"))
                else:
                    enc = Encounter.Encounter()
                    await enc.setup([self], EncType.BOSS)
            else:
                await idchat(self.id, ("You can't get in encounters in %s!" % bold(self.location.name)))
        elif self.lastmessage[:7] == '-meditate ' or self.lastmessage[:13] == '-concentrate ' or self.lastmessage[:5] == '-med ' or self.lastmessage[:5] == '-con ':
            cmd = self.lastmessage.split(' ')
            command = cmd[0]
            amount = cmd[1]
            await self.meditateconcentrate(command, amount)
        elif self.lastmessage == '-imstuck':
            for encounter in ENCOUNTERS:
                if self in encounter.players:
                    await encounter.end()
            self.state = State.NORMAL
            await idchat(self.id, "Pulled you out of combat/shop/trainer! Careful with this command as it could break things!")
        self.lastmessage == ''

    async def save(self):
        fileobj = open("RPGFiles/Players/%s.temp.txt" % self.name, "w+")
        for attr in vars(self):
            attrval = getattr(self, attr)
            if isobject(attrval):
                fileobj.write("%s: \"%s\"\n" % (attr, attrval.name))
            elif isinstance(attrval, dict):
                for k in attrval:
                    v = attrval[k]
                    if isobject(v):
                        fileobj.write("%s.%s: \"%s\"\n" % (attr, k, v.name))
                    elif isinstance(v, str):
                        fileobj.write("%s.%s: \"%s\"\n" % (attr, k, v))
                    else:
                        fileobj.write("%s.%s: %s\n" % (attr, k, v))
            elif isinstance(attrval, str):
                fileobj.write("%s: \"%s\"\n" % (attr, attrval))
            elif isinstance(attrval, list):
                if len(attrval) == 0:
                    fileobj.write("%s: []\n" % attr)
                elif isobject(attrval[0]):
                    savelist = [obj.name for obj in attrval]
                    fileobj.write("%s: %s\n" % (attr, savelist))
                else:
                    fileobj.write("%s: %s\n" % (attr, attrval))
            else:
                fileobj.write("%s: %s\n" % (attr, attrval))
        fileobj.close()
        if isfile("RPGFiles/Players/%s.txt" % self.name) is True:
            os.remove("RPGFiles/Players/%s.txt" % self.name)
        os.rename("RPGFiles/Players/%s.temp.txt" % self.name, "RPGFiles/Players/%s.txt" % self.name)


    async def load(self):
        fileobj = open("RPGFiles/Players/%s.txt" % self.name)
        data = fileobj .readlines()
        fileobj .close()
        for line in data:
            parsed = line.split(': ', 1)
            if '.' in parsed[0]:
                attr, key = tuple(parsed[0].split('.', 1))
                val = parsed[1]
                dct = getattr(self, attr)
                dct[key] = eval(val)
            else:
                attr = parsed[0]
                val = parsed[1]
                setattr(self, attr, eval(val))
        await self.setPlayer()
        self.location = LOCATION[self.location]
        self.weapon = getItem(self.weapon)
        self.shield = getItem(self.shield)
        self.armor = getItem(self.armor)
        self.charm = getItem(self.charm)
        for item in self.inventory.copy():
            self.inventory.remove(item)
            self.inventory.append(ITEM[item])
        self.isplayer = True
        self.forcebreak = False
        self.state = State.NORMAL
        await self.clearStatChanges()


    async def delete(self):
        if isfile('RPG/Players/Deleted/%s.txt' % self.name):
            os.remove('RPG/Players/Deleted/%s.txt' % self.name)
        os.rename('RPG/Players/%s.txt' % self.name, 'RPG/Players/Deleted/%s.txt' % self.name)
        await idchat(self.id, ("Deleted %s!" % self.name))

    async def displayInventory(self):
        stacks = {}
        for item in self.inventory:
            if item.name not in stacks:
                stacks[item.name] = 1
            else:
                stacks[item.name] += 1
        sortedstacks = sorted(stacks.items(), key=operator.itemgetter(1), reverse=True)
        stringofitems = ''
        if len(sortedstacks) == 0:
            stringofitems = 'Nothing...'
        else:
            if len(sortedstacks) < 3:
                item, number = sortedstacks[0]
                if number == 1:
                    stringofitems = '%s' % item
                else:
                    stringofitems = '%s x%s' % (item, number)
            else:
                item, number = sortedstacks[0]
                if number == 1:
                    stringofitems = '%s,' % item
                else:
                    stringofitems = '%s x%s,' % (item, number)
            if len(sortedstacks) >= 2:
                for itempair in sortedstacks[1:len(stacks) - 1]:
                    item, number = itempair
                    if number == 1:
                        stringofitems += (' %s,' % item)
                    else:
                        stringofitems += (' %s x%s,' % (item, number))
            if len(sortedstacks) == 1:
                pass
            else:
                item, number = sortedstacks[len(stacks) - 1]
                if number == 1:
                    stringofitems += ' and %s' % item
                else:
                    stringofitems += ' and %s x%s' % (item, number)
        imageList = []
        equipList = []
        for item in sortedstacks:
            num = item[1]
            while num > 0:
                imageList.append(ITEM[item[0]].getImage())
                num -= 1
        equipList.append(self.weapon.getImage())
        equipList.append(self.shield.getImage())
        equipList.append(self.armor.getImage())
        equipList.append(self.charm.getImage())
        image = image_editor.createInventory(equipList, imageList, self.id)
        if image is not None:
            if self.weapon is None or self.weapon.is2handed is False:
                await idchat(self.id, blockify("Weapon: %s\nShield: %s\n Armor: %s\n Charm: %s\n\n" % (self.weapon.name, self.shield.name, self.armor.name, self.charm.name) +
                                               "Inventory %s/%s : %s\n" % (len(self.inventory), self.inventorymax, stringofitems) +
                                               "Ides: %s" % (self.money)), ['temp_inv_%s.jpg' % self.id])
            else:
                await idchat(self.id, blockify("Weapon: %s\nShield: %s (Inactive)\nArmor: %s\nCharm: %s\n\n" % (self.weapon.name, self.shield.name, self.armor.name, self.charm.name) +
                                               "Inventory %s/%s : %s\n" % (len(self.inventory), self.inventorymax, stringofitems) +
                                               "Ides: %s" % (self.money)), ['temp_inv_%s.jpg' % self.id])
        else:
            if self.weapon is None or self.weapon.is2handed is False:
                await idchat(self.id, blockify("Weapon: %s\nShield: %s\n Armor: %s\n Charm: %s\n\n" % (self.weapon.name, self.shield.name, self.armor.name, self.charm.name) +
                                               "Inventory %s/%s : %s\n" % (len(self.inventory), self.inventorymax, stringofitems) +
                                               "Ides: %s" % (self.money)))
            else:
                await idchat(self.id, blockify("Weapon: %s\nShield: %s (Inactive)\nArmor: %s\nCharm: %s\n\n" % (self.weapon.name, self.shield.name, self.armor.name, self.charm.name) +
                                               "Inventory %s/%s : %s\n" % (len(self.inventory), self.inventorymax, stringofitems) +
                                               "Ides: %s" % (self.money)))
        os.remove('temp_inv_%s.jpg' % self.id)


    async def displayStats(self):
        await self.clearStatChanges()
        await idchat(self.id, blockify("     Name: %s\n\n    Level: %s\n      EXP: %s/%s\nPotential: %s\n" % (self.name, self.level, self.exp, self.level * self.level, self.potential) +
                                       "\n     Life: %s/%s\n     Mana: %s/%s\n    Focus: %s/%s\n" % (self.life, self.get('maxlife'), self.mana, self.get('maxmana'), self.focus, self.get('maxfocus')) +
                                       "\n    Vigor: %s\n    Power: %s\n  Finesse: %s\n     Will: %s\n" % (self.vigor, self.get('power'), self.get('finesse'), self.get('will')) +
                                       "    Guard: %s\n    Speed: %s\n     Luck: %s\n" % (self.get('guard'), self.get('speed'), self.get('luck'))))


    async def displayTravel(self):
        loc = self.allowedlocations
        loc.sort()
        stringofitems = ''
        for i in loc:
            stringofitems += i + "\n"
        await idchat(self.id, "Travel Locations:\n%s" % (blockify(stringofitems)))


    async def travel(self, location):
        if location == self.location.name:
            await idchat(self.id, "You are already here!")
        else:
            await idchat(self.id, "You traveled to %s! %s" % (bold(location), LOCATION[location].traveltext))
            self.encountersinsamearea = 0
            self.location = LOCATION[location]
            self.life = self.maxlife + self.statchange['maxlife']
            if self.location.name in townlocationlist:
                self.lasttown = self.location.name
            await self.save()


    # async def itemAmbiguity(self, itemname):
    #     itemwords = [i.name for i in self.inventory] + [self.weapon.name, self.shield.name, self.armor.name, self.charm.name]
    #     c = Counter(itemwords)
    #     if c[itemname] > 1:
    #         return True
    #     return False


    async def useItem(self, item):
        if self.state != State.ENCOUNTER:
            if ITEM[item].worlditem is True:
                if item not in ITEM:
                    await idchat(self.id, "'%s' does not exist!" % item)
                elif ITEM[item] in self.inventory:
                    await ITEM[item].useItem(self)
                else:
                    await idchat(self.id, "You don't have that item.")
            else:
                await idchat(self.id, "You cannot use this item in this way.")


    async def examineItem(self, item, PLAYER):
        if item in ITEM:
            item_obj = None
            types = ['Weapons', 'Shields', 'Charms', 'Items']
            if ITEM[item].typeof in types:
                type = ITEM[item].typeof[:len(ITEM[item].typeof) - 1].capitalize()
            else:
                type = ITEM[item].typeof.capitalize()
            equipment = [self.weapon.name, self.armor.name, self.shield.name, self.charm.name]
            inventory = [item.name for item in self.inventory]
            itemlist = equipment + inventory
            if self.state == State.SHOPPING:
                itemlist += self.location.shopitem
            elif len(self.tempslot) == 1:
                itemlist.append(self.tempslot[0].name)
            if item in itemlist:
                item_obj = ITEM[item]
            if item_obj is not None:
                str = item_obj.getImage()
                if str != 'RPGFiles/Art/Icons/NOPIC.png':
                    img = image_editor.size128(str, string=True)
                    img.save('temp%s.png' % self.id)
                    await idchat(self.id, blockify(type + "\n%s" % (item_obj.description)), ['temp%s.png' % self.id])
                    os.remove('temp%s.png' % self.id)
                else:
                    await idchat(self.id, blockify(type + "\n%s" % (item_obj.description)))
            else:
                await idchat(self.id, ("You can't find the item to examine..."))
        elif item in TECH:
            tech_obj = None
            tech = item
            if self.state == State.TRAINING:
                examinelist = self.location.traineritem
                if tech in examinelist:
                    tech_obj = TECH[tech]
            else:
                techlist = [TECH[tech].name for tech in self.skills] + [TECH[tech].name for tech in self.spells]
                if tech in techlist:
                    tech_obj = TECH[tech]
            if tech_obj is not None:
                await idchat(self.id, blockify(TECH[tech].description))
            else:
                await idchat(self.id, "No one around knows that spell or skill...")
        else:
            await idchat(self.id, "'%s' does not exist!" % item)


    async def discarditem(self, itemname):
        if itemname not in ITEM:
            await idchat(self.id, "'%s' does not exist!" % itemname)
        elif ITEM[itemname] in self.inventory:
            self.inventory.remove(ITEM[itemname])
            await idchat(self.id, "You discard %s." % (bold(itemname)))
        elif itemname in [self.weapon.name, self.shield.name, self.armor.name, self.charm.name]:
            await idchat(self.id, "You can't discard something you have equipped!")
        else:
            await idchat(self.id, "You don't have %s!" % (bold(itemname)))


    async def equipitem(self, itemname):
        if self.state == State.ENCOUNTER:
            await idchat(self.id, "You don't have time for that!")
        else:
            if itemname not in ITEM:
                await idchat(self.id, "'%s' does not exist!" % itemname)
                return
            elif ITEM[itemname] in self.inventory:
                item = ITEM[itemname]
                if item.typeof == 'Weapons':
                    self.inventory.remove(item)
                    self.inventory.insert(0, self.weapon)
                    self.weapon = item
                    await idchat(self.id, ("You equip %s" % (bold(itemname))))
                    return
                elif item.typeof == 'Armor':
                    self.inventory.remove(item)
                    self.inventory.insert(0, self.armor)
                    self.armor = item
                    await idchat(self.id, ("You equip %s" % (bold(itemname))))
                    return
                elif item.typeof == 'Shields':
                    self.inventory.remove(item)
                    self.inventory.insert(0, self.shield)
                    self.shield = item
                    await idchat(self.id, ("You equip %s" % (bold(itemname))))
                    return
                elif item.typeof == 'Charms':
                    self.inventory.remove(item)
                    self.inventory.insert(0, self.charm)
                    self.charm = item
                    await idchat(self.id, ("You equip %s" % (bold(itemname))))
                    return
                else:
                    await idchat(self.id, ("%s cannot be equipped!" % (bold(itemname))))
            await idchat(self.id, ("You don't have %s!" % (bold(itemname))))


    async def levelUp(self, droplist):
        while self.exp >= self.level ** 2:
            await asyncio.sleep(.25)
            self.exp -= self.level ** 2
            self.level += 1
            await idchat(self.id, "You hit level %s! You gain 5 Potential and 10 Life!" % (self.level))
            await rpgChat("%s hit level %s!" % (bold(self.name), self.level))
            self.potential += 5
            self.maxlife += 10
            self.life += 10
            if randint(1, 100) < self.luck:
                await idchat(self.id, "What luck! You gain 1 extra Potential!")
                self.potential += 1
        await self.drops(droplist)


    async def drops(self, droplist):
        self.state = State.NORMAL
        for item in droplist:
            if randint(1, 100) <= (droplist[item] + (100 - droplist[item]) * (0.01 * self.encountersinsamearea) + (self.luck / 15)):
                await idchat(self.id, ("You find %s!" % (bold(item))))
                self.tempslot.append(ITEM[item])
                if await self.checkinventoryslots() > 0:
                    self.inventory.insert(0, ITEM[item])
                    await idchat(self.id, ("You take %s!" % (bold(item))))
                else:
                    await idchat(self.id, ("You forfeit %s." % (bold(item))))
                self.tempslot.remove(ITEM[item])
        if self.life > (self.maxlife + self.statchange['maxlife']) * .75:
            await idchat(self.id, ("With a feeling of triumph, you press on."))
        elif self.life > (self.maxlife + self.statchange['maxlife']) * .5:
            await idchat(self.id, ("Wounded, but not discouraged, you press on."))
        elif self.life > (self.maxlife + self.statchange['maxlife']) * .25:
            await idchat(self.id, ("After the trying conflict, you pick yourself up and press on."))
        else:
            await idchat(self.id, ("Holding on by a thread, you drag yourself to your feet and press on."))
        await self.save()


    async def cleanUp(self, droplist, die):
        await self.clearStatChanges()
        await self.clearStatusEffects()
        self.energy = 0
        self.chargecount = 1
        await self.save()
        if die is False:
            await self.levelUp(droplist)


    async def checkinventoryslots(self):
        if len(self.inventory) < self.inventorymax:
            return (self.inventorymax - len(self.inventory))
        return await self.fullinventory()


    async def fullinventory(self):
        await idchat(self.id, ("Your inventory is full! Discard or use something now or say -forfeit"))
        self.lastmessage = ''
        while True:
            await asyncio.sleep(1)
            if self.lastmessage[:8] == '-discard':
                if len(self.inventory) < 8:
                    return True
            elif self.lastmessage[:4] == '-use':
                if len(self.inventory) < 8:
                    return True
            elif self.lastmessage == '-forfeit':
                return False



def getLocation(locationname):
    global LOCATION
    if locationname in LOCATION:
        return LOCATION[locationname]
    else:
        return None


def getItem(itemname):
    global ITEM
    if itemname in ITEM:
        return ITEM[itemname]
    else:
        return None


def isobject(data):
    return hasattr(data, '__dict__')
