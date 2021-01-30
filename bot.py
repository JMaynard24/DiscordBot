import discord
import RPGFiles.RPG as RPG
import RPGFiles.admin as admin
import Trivia.Trivia as trivia
import text_formatting
import os
from dotenv import load_dotenv
load_dotenv()


TEST = True

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

rpgStringSymbol = '-'
adminSymbol = '$'


@client.event
async def on_ready():
    global rpgChannel
    global triviaChannel
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name='Discord RPG'))
    if TEST is True:
        rpgChannel = client.get_channel(os.environ.get("test-rpg"))
        triviaChannel = client.get_channel(os.environ.get("test-trivia"))
    else:
        rpgChannel = client.get_channel(os.environ.get("real-rpg"))
        triviaChannel = client.get_channel(os.environ.get("real-trivia"))
    text_formatting.setRPGChannel(rpgChannel)
    text_formatting.setTriviaChannel(triviaChannel)
    text_formatting.setClient(client)
    print("\n\n")
    await RPG.initializeGame()
    trivia.initializeTrivia()


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print("%s - %s: %s" % (message.channel, message.author, message.content))
    if message.content.startswith(rpgStringSymbol):
        await RPG.handleCommand(message)
    elif message.content.startswith(adminSymbol):
        await admin.handleAdminCommand(message)
    elif message.channel == triviaChannel:
        await trivia.handleTriviaCommand(message)

test = input("T for test: ")

if test in "Tt":
    client.run(os.environ.get("test-token"))
else:
    client.run(os.environ.get("real-token"))
