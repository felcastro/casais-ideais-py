from enum import Enum
from random import randint
import threading
import time
import os

class Position(Enum):
    EMPTY = 0
    PERSON = 1
    REGISTRY = 2
    OBSTACLE = 3

class Gender(Enum):
    MALE = 0
    FEMALE = 1

class Person(object):
    
    def __init__(self, personid, gender, interests):
        self.personid = personid
        self.gender = gender
        self.interests = interests
        
    def __repr__(self):
        return "[%s, %s, %s, %s, %s]" % (self.personid, self.gender, self.interests, self.x, self.y)
        
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
        os.system('clear')
        print(persons[idx])
        print(matrixToString(matrix), flush=True)
        if walked:
            persons[idx].x = newX
            persons[idx].y = newY
        threadLock.release()
        time.sleep(delay)
        
def checkNearbyPartners(matrix, gender, x, y):
    for i in range(-2, 3):
        for j in range(-2, 3):
            if matrix[y + i][x + j] == "X":
                return [j, i]
    return []
            
def matrixToString(matrix):
    return '\n'.join([''.join(['{:2}'.format(item) for item in row]) for row in matrix])
    
def translatePerson(personString, gender):
    return Person(int(personString[0]), gender, list(map(lambda x: int(x), personString[2:].split(" "))))

def walk(x, y, newX, newY):
    if matrix[newY][newX] in ["O", "R", "M", "F"]:
        return False
    elif 0 > newX > len(matrix) - 1 or 0 > newY > len(matrix) - 1:
        return False
    else:
        matrix[newY][newX] = matrix[y][x]
        matrix[y][x] = "."  
    return True
        

threadLock = threading.Lock()
dimension = 20
rules = "3 4\n1 1 2 3\n2 3 1 2\n3 3 2 1\n1 2 3 1\n2 1 3 2\n3 2 1 3"

# 1. Sets the matrix with specified dimension.
matrix = [["."] * dimension for _ in range(dimension)]

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
        matrix[j][i] = "O"
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
    matrix[pos[1]][pos[0]] = "R"
    usedPositions.append(pos)
    registryPositions.append(pos)

# 3.3. Add each person to a random not used position on the matrix.
x = randint(0, len(matrix[0]) - 1)
y = randint(0, len(matrix) - 1)
for i in range(0, len(persons)):
    while [x, y] in usedPositions:
        x = randint(0, len(matrix[0]) - 1)
        y = randint(0, len(matrix) - 1)
    matrix[y][x] = "M" if persons[i].gender == Gender.MALE else "F"
    persons[i].x = x
    persons[i].y = y
    usedPositions.append([x, y])
    
# 4. Starts all agent threads
#thread = Agent(0, 1)
#thread.start()

#for i in range(0, len(persons)):
#    thread = Agent(i, 0.3)
#    thread.start()
    
#print(matrixToString(matrix), flush=True)
#print("\n")

testMatrix = matrix = [["."] * 20 for _ in range(20)]
testMatrix[9][9] = "O"
testMatrix[9][11] = "X"
testMatrix[7][8] = "X"
testMatrix[10][9] = "X"
testMatrix[8][10] = "X"
testMatrix[11][11] = "X"
testMatrix[10][7] = "X"

checkNearbyPartners(testMatrix, "M", 9, 9)

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