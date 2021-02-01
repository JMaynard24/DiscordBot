from RPGFiles.Character import Character
from text_formatting import smartCapitalize
from os.path import isfile


class Enemy(Character):

    def __init__(self, name):
        super().__init__(name)
        self.image = None
        self.moneyaward = 0
        self.expaward = 0
        self.opening = 'Missing Opening?'
        self.statusinflict = 0
        self.statuschance = 0
        self.enemyenergyuse = 200
        self.droplist = {}
        self.isboss = False
        self.israidboss = False
        self.bossoutro = 'Missing Outro?'
        self.damagetext = 'Missing DamageText?'
        self.nodamagetext = 'Missing NoDamageText?'
        self.crittext = 'Missing CritText?'
        self.unlocklocations = []

    def getImage(self):
        image = 'RPGFiles/Art/Enemy/%s.png' % smartCapitalize(self.name)
        if isfile(image):
            return image
        else:
            return 'RPGFiles/Art/Enemy/NOPIC.png'
