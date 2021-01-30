from RPGFiles.lookup import Commands
import asyncio
import discord

client = None
rpgChannel = None
triviaChannel = None


# -----------------------------------------------------------------------------


def setClient(c):
    global client
    client = c


# -----------------------------------------------------------------------------


async def chat(message, text):
    await asyncio.sleep(.5)
    while len(text) > 1800:
        await asyncio.sleep(.5)
        splitText = text[:1800] + "```"
        text = "```" + text[1800:]
        await message.author.send(splitText)
    await message.author.send(text)


# -----------------------------------------------------------------------------



async def channelchat(message, text):
    await asyncio.sleep(.5)
    while len(text) > 1800:
        await asyncio.sleep(.5)
        splitText = text[:1800] + "```"
        text = "```" + text[1800:]
        await message.channel.send(splitText)
    await message.channel.send(text)


# -----------------------------------------------------------------------------


async def idchat(id, text, files=None):
    id = client.get_user(id)
    await asyncio.sleep(.5)
    while len(text) > 1800:
        await asyncio.sleep(.5)
        splitText = text[:1800] + "```"
        text = "```" + text[1800:]
        await id.send(splitText)
    if files is not None:
        list = []
        for file in files:
            list.append(discord.File(file))
        await id.send(text, files=list)
    else:
        await id.send(text)


# -----------------------------------------------------------------------------



async def send_message(message, text):
    while len(text) > 1800:
        await asyncio.sleep(.5)
        splitText = text[:1800] + "```"
        text = "```" + text[1800:]
        await message.author.send(splitText)
    await message.author.send(text)


# -----------------------------------------------------------------------------


async def rpgChat(text):
    await asyncio.sleep(1)
    await rpgChannel.send(text)


# -----------------------------------------------------------------------------


async def triviaChat(text):
    await asyncio.sleep(1)
    await triviaChannel.send(text)


# -----------------------------------------------------------------------------


async def triviaClear():
    while True:
        await asyncio.sleep(1)
        counter = 0
        async for message in triviaChannel.history(limit=10):
            counter += 1
        if counter > 1:
            await asyncio.sleep(1)
            await triviaChannel.purge()
        else:
            break


# -----------------------------------------------------------------------------


def setRPGChannel(channel):
    global rpgChannel
    rpgChannel = channel


# -----------------------------------------------------------------------------


def setTriviaChannel(channel):
    global triviaChannel
    triviaChannel = channel


# -----------------------------------------------------------------------------



def bold(text):
    return "**" + text + "**"


# -----------------------------------------------------------------------------



def unbold(text):
    return text[2:len(text) - 2]


# -----------------------------------------------------------------------------


def italics(text):
    return "*" + text + "*"


# -----------------------------------------------------------------------------



def underline(text):
    return "__" + text + "__"


# -----------------------------------------------------------------------------



def blockify(text):
    return "```\n" + text + "```"


# -----------------------------------------------------------------------------



def single_blockify(text):
    return "`" + text + "`"


# -----------------------------------------------------------------------------



def nameFromID(id):
    id = client.get_user(id)
    return id.name


# -----------------------------------------------------------------------------



def createCommandsBlock(types):
    text_block = ''
    for type in types:
        if type in Commands:
            text_block += type + '\n'
            for command in Commands[type]:
                text_block += "  " + command + "  :  " + Commands[type][command] + '\n'
    return text_block


# -----------------------------------------------------------------------------


async def allCommands(message):
    types = []
    for type in Commands:
        types.append(type)
        if len(types) == 4:
            await chat(message, blockify(createCommandsBlock(types)))
            types = []


#-------------------------------------------------------------------------------


def smartCapitalize(text):
    skipWords = ['of', 'the', 'in', 'a', 'an', 'for', 'and', 'nor', 'but', 'so', 'yet', 'at', 'by', 'on', 'to']
    newText = text.lower()
    newerText = ''
    splitText = newText.split(' ')
    words = len(splitText)
    i = 1
    for j in splitText:
        if j not in skipWords:
            newerText += j.capitalize()
        elif i == 1:
            newerText += j.capitalize()
        else:
            newerText += j
        if i < words:
            newerText += ' '
        i += 1
    return newerText


#-------------------------------------------------------------------------------
