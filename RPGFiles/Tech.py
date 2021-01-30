from RPGFiles.lookup import TECH
from text_formatting import idchat, bold
from math import ceil
from MathUtility import is_number


class Tech:

    def __init__(self, name):
        TECH[name] = self
        self.name = name
        self.image = None
        self.type = ''
        self.prereq = None
        self.energyuse = 150
        self.pointuse = 0
        self.curelife = 0
        self.curestatus = -1     # -1 = no cure, 0 =  cure all, 1 = cure poison, 2 = cure toxic, 3 = cure blind, 4 = cure panic
        self.dmg = 0
        self.energydmg = 0
        self.battle = True
        self.world = False
        self.dmgtype = 'Physical'
        self.statusinflict = 0
        self.statuschance = 0
        self.description = 'Description Missing?'
        self.dealtext = 'DealText Missing? {player} {damage}'
        self.receivetext = 'Receivetext Missing? {player} {damage}'
        self.learntext = 'Missing learn text?'
        self.buff = {'maxlife': 0,
                     'maxmana': 0,
                     'maxfocus': 0,
                     'power': 0,
                     'finesse': 0,
                     'will': 0,
                     'guard': 0,
                     'magic': 0,
                     'speed': 0,
                     'luck': 0,
                     'critchance': 0,
                     }
        self.debuff = {'maxlife': 0,
                       'maxmana': 0,
                       'maxfocus': 0,
                       'power': 0,
                       'finesse': 0,
                       'will': 0,
                       'guard': 0,
                       'magic': 0,
                       'speed': 0,
                       'luck': 0,
                       'critchance': 0,
                       }
        self.buffelementalatk = {'Fire': 0,
                                 'Elec': 0,
                                 'Water': 0,
                                 'Earth': 0,
                                 'Psyche': 0,
                                 }
        self.buffelementaldef = {'Fire': 0,
                                 'Elec': 0,
                                 'Water': 0,
                                 'Earth': 0,
                                 'Psyche': 0,
                                 }

    async def useSpell(self, player):
        await idchat(player.id, ("You use %s!" % (bold(self.name))))
        await idchat(player.id, ("%s!" % (self.usedtext)))
        player.life = min(player.life + ceil(player.get('maxlife') * (self.curelife / 100)), player.get('maxlife'))
        player.focus = min(player.focus + ceil(player.get('maxfocus') * (self.curefocus / 100)), player.get('maxfocus'))
        player.mana = min(player.mana + ceil(player.get('maxmana') * (self.curemana / 100)), player.get('maxmana'))
        player.save()


    async def useSkill(self, player):
        await idchat(player.id, ("You use %s!" % (bold(self.name))))
        await idchat(player.id, ("%s!" % (self.usedtext)))
        player.life = min(player.life + ceil(player.get('maxlife') * (self.curelife / 100)), player.get('maxlife'))
        player.focus = min(player.focus + ceil(player.get('maxfocus') * (self.curefocus / 100)), player.get('maxfocus'))
        player.mana = min(player.mana + ceil(player.get('maxmana') * (self.curemana / 100)), player.get('maxmana'))
        player.save()



    async def useTechBattle(self, player, chars, players, message, target, escape):
        if self.battle is False:
            await idchat(self.id, "You can't use %s in this way." % (bold(self.name)))
        else:
            for p in players:
                if p.name == player.name:
                    await idchat(player.id, ("You use %s!" % (bold(self.name))))
                else:
                    await idchat(player.id, "%s used %s!" % (player.name, bold(self.name)))
            player.energy -= self.energyuse
            player.life = min(player.life + ceil(player.get('maxlife') * (self.curelife / 100)), player.get('maxlife'))
            player.focus = min(player.focus + ceil(player.get('maxfocus') * (self.curefocus / 100)), player.get('maxfocus'))
            player.mana = min(player.mana + ceil(player.get('maxmana') * (self.curemana / 100)), player.get('maxmana'))
            if self.curestatus == 0:
                await self.clearStatusEffects()
                await self.clearStatChanges()
            for stat in player.statchange:
                player.statchange[stat] += self.buff[stat]
            await target.evaluateStatus(player, message, self.statusinflict, self.statuschance)
            if self.name == 'ESCAPE SKILL/SPELL':
                await idchat(self.id, "You escape!")
                player.runaway += 1
                player.lastmessage = ''
                return True

    async def meditateconcentrate(self, player, command, amount):
        if is_number(amount) or amount == 'all':
            if amount != 'all':
                amount = int(amount)
            if command == '-meditate' or command == '-med':
                if 'Meditate' not in player.skills:
                    await idchat(player.id, ("You don't know how to Meditate!"))
                    return
                if amount == 'all':
                    amount = player.mana
                maxamount = player.get('maxfocus') - player.focus
                if amount > maxamount:
                    amount = maxamount
                if amount == 0:
                    await idchat(player.id, ("You already had full Focus!"))
                    return
                if amount > player.mana:
                    amount = player.mana
                if amount == 0:
                    await idchat(player.id, ("You don't have any Mana to meditate!"))
                    return
                player.mana -= amount
                player.focus += amount
                await idchat(player.id, ("You used %s Mana to regain %s Focus!" % (amount, amount)))
                await player.save()
            if command == '-concentrate' or command == '-con':
                if 'Concentrate' not in player.skills:
                    await idchat(player.id, ("You don't know how to Concentrate!"))
                    return
                if amount == 'all':
                    amount = player.focus
                maxamount = player.get('maxmana') - player.mana
                if amount > maxamount:
                    amount = maxamount
                if amount == 0:
                    await idchat(player.id, ("You already had full Mana!"))
                if amount > player.focus:
                    amount = player.focus
                if amount == 0:
                    await idchat(player.id, ("You don't have any Focus to concentrate!"))
                    return
                player.focus -= amount
                player.mana += amount
                await idchat(player.id, ("You used %s Focus to regain %s Mana!" % (amount, amount)))
                await player.save()
        else:
            await idchat(player.id, ("Amount must be a number or 'all'-"))
