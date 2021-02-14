import os
from os.path import isfile
import time
import asyncio
import math
import operator
from random import randint
from text_formatting import triviaChat, blockify, nameFromID, triviaClear
from Trivia.Question import questionPool, loadQuestions, addQuestion
from MathUtility import is_number

players = {}


class Trivia:

    def __init__(self, categories, amount):
        self.amount = amount
        self.categories = categories
        self.questions = []
        self.skip = []
        self.currentScores = {}
        self.questionAmount = 0
        self.lastAnswer = ['Player', 'Answer']
        self.currentAnswer = 'N/A'
        self.currentBlanks = ''
        self.next = False
        self.running = False
        self.startTime = 0

    async def stop(self):
        global triviaBot
        await triviaClear()
        await triviaChat("Finished the game! Scores:")
        await leaderBoards(self.currentScores)
        await triviaChat("Overall:")
        await leaderBoards(players)
        self.running = False
        self.currentScores = {}
        self.amount = 0
        self.savePlayers()
        triviaBot = None

    async def loop(self):
        while self.amount > 0:
            await asyncio.sleep(1)
            self.next = False
            r = randint(0, self.questionAmount - 1)
            q = self.questions[r]
            while q in self.skip:
                r = randint(0, self.questionAmount - 1)
                q = self.questions[r]
            self.skip.append(q)
            if self.questionAmount == len(self.skip):
                self.amount = 0
            self.currentAnswer = q.answer
            self.currentBlanks = ''
            self.blankify(0)
            await triviaChat("(%s) %s  :  %s" % (q.category, q.question, self.currentBlanks))
            self.startTime = time.time()
            check = 0
            while not self.next:
                await asyncio.sleep(1)
                t = time.time()
                if self.startTime + 180 < t and check == 5:
                    check += 1
                    await triviaChat("Time's up! The answer was '%s'!" % q.answer)
                    self.next = True
                    self.amount -= 1
                elif self.startTime + 150 < t and check == 4:
                    check += 1
                    self.blankify(50)
                    await triviaChat("0:30 left! %s" % self.currentBlanks)
                elif self.startTime + 120 < t and check == 3:
                    check += 1
                    self.blankify(40)
                    await triviaChat("1:00 left! %s" % self.currentBlanks)
                elif self.startTime + 90 < t and check == 2:
                    check += 1
                    self.blankify(30)
                    await triviaChat("1:30 left! %s" % self.currentBlanks)
                elif self.startTime + 60 < t and check == 1:
                    check += 1
                    self.blankify(20)
                    await triviaChat("2:00 left! %s" % self.currentBlanks)
                elif self.startTime + 30 < t and check == 0:
                    check += 1
                    self.blankify(10)
                    await triviaChat("2:30 left! %s" % self.currentBlanks)
        await self.stop()

    async def checkAnswer(self):
        if self.lastAnswer[1].lower() == self.currentAnswer.lower():
            await self.rewardPoints(self.lastAnswer[0])

    async def rewardPoints(self, person):
        points = math.floor(self.startTime + 300 - time.time())
        if person.id in self.currentScores:
            self.currentScores[person.id] += points
        else:
            self.currentScores[person.id] = points
        if person.id in players:
            players[person.id] += points
        else:
            players[person.id] = points
        await triviaChat("%s got it and gained %s points for a total of %s! The correct answer was '%s'!" % (person.name, points, players[person.id], self.currentAnswer))
        self.savePlayers()
        self.next = True
        self.amount -= 1

    async def startTrivia(self):
        for category in self.categories:
            for question in questionPool[category.title()]:
                self.questions.append(question)
        self.questionAmount = len(self.questions)
        await self.loop()

    def savePlayers(self):
        fileobj = open("Trivia/Files/Players.temp.txt", "w")
        for player in players:
            fileobj.write("%s: %s\n" % (player, players[player]))
        fileobj.close()
        if isfile("Trivia/Files/Players.txt") is True:
            os.remove("Trivia/Files/Players.txt")
        os.rename("Trivia/Files/Players.temp.txt", "Trivia/Files/Players.txt")

    def blankify(self, percent):
        blankCharacters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        newText = ''
        blankAmount = 0
        shownAmount = 0
        if self.currentBlanks != '':
            for character in self.currentBlanks:
                if character == '-':
                    blankAmount += 1
                elif character in blankCharacters:
                    shownAmount += 1
            newText = self.currentBlanks
            amountToShow = math.floor((blankAmount + shownAmount) * (percent / 100)) - shownAmount
            if amountToShow == 0 and blankAmount > 1:
                amountToShow = 1
            while amountToShow > 0 and '-' in newText:
                n = randint(0, len(newText) - 1)
                if newText[n] == '-':
                    s = list(newText)
                    s[n] = self.currentAnswer[n]
                    newText = "".join(s)
                    amountToShow -= 1
            self.currentBlanks = newText
        else:
            for character in self.currentAnswer:
                if character in blankCharacters:
                    self.currentBlanks += '-'
                else:
                    self.currentBlanks += character


def loadPlayers():
    fileobj = open("Trivia/Files/Players.txt")
    data = fileobj .readlines()
    fileobj .close()
    for line in data:
        if line.strip() == '':
            continue
        parsed = line.split(': ', 1)
        players[eval(parsed[0])] = eval(parsed[1])
    print("TRIVIA PLAYERS: %s" % players)


async def handleTriviaCommand(message):
    global triviaBot
    if message.content == '!start':
        await triviaChat("Start should be in this format: '!start <number of questions> <categories seperated by ',' or all>'")
    elif message.content[:7] == '!start ':
        message.content = message.content.lower()
        split = message.content.split(" ")
        if len(split) >= 3 and is_number(split[1]):
            categories = []
            if split[2] != 'all':
                categoriesCheck = split[2].split(',')
                for category in categoriesCheck:
                    if category.title() in questionPool:
                        categories.append(category)
                if len(categories) > 0:
                    triviaBot = Trivia(categories, int(split[1]))
                    await triviaBot.startTrivia()
            else:
                for category in questionPool:
                    categories.append(category)
                triviaBot = Trivia(categories, int(split[1]))
                await triviaBot.startTrivia()
        else:
            await triviaChat("Start should be in this format: '!start <number of questions> <categories seperated by ',' or all>'")
    elif message.content == '!add':
        await triviaChat("Questions should be added in this format: '!add (Category|Question|Answer)' (ex: !add (FinalFantasy|What are the iconic yellow chickens called?|Chocobo) )")
    elif message.content[:5] == '!add ':
        cmd = message.content[5:]
        print(cmd)
        if len(cmd) > 0:
            split2 = cmd[1:len(cmd) - 1].split("|")
            print(split2)
            if len(split2) == 3:
                await addQuestion(split2[0].title(), split2[1], split2[2].title())
                await triviaChat("Question has been added!")
            else:
                await triviaChat("Questions should be added in this format: '!add (Category|Question|Answer)' (ex: !add (FinalFantasy|What are the iconic yellow chickens called?|Chocobo) )")
        else:
            await triviaChat("Questions should be added in this format: '!add (Category|Question|Answer)' (ex: !add (FinalFantasy|What are the iconic yellow chickens called?|Chocobo) )")
    elif message.content == '!categories':
        text = ''
        for c in questionPool:
            text += "%s : %s\n" % (c, len(questionPool[c]))
        await triviaChat(blockify(text))
    elif message.content == '!stop':
        if triviaBot is not None:
            triviaBot.stop()
            triviaBot = None
            await triviaChat("The trivia bot has been stopped!")
        else:
            await triviaChat("The trivia bot is not running!")
    elif message.content == '!leaderboards' or message.content == '!lbs':
        await leaderBoards()
    else:
        if triviaBot is not None:
            triviaBot.lastAnswer = [message.author, message.content]
            await triviaBot.checkAnswer()


def initializeTrivia():
    loadQuestions()
    loadPlayers()


async def leaderBoards(list):
    newlist = {}
    for player in list:
        newlist[player] = list[player]
    sortedlist = sorted(newlist.items(), key=operator.itemgetter(1))
    sortedlist.reverse()
    while len(sortedlist) < 10:
        sortedlist.append('No Data')
    text = ""
    count = 0
    while count < 10:
        if sortedlist[count] != 'No Data':
            text += "%s. %s: %s\n" % (count + 1, nameFromID(sortedlist[count][0]), sortedlist[count][1])
        count += 1
    await triviaChat(blockify(text))

triviaBot = None
