from enum import Enum

ITEM = {}
PLAYER = {}
MONSTER = {}
LOCATION = {}
TECH = {}
ENCOUNTERS = []

hostilelocationlist = ['Prison of Hope', 'Eldergrimm', 'The Bad Place', 'Eldergrimm Bandit Camp']
townlocationlist = ['Tarrow']


class EncType(Enum):
    NORMAL = 0
    BOSS = 1
    RAID = 2
    PVP = 3


class State(Enum):
    NORMAL = 0
    ENCOUNTER = 1
    SHOPPING = 2
    TRAINING = 3


Commands = {
    'Inventory': {
        '-stats': 'Shows your stats',
        '-inventory (-inv)': 'Shows your inventory',
        '-equip <item>': 'Equips the chosen item from your inventory',
        '-examine <item>': 'Examines the chosen item from your equipment or inventory',
        '-discard <item>': 'Discards the chosen item from your inventory',
    },

    'Travel': {
        '-travel': 'Shows the locations you can travel to',
        '-travel <location>': 'Travels to the chosen location',
        '-location (-loc)': 'Shows your current location',
        '-surroundings (-look)': 'Gives a description of your surroundings',
    },

    'Instance': {
        '-encounter (-enc)': 'If you are in a hostile area, this will begin a random encounter',
        '-encounter boss (-enc boss)': 'If you are in a hostile area that has a boss, this will start the boss fight',
        '-shop': 'If you are in an area with a shop, this will start shopping',
        '-trainer': 'If you are in an area with a trainer, this will start training',
    },

    'Other': {
        '-commands (-cmds)': 'Shows the relevant commands',
        '-commands all (-cmds all)': 'Shows all commands (Will be a big block of text)',
        '-leaderboards (-lbs)': 'Shows the different categories you can find leaderboards for',
        '-leaderboards <category> (-lbs <category>)': 'Shows the top 5 players in the category chosen',
    },

    'Battle': {
        '-fight (-attack)': "Uses your weapon's energy use to attack",
        '-use <item>': 'Uses an item from your inventory and subtracts its energy cost',
        '-check': "Uses 100 energy to check the enemy's stats",
        '-escape': "Uses 200 energy to attempt to run away",
    },

    'Shopping': {
        '-buy <item> <amount>': 'Buys the chosen amount of the chosen item',
        '-sell <item> <amount>': 'Sells the chosen amount of the chosen item',
        '-examine <item>': 'Examines an item from your inventory, equipment, or the shop',
        '-rumors': 'Ask the shopkeeper for rumors',
        '-leave': 'Leaves the shop',
    },

    'Training': {
        '-train <stat> <amount>': 'Spends potential to raise the chosen stat by the chosen amount',
        '-learn <skill|spell>': 'Spends potential based on the chosen skill|spell to learn it',
        '-examine <skill|spell>': 'Examines the chosen skill|spell',
        '-respec': 'Spend 2500 ides to regain all potential and lose all stats, skills, and spells',
        '-rumors': 'Ask the trainer for rumors',
        '-leave': 'Leaves the trainer',
    },

    'Debug': {
        '-imstuck': 'Pulls you out of combat/shopping/training. Only use this if you have to!',
    },
}


def clear():
    global PLAYER, MONSTER, ITEM, LOCATION, TECH, ENCOUNTERS
    PLAYER = {}
    MONSTER = {}
    ITEM = {}
    LOCATION = {}
    TECH = {}
    ENCOUNTERS = []
