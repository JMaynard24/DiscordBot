from RPGFiles.lookup import ITEM
from text_formatting import idchat, bold, smartCapitalize
from math import ceil
from os.path import isfile


class Item:

    def __init__(self, name):
        ITEM[name] = self
        self.name = name
        self.typeof = ''
        self.is2handed = False
        self.isshield = False
        self.isarmor = False
        self.ischarm = False
        self.isconsumable = False
        self.energyuse = 400
        self.numofuses = 1
        self.curelife = 0
        self.curefocus = 0
        self.curemana = 0
        self.curestatus = -1     # -1 = no cure, 0 =  cure all, 1 = cure poison, 2 = cure toxic, 3 = cure blind, 4 = cure panic
        self.maxstacksize = 1
        self.statusinflict = 0   # -1 = random status, 0 = no status, 1+ look at status list
        self.statuschance = 0
        self.price = 0
        self.battleitem = False
        self.worlditem = False
        self.description = ''
        self.usedtext = ''
        self.damagereceivetext = 'Damage Recieve text missing {player} {damage}'
        self.damagedealtext = 'Damage Deal text missing {player} {damage}'
        self.critreceivetext = 'Crit Recieve text missing {player} {damage}'
        self.critdealtext = 'Crit Deal text missing {player} {damage}'
        self.nodamagedealtext = 'No Damage Deal Text Missing'
        self.nodamagereceivetext = 'No Damage Recieve Text Missing'
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


    async def useItem(self, player):
        for item in player.inventory:
            if item.name == self.name:
                player.inventory.remove(item)
                break
        await idchat(player.id, ("You use %s!" % (bold(self.name))))
        await idchat(player.id, ("%s!" % (self.usedtext)))
        player.life = min(player.life + ceil(player.get('maxlife') * (self.curelife / 100)), player.get('maxlife'))
        player.focus = min(player.focus + ceil(player.get('maxfocus') * (self.curefocus / 100)), player.get('maxfocus'))
        player.mana = min(player.mana + ceil(player.get('maxmana') * (self.curemana / 100)), player.get('maxmana'))


    async def useItemBattle(self, enc, player, target, players, escape):
        if self.battleitem is False:
            await idchat(self.id, "You can't use %s in this way." % (bold(self.name)))
        else:
            for p in players:
                if p.name == player.name:
                    await idchat(player.id, ("You use %s!" % (bold(self.name))))
                    await idchat(player.id, "%s" % (self.usedtext))
                else:
                    await idchat(player.id, "%s used %s!" % (player.name, bold(self.name)))
            player.energy -= self.energyuse
            player.life = min(player.life + ceil(player.get('maxlife') * (self.curelife / 100)), player.get('maxlife'))
            player.focus = min(player.focus + ceil(player.get('maxfocus') * (self.curefocus / 100)), player.get('maxfocus'))
            player.mana = min(player.mana + ceil(player.get('maxmana') * (self.curemana / 100)), player.get('maxmana'))
            if self.curestatus == 0:
                await player.clearStatusEffects()
            elif self.curestatus != -1:
                i = 0
                for status in player.status:
                    i += 1
                    if i == self.curestatus:
                        player.status[status] = False
            for stat in player.statchange:
                player.statchange[stat] += self.buff[stat]
            await enc.evaluateStatus(target, self.statusinflict, self.statuschance)
            player.inventory.remove(self)
            if self.name == 'Flask of Shadows':
                await idchat(self.id, "You escape!")
                player.runaway += 1
                player.lastmessage = ''
                return True

    def getImage(self):
        image = 'RPGFiles/Art/Icons/Item/%s.png' % smartCapitalize(self.name)
        if isfile(image):
            return image
        else:
            return 'RPGFiles/Art/Icons/NOPIC.png'


def checkItems():
    items = []
    for item in ITEM:
        image = 'RPGFiles/Art/Icons/Item/%s.png' % smartCapitalize(item)
        if not isfile(image):
            items.append(item)
    return items
