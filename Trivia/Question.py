import os
from os.path import isfile

questionPool = {}


class Question:

    def __init__(self, question):
        self.category = 'Missing Category'
        self.question = question
        self.answer = 'Missing Answer'


async def addQuestion(c, q, a):
    newQuestion = Question(q)
    newQuestion.category = c
    newQuestion.answer = a
    if c in questionPool:
        questionPool[c].append(newQuestion)
    else:
        questionPool[c] = [newQuestion]
    saveQuestions()


def saveQuestions():
    for category in questionPool:
        fileobj = open("Trivia/Files/QuestionCategories/%s.temp.txt" % category, "w+")
        for question in questionPool[category]:
            fileobj.write("question: \"%s\"\nanswer: \"%s\"\n\n" % (question.question, question.answer))
        fileobj.close()
        if isfile("Trivia/Files/QuestionCategories/%s.txt" % category) is True:
            os.remove("Trivia/Files/QuestionCategories/%s.txt" % category)
        os.rename("Trivia/Files/QuestionCategories/%s.temp.txt" % category, "Trivia/Files/QuestionCategories/%s.txt" % category)


def loadQuestions():
    for filename in os.listdir("Trivia/Files/QuestionCategories"):
        fileobj = open("Trivia/Files/QuestionCategories/%s" % filename)
        data = fileobj .readlines()
        fileobj .close()
        currentItem = None
        for line in data:
            if line.strip() == '':
                continue
            parsed = line.split(': ', 1)
            if parsed[0] == 'question':
                newItem = True
                question = eval(parsed[1])
                currentItem = Question(question)
                currentItem.category = filename[:-4]
                if currentItem.category in questionPool:
                    questionPool[currentItem.category].append(currentItem)
                elif newItem:
                    questionPool[currentItem.category] = [currentItem]
            else:
                newItem = False
                attr = parsed[0].lower()
                val = parsed[1]
                setattr(currentItem, attr, eval(val))
