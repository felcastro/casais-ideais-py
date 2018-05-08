from enum import Enum
from random import randint
import threading
import time
import os
import math
import collections

class PriorityQueue:
        
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, x, priority):
        self.elements.append([x, priority])
        self.elements.sort(key=lambda x: x[1], reverse=True)

    def get(self):
        x = self.elements[-1]
        self.elements = self.elements[:-1]
        return x[0]

class Gender(Enum):
    MALE = 0
    FEMALE = 1

    def __str__(self):
        return self.name.title()

class Position(object):

    def __init__(self, name):
        self.name = name
        self.i = 0
        self.j = 0
        self.g = 1
        self.neighbors = []
    
    def __repr__(self):
        return "[" + str(self.i) + ", " + str(self.j) + "]"

    def __str__(self):
        if self.name == "M":
            string = "\x1b[0;30;44m" + "M" + "\x1b[0m"
        elif self.name == "F":
            string = "\x1b[0;30;41m" + "F" + "\x1b[0m"
        elif self.name == "R":
            string = "\x1b[5;30;42m" + "R" + "\x1b[0m"
        elif self.name == "O":
            string = "\x1b[6;30;47m" + "O" + "\x1b[0m"
        else:
            string = self.name
        return string

    def toStr(self):
        return "[" + str(self.i) + ", " + str(self.j) + "]"

class RulesReader(object):

    def readRules(self, rules):
        rulesList = rules.split("\n")
        couplesRegistrys = rulesList[0].split(" ")
        self.couples = int(couplesRegistrys[0])  
        self.registrys = int(couplesRegistrys[1])
        self.persons = [self.translatePerson(x, Gender.MALE, ind) if ind < self.couples
           else self.translatePerson(x, Gender.FEMALE, ind) 
           for ind, x in enumerate(rulesList[1:]) if x.strip() != ""]

    def translatePerson(self, personString, gender, index):
        personString = "".join(personString.split())
        print(personString)
        return Agent(int(personString[0]), gender, list(map(lambda x: int(x), list(personString[1:]))), index)
 
class Agent(object):
    
    def __init__(self, id, gender, interests, index):
        self.id = id
        self.gender = gender
        self.interests = interests
        self.index = index
        self.partner = 0
        self.goRegistry = False
        self.i = 0
        self.j = 0
        
    def __repr__(self):
        return "[Id: %s, Genero: %s, Parceiro atual: %s, Interesses: %s, I atual: %s, J atual: %s, Go reg: %s]" % (self.id, str(self.gender), self.partner, self.interests, self.i, self.j, self.goRegistry)

    def checkPartners(self, persons):
        for ind, p in enumerate(persons):
            if ind != self.index:
                if self.id != p.id and self.gender != p.gender:
                    if self.i - 2 <= p.i <= self.i + 2 and self.j - 2 <= p.j <= self.j + 2:
                        if self.partner == 0 and p.partner == 0:
                            self.partner = p.id
                            self.goRegistry = True
                            p.partner = self.id
                            p.goRegistry = True
                        elif self.partner == 0 and p.interests.index(self.id) < p.interests.index(p.partner):
                            for prsn in persons:
                                if prsn.id == p.partner and prsn.gender != p.gender:
                                    prsn.partner = 0
                                    prsn.goRegistry = False
                            self.partner = p.id
                            self.goRegistry = True
                            p.partner = self.id
                            p.goRegistry = True
                        elif p.partner == 0 and self.interests.index(p.id) < self.interests.index(self.partner):
                            for prsn in persons:
                                if prsn.id == self.partner and prsn.gender != self.gender:
                                    prsn.partner = 0
                                    prsn.goRegistry = False
                            self.partner = p.id
                            self.goRegistry = True
                            p.partner = self.id
                            p.goRegistry = True
                        elif self.interests.index(p.id) < self.interests.index(self.partner) and p.interests.index(self.id) < p.interests.index(p.partner):
                            for prsn in persons:
                                if prsn.id == p.partner and prsn.gender != p.gender:
                                    prsn.partner = 0
                                    prsn.goRegistry = False
                                elif prsn.id == self.partner and prsn.gender != self.gender:
                                    prsn.partner = 0
                                    prsn.goRegistry = False
                            self.partner = p.id
                            self.goRegistry = True
                            p.partner = self.id
                            p.goRegistry = True

    def walk(self, matrix, i = None, j = None):
        if i != None and j != None:
            step = [i, j]
        else:
            step = self.getNextStep(matrix)
        self.i = step[0]
        self.j = step[1]

    def getNextStep(self, matrix):
        step = self.getRandomMovement(matrix)
        while matrix[step[0]][step[1]].name != "-":
            step = self.getRandomMovement(matrix)
        return step

    def getRandomMovement(self, matrix):
        newI = self.i
        newJ = self.j
        moveType = randint(0, 1)
        if moveType == 0:
            if newI <= 0: 
                newI += 1
            elif newI >= len(matrix[0]) - 1: 
                newI -= 1
            else:
                if randint(0, 1) > 0:
                    newI += 1
                else:
                    newI -= 1
        else:
            if newJ <= 0:
                newJ += 1
            elif newJ >= len(matrix) - 1:
                newJ -= 1
            else:
                if randint(0, 1) > 0:
                    newJ += 1
                else:
                    newJ -= 1
        return [newI, newJ]

    def getClosestRegistry(self, registrys):
        regs = []
        for r in registrys:
            regs.append(math.hypot(r[0] - self.i, r[1] - self.j))
        return regs.index(min(regs))

    def astar2(self, start, goal):
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        while not frontier.empty():
            current = frontier.get()

            if current == goal:
                break
            
            for next in current.neighbors:
                new_cost = cost_so_far[current] + current.g
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current
        return came_from
    
    def heuristic(self, goal, next):
        return math.sqrt(math.pow(goal.i - next.i, 2) + math.pow(goal.j - next.j, 2))

    def isOnRegistry(self, registrys):
        for r in registrys:
            if self.i - 1 <= r[0] <= self.i + 1 and self.j - 1 <= r[1] <= self.j + 1:
                self.goRegistry = False
                return True
        return False

class Matrix(object):

    def __init__(self, dimension, couples):
        self.dimension = dimension
        self.matrix = self.newMatrix()
        self.obstacles = []
        self.registrys = []
        self.persons = []
        self.couples = couples

    def __repr__(self):
        string = '\n'.join([''.join(["" + str(j) + " " for j in i]) for i in self.matrix]) + "\n\n"
        if self.couples < 5:
            for p in self.persons:
                string += repr(p) + "\n"
        return string

    def newMatrix(self):
        matrix = []
        for i in range(self.dimension):
            matrix.append([])
            for j in range(self.dimension):
                matrix[i].append(Position("-"))
                matrix[i][j].i = i
                matrix[i][j].j = j
        return matrix

    def setObstacles(self):
        self.obstacles = []
        matrixHalf = int(round(self.dimension / 2))
        numberOfObstacles = int(round(self.dimension / 5))
        obstacleSpacing = int(round(self.dimension / numberOfObstacles))
        i = int(round(obstacleSpacing / 2))
        while i < self.dimension:
            sizeRandomizer = randint(0, int(round((0.2 * matrixHalf))))
            topPosition = randint(2, matrixHalf - 3)
            bottomPosition = topPosition + matrixHalf
            while sizeRandomizer > 0:
                if randint(0, 1) > 0:
                    topPosition += 1
                else: 
                    bottomPosition -= 1
                sizeRandomizer -= 1
            j = topPosition
            while j < bottomPosition:
                mat.matrix[j][i].name = "O"
                self.obstacles.append([j, i])
                j += 1
            i += obstacleSpacing

    def setRegistrys(self, registrys):
        self.registrys = []
        for i in range(registrys):
            pos = self.obstacles[randint(0, len(self.obstacles) - 1)]
            if randint(0, 1) > 0:
                pos[1] += 1
            else: 
                pos[1] -= 1
            while [pos[0], pos[1]] in self.registrys:
                pos = self.obstacles[randint(0, len(self.obstacles) - 1)]
                if randint(0, 1) > 0:
                    pos[1] += 1
                else: 
                    pos[1] -= 1
            self.matrix[pos[0]][pos[1]].name = "R"
            self.registrys.append(pos)

    def setPersons(self, persons):
        self.persons = persons
        i = randint(0, self.dimension - 1)
        j = randint(0, self.dimension - 1)
        for idx, p in enumerate(self.persons):
            while self.matrix[i][j].name != "-":
                i = randint(0, self.dimension - 1)
                j = randint(0, self.dimension - 1)
            gndr = "M" if p.gender == Gender.MALE else "F"
            self.matrix[i][j].name = gndr
            p.i = i
            p.j = j

    def movePerson(self, person, pos):
        self.matrix[pos[0]][pos[1]].name = "-"
        self.matrix[person.i][person.j].name = "M" if person.gender == Gender.MALE else "F"

    def updateNeighbors(self):
        for i in self.matrix:
            for j in i:
                j.neighbors = []
                for k in range(-1, 2):
                    for l in range(-1, 2):
                        if 0 <= j.i - k < self.dimension and 0 <= j.j - l < self.dimension:
                            if not (k == 0 and l == 0) and not self.matrix[j.i - k][j.j - l].name in ["O", "M", "F"]:
                                j.neighbors.append(self.matrix[j.i - k][j.j - l])

    def finish(self):
        # TODO - Verify if no more couples can be formed
        for p in self.persons:
            pass

# Collect information to run the code.
os.system('cls' if os.name == 'nt' else 'clear')
print("Welcome to kouplez!\nPlease inform the name of the file containing the desired rules to load. (default = 3Casais.txt)")
print(os.listdir("Rules"))
rulesFile = "Rules/" + input()
if rulesFile == "Rules/":
    rulesFile = "Rules/3Casais.txt"
print("File: " + rulesFile)
with open(rulesFile) as f:
    rulesString = f.readlines()
rulesString[-1] = rulesString[-1].rstrip()
rulesString = "".join(rulesString)
print("Please inform the dimension of the matrix. (default = 20)")
dimension = input()
if dimension == "":
    dimension = 20
dimension = int(dimension)
print("Dimension: " + str(dimension))

# Prepare the environment.
rules = RulesReader()
rules.readRules(rulesString)
mat = Matrix(dimension, rules.couples)
mat.setObstacles()
mat.setRegistrys(rules.registrys)
mat.setPersons(rules.persons)
mat.updateNeighbors()

# Run agents on environment.
while True:
    for p in mat.persons:
        oldPos = [p.i, p.j]
        if p.goRegistry and not p.isOnRegistry(mat.registrys):
            reg = p.getClosestRegistry(mat.registrys)
            reg = mat.registrys[reg]
            # print(mat.matrix[p.i][p.j])
            # print(mat.matrix[p.i][p.j].neighbors)
            # print(mat.matrix[reg[0]][reg[1]])
            path = p.astar2(mat.matrix[p.i][p.j], mat.matrix[reg[0]][reg[1]])
            print(str(path))
            time.sleep(100)
            # print(path[0].toStr())
            p.walk(mat.matrix, path[0].i, path[0].j)
        else:
            p.walk(mat.matrix)
        mat.movePerson(p, oldPos)
        mat.updateNeighbors()
        try:
            p.checkPartners(mat.persons)
        except:
            pass
        os.system('cls' if os.name == 'nt' else 'clear')
        print(str(mat))
        time.sleep(0.03)

