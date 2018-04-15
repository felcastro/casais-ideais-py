from enum import Enum
from random import randint
import threading
import time
import os

class Position(object):
    
    def __init__(self, posType, name):
        self.posType = posType
        self.name = name
        self.f = 0
        self.g = 0
        self.h = 0
        

class Gender(Enum):
    MALE = 0
    FEMALE = 1

class Person(object):
    
    def __init__(self, personid, gender, interests):
        self.personid = personid
        self.gender = gender
        self.interests = interests
        self.partner = 0
        
    def __repr__(self):
        return "[Id: %s, Genero: %s, Parceiro atual: %s, Interesses: %s, X atual: %s, Y atual: %s]" % (self.personid, self.gender.name.lower(), self.partner, self.interests, self.x, self.y)
        
class Agent (threading.Thread):
    
   def __init__(self, idx, delay):
      threading.Thread.__init__(self)
      self.idx = idx
      self.delay = delay
      
   def run(self):
      startAgent(self.idx, self.delay)
          
def startAgent(idx, delay):
    while True:
        newX = persons[idx].x
        newY = persons[idx].y
        moveType = randint(0, 1)
        if moveType == 0:
            if newX <= 0: 
                newX += 1
            elif newX >= len(matrix[0]) - 1: 
                newX -= 1
            else:
                if randint(0, 1) > 0:
                    newX += 1
                else:
                    newX -= 1
        else:
            if newY <= 0:
                newY += 1
            elif newY >= len(matrix) - 1:
                newY -= 1
            else:
                if randint(0, 1) > 0:
                    newY += 1
                else:
                    newY -= 1
        threadLock.acquire()
        walked = walk(persons[idx].x, persons[idx].y, newX, newY)
        if walked:
            persons[idx].x = newX
            persons[idx].y = newY
        try: 
            checkNearbyPartners(idx, persons[idx].x, persons[idx].y)
        except:
            False
        screen = "Agente atual: " + repr(persons[idx]) + "\n" + matrixToString(matrix) + "\n" + getStatus() + "\n" 
        os.system('cls' if os.name == 'nt' else 'clear')
        print(screen)
        threadLock.release()
        time.sleep(delay)
        
        
def checkNearbyPartners(idx, x, y):
    for p in persons:
        if x - p.x in range(-2, 3) and y - p.y in range(-2, 3) and not p.gender == persons[idx].gender and not persons[idx].partner == p.personid:
            if persons[idx].partner == 0 and p.partner == 0:
                persons[idx].partner = p.personid
                p.partner = persons[idx].personid
            elif persons[idx].partner == 0 and p.interests.index(persons[idx].personid) < p.interests.index(p.partner):
                for prsn in persons:
                    if p.partner == prsn.personid and not p.gender == prsn.gender:
                        prsn.partner = 0
                persons[idx].partner = p.personid
                p.partner = persons[idx].personid
            elif p.partner == 0 and persons[idx].interests.index(p.personid) < persons[idx].interests.index(persons[idx].partner):
                for prsn in persons:
                    if persons[idx].partner == prsn.personid and not persons[idx].gender == prsn.gender:
                        prsn.partner = 0
                persons[idx].partner = p.personid
                p.partner = persons[idx].personid
            elif persons[idx].interests.index(p.personid) < persons[idx].interests.index(persons[idx].partner) and p.interests.index(persons[idx].personid) < p.interests.index(p.partner):
                for prsn in persons:
                    if persons[idx].partner == prsn.personid and not persons[idx].gender == prsn.gender:
                        prsn.partner = 0
                    elif p.partner == prsn.personid and not p.gender == prsn.gender:
                        prsn.partner = 0
                persons[idx].partner = p.personid
                p.partner = persons[idx].personid
            
def matrixToString(matrix):
    return '\n'.join([''.join(['{:2}'.format(item.name) for item in row]) for row in matrix])
    
def translatePerson(personString, gender):
    return Person(int(personString[0]), gender, list(map(lambda x: int(x), personString[2:].split(" "))))

def walk(x, y, newX, newY):
    if matrix[newY][newX].posType in [1, 2, 3, 4]:
        return False
    elif 0 > newX > len(matrix) - 1 or 0 > newY > len(matrix) - 1:
        return False
    else:
        matrix[newY][newX] = matrix[y][x]
        matrix[y][x] = Position(0, ".")
    return True
        
def getStatus():
    string = "------------------------------------------------------------------------------------\n"
    string += "Matriz de dimensão: " + str(dimension) + " x " + str(dimension) + "\n"
    for p in persons:
        string += repr(p) + "\n"
    return string
    

threadLock = threading.Lock()
dimension = 20
rules = "3 4\n1 1 2 3\n2 3 1 2\n3 3 2 1\n1 2 3 1\n2 1 3 2\n3 2 1 3"

# 1. Sets the matrix with specified dimension.
matrix = [[Position(0, ".")] * dimension for _ in range(dimension)]

# 2. Read rules and prepare variables.
rulesList = rules.split("\n")
couplesRegistrys = rulesList[0].split(" ")
couples = int(couplesRegistrys[0])  
registrys = int(couplesRegistrys[1])
persons = [translatePerson(x, Gender.MALE) if ind < couples
           else translatePerson(x, Gender.FEMALE) 
           for ind, x in enumerate(rulesList[1:])]

# 3. Position everything in the matrix.
usedPositions = []
obstaclePositions = []
registryPositions = []

# 3.1. Add obstacles to random positions on the matrix.
matrixHalf = int(round(len(matrix) / 2))
numberOfObstacles = int(round(len(matrix) / 5))
obstacleSpacing = int(round(len(matrix) / numberOfObstacles))
i = int(round(obstacleSpacing / 2))
while i < len(matrix):
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
        matrix[j][i] = Position(1, "O")
        usedPositions.append([i, j])
        obstaclePositions.append([i, j])
        j += 1
    i += obstacleSpacing
    
# 3.2. Add each registry to a random not used position on the matrix 
#      next to obstacles.
for i in range(0, registrys):
    pos = obstaclePositions[randint(0, len(obstaclePositions) - 1)]
    if randint(0, 1) > 0:
        pos[0] += 1
    else: 
        pos[0] -= 1
    while pos in usedPositions:
        pos = obstaclePositions[randint(0, len(obstaclePositions) - 1)]
        if randint(0, 1) > 0:
            pos[0] += 1
        else: 
            pos[0] -= 1
    matrix[pos[1]][pos[0]] = Position(2, "R")
    usedPositions.append(pos)
    registryPositions.append(pos)

# 3.3. Add each person to a random not used position on the matrix.
x = randint(0, len(matrix[0]) - 1)
y = randint(0, len(matrix) - 1)
for i in range(0, len(persons)):
    while [x, y] in usedPositions:
        x = randint(0, len(matrix[0]) - 1)
        y = randint(0, len(matrix) - 1)
    matrix[y][x] = Position(3, "M") if persons[i].gender == Gender.MALE else Position(4, "F")
    persons[i].x = x
    persons[i].y = y
    usedPositions.append([x, y])
    
# 4. Starts all agent threads
for i in range(0, len(persons)):
    thread = Agent(i, 0.2)
    thread.start()
    
#print(matrixToString(matrix), flush=True)
#print("\n")

# -------TEST AREA-------

def aStarOk():
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
        
        for next in graph.neighbors(current):
            new_cost = cost_so_far(current) + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current

def getNeighbors(matrix, x, y):
    neighbors = []
    for i in range(-2, 2):
        for j in range(-2, 2):
            if not matrix[i][j] == "O":
                neighbors.append
                
def test():
    os.system('cls' if os.name == 'nt' else 'clear')
    testMatrix = [["-"] * 20 for _ in range(20)]
    testMatrix[0][7] = "O"
    testMatrix[1][7] = "O"
    testMatrix[2][7] = "O"
    testMatrix[3][7] = "O"
    testMatrix[4][7] = "O"
    testMatrix[5][7] = "O"
    testMatrix[5][6] = "O"
    testMatrix[5][5] = "O"
    testMatrix[5][4] = "O"
    testMatrix[5][3] = "O"
    testMatrix[5][2] = "O"
    testMatrix[14][14] = "O"
    testMatrix[14][15] = "O"
    testMatrix[14][16] = "O"
    testMatrix[14][17] = "O"
    testMatrix[14][19] = "O"
    testMatrix[15][14] = "O"
    testMatrix[16][14] = "O"
    testMatrix[17][14] = "O"
    testMatrix[18][14] = "O"
    testMatrix[19][14] = "O"
    testMatrix[10][11] = "O"
    testMatrix[10][12] = "O"
    testMatrix[9][12] = "O"
    testMatrix[9][13] = "O"
    testMatrix[8][13] = "O"
    testMatrix[8][14] = "O"
    testMatrix[7][14] = "O"
    testMatrix[7][15] = "O"
    testMatrix[6][15] = "O"
    testMatrix[6][16] = "O"
    testMatrix[5][16] = "O"
    testMatrix[5][17] = "O"
    testMatrix[4][17] = "O"
    testMatrix[11][10] = "O"
    testMatrix[11][11] = "O"
    testMatrix[12][9] = "O"
    testMatrix[12][10] = "O"
    testMatrix[13][8] = "O"
    testMatrix[13][9] = "O"
    testMatrix[14][8] = "O"
    testMatrix[15][8] = "O"
    testMatrix[16][8] = "O"
    testMatrix[17][8] = "O"
    testMatrix[18][8] = "O"
    testMatrix[19][8] = "O"
    testMatrix[11][19] = "O"
    testMatrix[11][18] = "O"
    testMatrix[11][17] = "O"
    testMatrix[11][16] = "O"
    testMatrix[2][4] = "X"
    testMatrix[17][17] = "Y"
    print(matrixToString(testMatrix))
                    
                    
from collections import deque

class AStar:
    def distBetween(self,current,neighbor):
        pass

    def heuristicEstimate(self,start,goal):
        pass

    def neighborNodes(self,current):
        pass
    
    def reconstructPath(self,cameFrom,goal):
        path = deque()
        node = goal
        path.appendleft(node)
        while node in cameFrom:
            node = cameFrom[node]
            path.appendleft(node)
        return path
    
    def getLowest(self,openSet,fScore):
        lowest = float("inf")
        lowestNode = None
        for node in openSet:
            if fScore[node] < lowest:
                lowest = fScore[node]
                lowestNode = node
        return lowestNode

    def aStar(self,start,goal):
        cameFrom = {}
        openSet = set([start])
        closedSet = set()
        gScore = {}
        fScore = {}
        gScore[start] = 0
        fScore[start] = gScore[start] + self.heuristicEstimate(start,goal)
        while len(openSet) != 0:
            current = self.getLowest(openSet,fScore)
            if current == goal:
                return self.reconstructPath(cameFrom,goal)
            openSet.remove(current)
            closedSet.add(current)
            for neighbor in self.neighborNodes(current):
                tentative_gScore = gScore[current] + self.distBetween(current,neighbor)
                if neighbor in closedSet and tentative_gScore >= gScore[neighbor]:
                    continue
                if neighbor not in closedSet or tentative_gScore < gScore[neighbor]:
                    cameFrom[neighbor] = current
                    gScore[neighbor] = tentative_gScore
                    fScore[neighbor] = gScore[neighbor] + self.heuristicEstimate(neighbor,goal)
                    if neighbor not in openSet:
                        openSet.add(neighbor)
        return 0