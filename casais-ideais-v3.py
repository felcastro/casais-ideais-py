from enum import Enum
from random import randint
import threading
import time
import os
import math
import collections

class Queue:
        
    def __init__(self):
        self.elements = collections.deque()

    def empty(self):
        return len(self.elements) == 0

    def put(self, x):
        self.elements.append(x)

    def get(self):
        return self.elements.popleft()

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

class RulesReader(object):

    def readRules(self, rules):
        rulesList = rules.split("\n")
        couplesRegistrys = rulesList[0].split(" ")
        self.couples = int(couplesRegistrys[0])  
        self.registrys = int(couplesRegistrys[1])
        self.persons = [self.translatePerson(x, Gender.MALE, ind) if ind < self.couples
           else self.translatePerson(x, Gender.FEMALE, ind) 
           for ind, x in enumerate(rulesList[1:]) if x.strip() != ""]

    # Returns a Agent object from the string provided. 
    def translatePerson(self, personString, gender, index):
        personId = ""
        for c in personString:
            if not c in ["\t", " "]:
                personId += c
            else:
                break
        interests = personString[len(personId):].lstrip().rstrip()
        interests = interests.split(" ")
        interests = list(filter(lambda a: a != '', interests))
        # personString = " ".join(personString[len(personId):].split(""))
        return Agent(int(personId), gender, list(map(lambda x: int(x), interests)), index)
 
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

    # Check if there is possible partner at a 360 degree 2 positions range on the matrix.
    def checkPartners(self, persons):
        for p in persons:
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

    # Move the agent to a random empty neighbor or to a specific position.
    def walk(self, matrix, i = None, j = None):
        step = []
        if i != None and j != None:
            if mat.matrix[i][j].name == "-":
                step = [i, j]
        else:
            step = self.getNextStep(matrix)
        if step != []:
            self.i = step[0]
            self.j = step[1]

    # Returns a random position.
    def getNextStep(self, matrix):
        step = []
        neighbors = [n for n in matrix.getNeighbors(self) if n.name == "-"]
        if len(neighbors) - 1 > 0:
            rdmNeighbor = neighbors[randint(0, len(neighbors) - 1)]
            step = [rdmNeighbor.i, rdmNeighbor.j]
        return step

    # Returns the index of the closest registry from the agent.
    def getClosestRegistry(self, registrys):
        regs = []
        for r in registrys:
            regs.append(math.hypot(r[0] - self.i, r[1] - self.j))
        return regs.index(min(regs))

    # Bredth first algorithm to get best movement to a position from any position.
    def astar(self, start, matrix):
        frontier = Queue()
        frontier.put(start)
        came_from = {}
        came_from[start] = None
        while not frontier.empty():
            current = frontier.get()
            for next in matrix.getNeighbors(current):
                if next not in came_from:
                    frontier.put(next)
                    came_from[next] = current
        return came_from[matrix.matrix[self.i][self.j]]

    # Checks if one of the agent's neighbors are a registry.
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
        if self.couples < 11:
            for p in self.persons:
                string += repr(p) + "\n"
        else:
            for p in self.persons:
                string += "[" + str(p.id) + ", " + str(p.partner) + "], "
        return string

    # Return a new empty matrix.
    def newMatrix(self):
        matrix = []
        for i in range(self.dimension):
            matrix.append([])
            for j in range(self.dimension):
                matrix[i].append(Position("-"))
                matrix[i][j].i = i
                matrix[i][j].j = j
        return matrix

    # Randomly sets all obstacles on the matrix.
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

    # Randomly sets all registrys by the obstacles.
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

    # Randomly set all persons on the matrix.
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

    # Move a person from a position to its position.
    def movePerson(self, person, pos):
        self.matrix[pos[0]][pos[1]].name = "-"
        self.matrix[person.i][person.j].name = "M" if person.gender == Gender.MALE else "F"

    # Return all valid neighbors of a position
    def getNeighbors(self, pos):
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= pos.i - i < self.dimension and 0 <= pos.j - j < self.dimension:
                    if not (i == 0 and j == 0) and not self.matrix[pos.i - i][pos.j - j].name in ["O"]:
                        neighbors.append(self.matrix[pos.i - i][pos.j - j])
        return neighbors

    # Verify if maximum combination of couples was formed.
    def finish(self):
        for pOne in self.persons:
            if pOne.partner == 0:
                return False
            if pOne.partner != pOne.interests[0]:
                for pTwo in self.persons:
                    if pOne != pTwo and pOne.gender != pTwo.gender:
                        if pTwo.partner == 0:
                            return False
                        if pTwo.interests.index(pOne.id) < pTwo.interests.index(pTwo.partner) and pOne.interests.index(pTwo.id) < pOne.interests.index(pOne.partner):
                            return False
        return True

# Collect information from user to run the code.
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

# Run agents on environment.
finished = False
while not finished:
    for p in mat.persons:
        oldPos = [p.i, p.j]
        if p.goRegistry and not p.isOnRegistry(mat.registrys):
            reg = p.getClosestRegistry(mat.registrys)
            reg = mat.registrys[reg]
            path = p.astar(mat.matrix[reg[0]][reg[1]], mat)
            p.walk(mat.matrix, path.i, path.j)
        else:
            p.walk(mat)
        mat.movePerson(p, oldPos)
        try:
            p.checkPartners(mat.persons)
        except:
            pass
        os.system('cls' if os.name == 'nt' else 'clear')
        print(str(mat))
        finished = mat.finish()
        # time.sleep(0.03)
print("Casais máximos formados!")