from RPGFiles.lookup import PLAYER, MONSTER
from text_formatting import bold
from random import randint


class Character:
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.maxlife = 40
        self.life = 40
        self.maxmana = 10
        self.mana = 10
        self.maxfocus = 10
        self.focus = 10
        self.vigor = 10
        self.power = 10
        self.finesse = 10
        self.will = 10
        self.guard = 10
        self.magic = 10
        self.speed = 10
        self.luck = 10
        self.energy = 0
        self.critchance = 5
        self.isplayer = False
        self.description = 'This is %s, an adventurer just like you!' % self.name
        self.team = 0
        self.isguarding = False
        self.chargecount = 1
        self.skills = []
        self.spells = []

        self.status = {'Poison': False,
                       'Stun': False,
                       'Paralysis': False,
                       'Toxic': False,
                       'Sleep': False,
                       'Blind': False,
                       'Panic': False,
                       'Bleed': False,
                       'Sap': False,
                       'Silence': False,
                       'Horror': False
                       }
        self.statchange = {'maxlife': 0,
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
        self.elementalatk = {'Fire': 0,
                             'Elec': 0,
                             'Water': 0,
                             'Earth': 0,
                             'Psyche': 0,
                             }
        self.elementaldef = {'Fire': 0,
                             'Elec': 0,
                             'Water': 0,
                             'Earth': 0,
                             'Psyche': 0,
                             }


    def get(self, stat):
        return getattr(self, stat) + self.statchange[stat]


    async def setPlayer(self):
        if self.name not in PLAYER:
            PLAYER[self.name] = self
            self.isplayer = True


    async def setMonster(self):
        if self.name not in MONSTER:
            MONSTER[self.name] = self
            self.name = bold(self.name)


    async def clearStatusEffects(self):
        for i in self.status.keys():
            self.status[i] = False


    async def clearStatChanges(self):
        for i in self.statchange.keys():
            self.statchange[i] = 0
            self.statchange[i] += self.weapon.buff[i]
            if self.weapon.is2handed is False:
                self.statchange[i] += self.shield.buff[i]
            self.statchange[i] += self.armor.buff[i]
            self.statchange[i] += self.charm.buff[i]


    async def hitChance(self, target):
        chance = min(100, (self.speed / target.speed) * 50 + 50 + (self.luck * 0.0392) - (target.luck * 0.0392))
        chance = max(chance, 0)
        if self.status['Blind']:
            chance *= 0.5
        if chance >= randint(1, 100) or target.status['Paralysis'] or target.status['Sleep']:
            return True
        else:
            return False


    async def energyRecovery(self):
        self.energy += (self.speed * 5 + 95)


    def sortEncounterList(self):
        return self.energy * 10000 + self.speed * 100 + self.luck


#-------------------------------------------------------------------------------
