from RPGFiles.lookup import MONSTER, ENCOUNTERS, LOCATION, ITEM, TECH, State, EncType
from text_formatting import idchat, bold, unbold, blockify, rpgChat, smartCapitalize

from random import randint, choice
from math import ceil, floor
import copy
import time
import asyncio


class Encounter:

    def __init__(self):
        self.characters = []
        self.players = []
        self.type = EncType.NORMAL
        self.startTime = time.time()
        self.lastTurn = None
        self.escape = False
        self.finished = False
        self.enemy = None

    async def setup(self, characters, type, pvpBoss=''):
        global ENCOUTNERS
        ENCOUNTERS.append(self)
        for character in characters:
            self.characters.append(character)
            self.players.append(character)
            character.state = State.ENCOUNTER
            character.team = 1
            character.lastmessage = ''
        if type == EncType.NORMAL:
            enemy = self.players[0].location.loadEnemy()
            self.characters.append(enemy)
            self.enemy = enemy
        elif type == EncType.BOSS:
            enemy = self.players[0].location.loadBoss()
            self.characters.append(enemy)
            self.enemy = enemy
        elif type == EncType.RAID:
            enemy = copy.deepcopy(MONSTER[pvpBoss])
            self.characters.append(enemy)
            self.enemy = enemy
        for character in self.characters:
            character.energy = 0
        self.characters.sort(key=sortEncounterList, reverse=True)
        if type != EncType.PVP:
            await asyncio.sleep(1)
            for player in self.players:
                await idchat(player.id, ("%s\nYou have encountered %s!" % (enemy.opening, enemy.name)))
        else:
            await idchat(player.id, "You are dueling %s!" % (bold(self.players[1].name)))
            await idchat(player.id, "You are dueling %s!" % (bold(self.players[0].name)))
        await self.loop()

    async def loop(self):
        while not self.finished:
            newTurn = False
            await asyncio.sleep(.1)
            turnlist = self.characters.copy()
            for character in turnlist:
                playerCount = len(self.players)
                enemyCount = len(self.characters) - playerCount
                if self.type == EncType.PVP and playerCount <= 1:
                    self.finished = True
                    break
                elif self.type != EncType.PVP and (playerCount == 0 or enemyCount == 0):
                    self.finished = True
                    break
                elif self.escape is True:
                    self.finished = True
                    break
                if character.energy < 1000:
                    await character.energyRecovery()  # FIX!!!
                    continue
                else:
                    await self.statusDamage(character)  # FIX!!!
                    if character.life <= 0:
                        continue
                if character.energy > 1000:
                    newTurn = True
                while character.energy >= 1000:
                    await asyncio.sleep(1)
                    if character.status['Sleep']:
                        sleepRoll = randint(1, 10)
                        if sleepRoll > 3:
                            character.energy = 900
                            for player in self.players:
                                if character == player:
                                    await idchat(player.id, "You are asleep!")
                                else:
                                    await idchat(player.id, "%s is asleep!" % (character.name))
                            break
                        else:
                            character.status['Sleep'] = False
                            for player in self.players:
                                if character == player:
                                    await idchat(player.id, "You woke up!")
                                else:
                                    await idchat(player.id, "%s woke up!" % (character.name))
                    if character.status['Paralysis']:
                        paralysisRoll = randint(1, 10)
                        if paralysisRoll > 5:
                            character.energy = 700
                            for player in self.players:
                                if character == player:
                                    await idchat(player.id, "You are paralyzed!")
                                else:
                                    await idchat(player.id, "%s is paralyzed!" % (character.name))
                            break
                        else:
                            character.status['Paralysis'] = False
                            for player in self.players:
                                if character == player:
                                    await idchat(player.id, "You can move again!")
                                else:
                                    await idchat(player.id, "%s can move again!" % (character.name))
                    if character.status['Panic']:
                        panicRoll = randint(1, 10)
                        if panicRoll < 4:
                            character.energy = 900
                            for player in self.players:
                                if character == player:
                                    await idchat(player.id, "You panic and fumble your weapon!")
                                else:
                                    await idchat(player.id, "%s is panicking!" % (character.name))
                            break
                        elif panicRoll == 10:
                            character.status['Panic'] = False
                            for player in self.players:
                                if player == character:
                                    await idchat(player.id, "Your panic subsides!")
                                else:
                                    await idchat(player.id, "%s stops panicking!" % (character.name))
                        else:
                            await idchat(character.id, "You feel very tense!")
                    if self.lastTurn != character:
                        newTurn = False
                        for player in self.players:
                            if player == character:
                                await idchat(player.id, ("It's your turn! You have %s energy and %s health! What "
                                                         "would you like to do? (-commands)" % (character.energy, character.life)))
                                character.lastmessage == ''
                            else:
                                await idchat(player.id, "It's %s's turn!" % (character.name))
                    elif newTurn or character.isplayer is False:
                        newTurn = False
                        for player in self.players:
                            if player == character:
                                await idchat(player.id, "You continue your attack! You have %s energy and %s health! What "
                                                        "would you like to do? (-commands)" % (character.energy, character.life))
                            else:
                                await idchat(player.id, "%s continues their attack!" % (character.name))
                    if character.isplayer:
                        if self.type != EncType.PVP:
                            if self.lastTurn != character:
                                self.lastTurn == character
                            escape = await self.playerTurn(character, self.enemy, True)
                            if escape is True:
                                self.finished = True
                                break
                        else:
                            if character == self.players[0]:
                                if self.lastTurn != character:
                                    self.lastTurn == character
                                escape = await self.playerTurn(character, self.players[1], False)
                            else:
                                if self.lastTurn != character:
                                    self.lastTurn == character
                                escape = await self.playerTurn(character, self.players[0], False)
                    elif character.isplayer is False:
                        if self.lastTurn != character:
                            self.lastTurn == character
                        await self.enemyTurn()
                    if time.time() - 3600 > self.startTime:
                        for player in self.players:
                            await idchat(player.id, ("Time's up! Encounters time out after one hour!"))
                            player.timeouts += 1
                            await player.cleanUp(player.id, {}, True)
                        self.finished = True
                        break
                    self.lastTurn = character
            self.characters.sort(key=sortEncounterList, reverse=True)
        await self.end()

    async def end(self):
        self.finished = True
        for player in self.players:
            player.state = State.NORMAL
            player.energy = 0
            player.chargecount = 1
            await player.clearStatChanges()
            await player.clearStatusEffects()
        if self in ENCOUNTERS:
            ENCOUNTERS.remove(self)

    async def damageRoll(self, character, target):
        if not await character.hitChance(target):
            if character.status['Blind']:
                for player in self.players:
                    if player.name == target.name:
                        await idchat(player.id, "%s flails blindly and misses you!" % (character.name))
                    elif player.name == character.name:
                        await idchat(player.id, "You flail blindly and miss %s!" % (target.name))
                    else:
                        await idchat(player.id, "%s flails blindly and misses %s!" % (character.name, target.name))
            else:
                for player in self.players:
                    if player.name == target.name:
                        await idchat(player.id, "You dodged %s's attack!" % (character.name))
                    elif player.name == character.name:
                        await idchat(player.id, "%s dodged your attack!" % (target.name))
                    else:
                        await idchat(player.id, "%s dodged %s's attack!" % (target.name, character.name))
            return
        iscrit = False
        Damage = randint(ceil(character.power / 2), character.power)
        CritRoll = randint(1, 100)
        if ceil(character.critchance + character.luck * 0.075) >= CritRoll:
            Damage += character.power
            iscrit = True
        Damage = ceil(Damage * min(1, (character.power / target.guard) * 0.5))
        if Damage == 0:
            for player in self.players:
                if player.name == target.name and target.behavior == 'Player' and target.weapon.is2handed:
                    await idchat(player.id, "%s" % (character.weapon.nodamagereceivetext.format(player=character.name)))
                elif player.name == target.name and target.behavior == 'Player' and target.weapon.is2handed is False:
                    await idchat(player.id, "%s" % (character.shield.nodamagereceivetext.format(player=character.name)))
                elif player.name == character.name and target.behavior != 'Player':
                    await idchat(player.id, "%s" % (target.nodamagetext))
                elif player.name == character.name and target.weapon.is2handed:
                    await idchat(player.id, "%s" % (target.weapon.nodamagedealtext.format(player=target.name)))
                elif player.name == character.name and target.weapon.is2handed is False:
                    await idchat(player.id, "%s" % (target.shield.nodamagedealtext.format(player=target.name)))
                else:
                    await idchat(player.id, "%s's attack bounced off %s's armor!" % (target.name, character.name))
        elif iscrit:
            for player in self.players:
                if player.name == target.name and character.isplayer is False:
                    await idchat(player.id, "%s" % (character.crittext.format(damage=Damage)))
                elif player.name == target.name and character.isplayer:
                    await idchat(player.id, "%s" % (character.weapon.critreceivetext.format(player=character.name, damage=Damage)))
                elif player.name == character.name:
                    await idchat(player.id, "%s" % (character.weapon.critdealtext.format(player=target.name, damage=Damage)))
                else:
                    await idchat(player.id, "%s was dealt a critical blow by %s for %s damage!" % (target.name, character.name, Damage))
        else:
            for player in self.players:
                if player.name == target.name and character.isplayer is False:
                    await idchat(player.id, "%s" % (character.damagetext.format(damage=Damage)))
                elif player.name == target.name and character.isplayer:
                    await idchat(player.id, "%s" % (character.weapon.damagereceivetext.format(player=character.name, damage=Damage)))
                elif player.name == character.name:
                    await idchat(player.id, "%s" % (character.weapon.damagedealtext.format(player=target.name, damage=Damage)))
                else:
                    await idchat(player.id, "%s was hit by %s for %s damage!" % (target.name, character.name, Damage))
        await self.takeDamage(target, Damage)
        if target.life > 0 and Damage > 0:
            if character.isplayer:
                await self.evaluateStatus(target, character.weapon.statusinflict, character.weapon.statuschance)
            else:
                await self.evaluateStatus(target, character.statusinflict, character.statuschance)

    async def statusDamage(self, character):
        TotalDamage = 0
        if character.status['Poison'] is True:
            Damage = randint(1, ceil((character.maxlife + character.statchange['maxlife']) / 20))
            TotalDamage += Damage
            for player in self.players:
                if player.name == character.name:
                    await idchat(player.id, "You took %s poison damage!" % (Damage))
                else:
                    await idchat(player.id, "%s took %s poison damage!" % (character.name, Damage))
        if character.status['Toxic'] is True:
            Damage = randint(ceil((character.maxlife + character.statchange['maxlife']) / 10), ceil((character.maxlife + character.statchange['maxlife']) / 4))
            TotalDamage += Damage
            for player in self.players:
                if player.name == character.name:
                    await idchat(player.id, "You took %s toxic damage!" % (Damage))
                else:
                    await idchat(player.id, "%s took %s toxic damage!" % (character.name, Damage))
        if character.status['Bleed'] is True:
            Damage = randint(ceil((character.maxlife + character.statchange['maxlife']) / 25), ceil((character.maxlife + character.statchange['maxlife']) / 10))
            TotalDamage += Damage
            for player in self.players:
                if player.name == character.name:
                    await idchat(player.id, "You took %s bleeding damage!" % (Damage))
                else:
                    await idchat(player.id, "%s took %s bleeding damage!" % (character.name, Damage))
        await self.takeDamage(character, TotalDamage)

    async def takeDamage(self, character, amount):
        character.life -= amount
        if character.life <= 0:
            self.characters.remove(character)
            for player in self.players:
                if player.name == character.name:
                    await idchat(player.id, "You collapse!")
                    print(character.name + " died")
                else:
                    await idchat(player.id, "%s dies!" % (character.name))
            if character.isplayer is False:
                for player in self.players:
                    moneyfound = floor(character.moneyaward * (1 + (player.luck / 100)))
                    print(player.name + ' has defeated ' + unbold(character.name))
                    if character.isboss is True and character.name in player.bossesbeaten:
                        player.money += floor(moneyfound / 3)
                        player.exp += floor(character.expaward / 3)
                        money = floor(moneyfound / 3)
                        exp = floor(character.expaward / 3)
                    else:
                        player.money += moneyfound
                        player.exp += character.expaward
                        money = moneyfound
                        exp = character.expaward
                    if character.isboss:
                        if character.name not in player.bossesbeaten:
                            player.bossesbeaten.append(character.name)
                            await idchat(player.id, "%s" % (character.bossoutro))
                            await rpgChat("%s has cleared %s!" % (bold(player.name), bold(player.location.name)))
                    if character.israidboss:
                        if character.name not in player.raidbossesbeaten:
                            player.raidbossesbeaten.append(character.name)
                            await idchat(player.id, "%s" % (character.bossoutro))
                    await idchat(player.id, "You got %s ides and %s experience!" % (money, exp))
                    if len(character.unlocklocations) > 0:
                        addedlocations = []
                        for location in character.unlocklocations:
                            if location not in player.allowedlocations:
                                player.allowedlocations.append(location)
                                addedlocations.append(location)
                        if len(addedlocations) > 0:
                            await idchat(player.id, "You've unlocked new destinations: %s" % (', '.join(bold(addedlocations))))
                    player.encountersinsamearea += 1
                    player.kills += 1
                    if player.encountersinsamearea > player.killstreak:
                        player.killstreak = player.encountersinsamearea
                    await player.cleanUp(character.droplist, False)
            else:
                character.state = State.NORMAL
                await character.clearStatChanges()
                await character.clearStatusEffects()
                character.life = (character.maxlife + character.statchange['maxlife'])
                self.players.remove(character)
                moneyloss = ceil(character.money / 10)
                character.money = character.money - moneyloss
                character.encountersinsamearea = 0
                character.deaths += 1
                if len(character.allowedlocations) == 1:
                    if moneyloss > 0:
                        await idchat(character.id, "A guard drags you back to your cell. He smirks as he pilfers a portion of your ides (%s). After some time, you return to your feet." % (moneyloss))
                    else:
                        await idchat(character.id, "A guard drags you back to your cell. Finding no ides on you, he gives you a solid kick to the ribs and leaves. After some time, you return to your feet.")
                else:
                    character.location = getLocation(character.lasttown)
                    if moneyloss > 0:
                        await idchat(character.id, "A mysterious figure approaches as you lose consciousness. You awaken in the %s inn clutching a note, \"Your generous payment of %s ides is accepted. Be vigilant, stranger.\"" % (bold(character.location.name), moneyloss))
                    else:
                        await idchat(character.id, "A mysterious figure approaches as you lose consciousness. You awaken in the %s inn clutching a note, \"You owe me, stranger. Dearly.\"" % (bold(character.location.name)))
                await character.save()
                await character.cleanUp({}, True)

    async def evaluateStatus(self, character, inflict, chance):
        if inflict > 0:
            statroll = randint(1, 100)
            chance *= 1 - (character.will / 272)
            if chance >= statroll:
                if inflict == 1 and character.status['Poison'] is False:
                    character.status['Poison'] = True
                    for player in self.players:
                        if player.name == character.name:
                            await idchat(player.id, ("You got poisoned!"))
                        else:
                            await idchat(player.id, "%s has been poisoned!" % (character.name))
                elif inflict == 2 and character.status['Stun'] is False:
                    for player in self.players:
                        if player.name == character.name:
                            await idchat(player.id, ("You have been stunned and lost 100 energy!"))
                            character.energy -= 100
                        else:
                            await idchat(player.id, "%s has been stunned and lost 100 energy!" % (character.name))
                elif inflict == 3 and character.status['Paralysis'] is False:
                    character.status['Paralysis'] = True
                    for player in self.players:
                        if player.name == character.name:
                            await idchat(player.id, ("You have been paralyzed!"))
                        else:
                            await idchat(player.id, "%s has been paralyzed!" % (character.name))
                elif inflict == 4 and character.status['Toxic'] is False:
                    character.status['Toxic'] = True
                    for player in self.players:
                        if player.name == character.name:
                            await idchat(player.id, ("You are toxic!"))
                        else:
                            await idchat(player.id, "%s is toxic!" % (character.name))
                elif inflict == 5 and character.status['Sleep'] is False:
                    character.status['Sleep'] = True
                    for player in self.players:
                        if player.name == character.name:
                            await idchat(player.id, ("You have been put to sleep!"))
                        else:
                            await idchat(player.id, "%s has been put to sleep!" % (character.name))
                elif inflict == 6 and character.status['Blind'] is False:
                    character.status['Blind'] = True
                    for player in self.players:
                        if player.name == character.name:
                            await idchat(player.id, ("You have been blined!"))
                        else:
                            await idchat(player.id, "%s has been blined!" % (character.name))
                elif inflict == 7 and character.status['Panic'] is False:
                    character.status['Panic'] = True
                    for player in self.players:
                        if player.name == character.name:
                            await idchat(player.id, ("You have been put into a panic!"))
                        else:
                            await idchat(player.id, "%s has been put into a panic!" % (character.name))
                elif inflict == 8 and character.status['Bleed'] is False:
                    character.status['Bleed'] = True
                    for player in self.players:
                        if player.name == character.name:
                            await idchat(player.id, ("You begin to bleed!"))
                        else:
                            await idchat(player.id, "%s begins to bleed!" % (character.name))
                elif inflict == 11 and character.status['Horror'] is False:
                    damage = ceil(character.life / 4)
                    for player in self.players:
                        if player.name == character.name:
                            await idchat(player.id, ("Horrible images fill your vision. You claw at your eyes for %s damage!" % (damage)))
                            await self.takeDamage(player, damage)
                        else:
                            await idchat(player.id, "%s claws at their eyes for %s damage!" % (character.name, damage))

    async def playerTurn(self, player, target, escape):
        # commands = ['-fight', '-attack', '-check', '-use', '-escape']
        # notFound = True
        if player.lastmessage == '-fight' or player.lastmessage == '-attack':
            await self.damageRoll(player, target)
            player.energy -= player.weapon.energyuse
            if player.energy >= 1000 and target.life > 0:
                await idchat(player.id, ("You still have %s energy!" % (player.energy)))
            player.lastmessage = ''
            player.chargecount = 1
        elif player.lastmessage == '-check':
            for player in self.players:
                if player.name == player.name:
                    await idchat(player.id, blockify(("%s\n Life: %s\n Will: %s\nPower: %s\nGuard: %s\nSpeed: %s\n Luck: %s\n%s" %
                                                      (unbold(target.name), target.life, (target.will + target.statchange['will']),
                                                       (target.power + target.statchange['power']), (target.guard + target.statchange['guard']),
                                                       (target.speed + target.statchange['speed']),
                                                       (target.luck + target.statchange['luck']), target.description))))
                elif player.name == target.name:
                    await idchat(player.id, "%s is checking you out!" % (player.name))
                else:
                    await idchat(player.id, "%s is checking out %s!" % (player.name, target.name))
            player.energy -= 100
            if player.energy >= 1000 and target.life > 0:
                await idchat(player.id, ("You still have %s energy!" % (player.energy)))
            player.lastmessage = ''
        elif player.lastmessage[:5] == '-use ':
            itemname = smartCapitalize(player.lastmessage[5:])
            if itemname not in ITEM:
                await idchat(self.id, "'%s' does not exist!" % itemname)
            elif ITEM[itemname] in player.inventory:
                item = ITEM[itemname]
                if await item.useItemBattle(self, player, target, self.players, escape):
                    return True
            else:
                await idchat(player.id, "You don't have %s!" % (bold(itemname)))
            if player.energy >= 1000 and target.life > 0:
                await idchat(player.id, "You still have %s energy!" % (player.energy))
            player.lastmessage = ''
        elif player.lastmessage[:6] == '-cast ':
            spellname = smartCapitalize(player.lastmessage[6:])
            if spellname not in TECH:
                await idchat(player.id, "This spell does not exist!")
            elif TECH[spellname] in player.spells:
                spell = TECH[spellname]
                if spell.battle is False:
                    await idchat(player.id, "You can't use %s in this way." % (bold(spellname)))
                else:
                    for player in self.players:
                        if player.name == player.name:
                            await idchat(player.id, "%s" % (spell.usedtext))
                        else:
                            await idchat(player.id, "%s used %s!" % (player.name, bold(spell.name)))
                    player.energy -= item.energyuse
                    player.life = min(player.life + ceil(player.get('maxlife') * (spell.curelife / 100)), player.get('maxlife'))
                    if spell.curestatus == 0:
                        await player.clearStatusEffects()
                        await player.clearStatChanges()
                    for stat in player.statchange:
                        player.statchange[stat] += spell.buff[stat]
                    await target.evaluateStatus(target, spell.statusinflict, spell.statuschance)
            else:
                await idchat(player.id, "You don't know %s!" % (bold(spellname)))
            if player.energy >= 1000 and target.life > 0:
                await idchat(player.id, "You still have %s energy!" % (player.energy))
            player.lastmessage = ''
        elif player.lastmessage == '-escape':
            if escape is True:
                escaperoll = randint(1, 100)
                escapechance = ((player.life / player.get('maxlife')) * (player.get('speed') / target.get('speed')) + player.get('luck') * 0.002) * 100
                if escapechance >= escaperoll:
                    await idchat(player.id, "You escape!")
                    player.runaway += 1
                    player.lastmessage = ''
                    return True
                else:
                    await idchat(player.id, "You fail to escape!")
                    player.energy -= 200
                    if player.energy >= 1000 and target.life > 0:
                        await idchat(player.id, "You still have %s energy!" % (player.energy))
            else:
                await idchat(player.id, "You can not escape!")
            player.lastmessage = ''
        return False



    async def enemyTurn(self):
        target = choice(self.players)
        if target is not None:
            await self.damageRoll(self.enemy, target)
        self.enemy.energy -= self.enemy.enemyenergyuse



def sortEncounterList(self):
    return self.energy * 10000 + self.speed * 100 + self.luck


def getLocation(locationname):
    if locationname in LOCATION:
        return LOCATION[locationname]
    else:
        return None
