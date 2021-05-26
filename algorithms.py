from typeRotation import *
from typeDirection import *
from typeAngle import *
from typeCell import *
from typeThick import *
import classCell as c
import numpy as np
import copy
import csv
import math as m

def findDir(rotationType, angleType):
    """returns the direction of a trap piece from our bottom-up perspective (primarily for the arrow)"""

    if(rotationType == RotationType.left):
        if(angleType == AngleType.lacute):
            return DirectionType.lowerright 
        elif(angleType == AngleType.racute):
            return DirectionType.upperright
        elif(angleType == AngleType.lright):
            return DirectionType.down
        elif(angleType == AngleType.rright):
            return DirectionType.up
        elif(angleType == AngleType.lobtuse):
            return DirectionType.lowerleft
        elif(angleType == AngleType.robtuse):
            return DirectionType.upperleft
        elif(angleType == AngleType.straight):
            return DirectionType.left
        else:
            raise Exception("Error: angleType doesn't exist")
    
    elif(rotationType == RotationType.right): 
        if(angleType == AngleType.lacute):
            return DirectionType.upperleft
        elif(angleType == AngleType.racute):
            return DirectionType.lowerleft
        elif(angleType == AngleType.lright):
            return DirectionType.up
        elif(angleType == AngleType.rright):
            return DirectionType.down
        elif(angleType == AngleType.lobtuse):
            return DirectionType.upperright
        elif(angleType == AngleType.robtuse):
            return DirectionType.lowerright
        elif(angleType == AngleType.straight):
            return DirectionType.right
        else:
            raise Exception("Error: angleType doesn't exist")

    elif(rotationType == RotationType.up): 
        if(angleType == AngleType.lacute):
            return DirectionType.lowerleft
        elif(angleType == AngleType.racute):
            return DirectionType.lowerright
        elif(angleType == AngleType.lright):
            return DirectionType.left
        elif(angleType == AngleType.rright):
            return DirectionType.right
        elif(angleType == AngleType.lobtuse):
            return DirectionType.upperleft
        elif(angleType == AngleType.robtuse):
            return DirectionType.upperright
        elif(angleType == AngleType.straight):
            return DirectionType.up
        else:
            raise Exception("Error: angleType doesn't exist")

    elif(rotationType == RotationType.down):
        if(angleType == AngleType.lacute):
            return DirectionType.upperright
        elif(angleType == AngleType.racute):
            return DirectionType.upperleft
        elif(angleType == AngleType.lright):
            return DirectionType.right
        elif(angleType == AngleType.rright):
            return DirectionType.left
        elif(angleType == AngleType.lobtuse):
            return DirectionType.lowerright
        elif(angleType == AngleType.robtuse):
            return DirectionType.lowerleft
        elif(angleType == AngleType.straight):
            return DirectionType.down
        else:
            raise Exception("Error: angleType doesn't exist")

def formatMatrix(matrix):
    """returns a string representation of the matrix that can then be printed"""  
    string = ""
    colLength = len(matrix)
    rowLength = len(matrix[0])
    for y in range(colLength):
        for x in range(rowLength):
            string += str(matrix[y][x]) + "\t"
        string += "\n\n\n"
    return string

def flatten(l):
    """turns a matrix (list of lists) into a single list"""
    return [item for sublist in l for item in sublist]

#Defining pieces necessary for fsc
TOTAL = 427929800129788411
r = TOTAL * (1 + m.log(TOTAL))
p = 1 / TOTAL
#These are the frequencies of varying levels of coherence
f_g = {
    (0.0, 1.0) : 427929800129788411 / TOTAL,
    (1.0, 9.0) : 354394707075243198 / TOTAL,
    (1.0, 8.0) : 123453353582343198 / TOTAL,
    (1.0, 7.0) : 102193295525793198 / TOTAL,
    (1.0, 6.0) : 101346901331553198 / TOTAL,
    (1.0, 5.0) : 101327843325852198 / TOTAL,
    (2.0, 9.0) : 101327577622082748 / TOTAL,
    (1.0, 4.0) : 18317428758242748 / TOTAL,
    (2.0, 7.0) : 12289201862932377 / TOTAL,
    (1.0, 3.0) : 12103878714006177 / TOTAL,
    (3.0, 8.0) : 1272268411781292 / TOTAL,
    (2.0, 5.0) : 689654429107497 / TOTAL,
    (3.0, 7.0) : 689623309037907 / TOTAL,
    (4.0, 9.0) : 677046035997297 / TOTAL,
    (1.0, 2.0) : 41696845623225 / TOTAL,
    (5.0, 9.0) : 18559182512862 / TOTAL,
    (4.0, 7.0) : 919349539299 / TOTAL,
    (3.0, 5.0) : 616034679885 / TOTAL,
    (5.0, 8.0) : 615255422625 / TOTAL,
    (2.0, 3.0) : 239164711182 / TOTAL,
    (5.0, 7.0) : 6417454230 / TOTAL,
    (3.0, 4.0) : 3925431153 / TOTAL,
    (7.0, 9.0) : 1459677645 / TOTAL,
    (4.0, 5.0) : 26456355 / TOTAL,
    (5.0, 6.0) : 22595625 / TOTAL,
    (6.0, 7.0) : 17067672 / TOTAL,
    (7.0, 8.0) : 10561401 / TOTAL,
    (8.0, 9.0) : 4297158 / TOTAL,
    (1.0, 1.0) : 26730 / TOTAL,
    (10.0, 9.0) : 3 / TOTAL,
}

def functional_specified_complexity(connectionTuple):
    """returns the fsc (surprisal) of a given traps' connection tuple
    connection tuple: (numerator, denominator) of the simplified fraction for valid connections / wire and arrow pieces"""
    global r
    global p
    v = 1 / f_g[connectionTuple]
    k = r * p / v
    fsc = -m.log(k, 2)
    return fsc

def isTrap(trap, sigVal=13.29):
    """given a trap and a significant value, determines whether the trap is coherent enough to be considered designed"""
    connectionTuple = connectionsPerPiece(trap)
    if functional_specified_complexity(connectionTuple) >= sigVal:
        return True
    else:
        return False

#the historical frequencies of intention gophers entering traps
#to be used for the cautious gopher
intentionEnter = {
    "0.0" : 0.0,
    "0.05" : 0.04988481269964185,
    "0.1" : 0.09948793864971121,
    "0.15" : 0.14881005760747487,
    "0.2" : 0.199672975964652,
    "0.25" : 0.24902111248844028,
    "0.3" : 0.298916566348736,
    "0.35" : 0.3495346742719904,
    "0.4" : 0.39898116983534976,
    "0.45" : 0.44854377391645306,
    "0.5" : 0.5017578233012316,
    "0.55" : 0.5510910365512773,
    "0.6" : 0.6005349888710337,
    "0.65" : 0.6493674432638634,
    "0.7" : 0.7013113161728994,
    "0.75" : 0.7513506373423156,
    "0.8" : 0.799739176543086,
    "0.85" : 0.850076699120308,
    "0.9" : 0.8984355307600531,
    "0.95" : 0.9488828397610392,
    "1.0" : 1.0
}

def cautious(trap, probReal):
    """randomly determines whether the trap is real given a probability
    for the cautious gopher's entering algorithm"""
    realTrap = np.random.binomial(n=1, p=intentionEnter[str(probReal)])
    return realTrap

def connectionsPerPiece(trap):
    """given a trap, returns its connection tuple (the simplified fraction for valid connections / wire and arrow pieces)"""
    connections = totalConnections(trap)
    if connections == 0:
        return (0, 1.0)
    numPieces = 0
    for cell in flatten(trap.board):
        if cell.cellType == CellType.wire or cell.cellType == CellType.arrow:
            numPieces += 1
    return simplifyRatioTuple(connections, numPieces)

def simplifyRatioTuple(num, denom):
	"""Simplifies the tuple, which represents the numerator and denominator of a fraction.
	Inputs: 
		num: the numerator
		denom: the denominator"""
	if num == 0:# group anything with num 0 into the (0, 1) category
		return (0.0, 1.0)
	elif num != 0 and denom == 0:
		raise Exception("ERROR: All cells are floor cells, but connections were found.")

	gcd = int(np.gcd(num, denom))
	num = num/gcd
	denom = denom/gcd
	return (num, denom) 


usedCells = [] #initializing usedCells as a global variable for use in several following methods
def totalConnections(trap):
    """
    returns how many connections a trap has
    """
    global usedCells
    usedCells = []
    endpoints = 0
    allCells = flatten(trap.board)
    for cell in allCells:
        if cell.cellType == CellType.arrow or cell.cellType == CellType.wire or cell.cellType == CellType.door:
            for endpoint in cell.endpoints:
                neighbor = cell.getNeighboringCell(endpoint)
                if neighbor != None:
                    if (neighbor.cellType == CellType.wire) or ((cell.cellType == CellType.wire or cell.cellType == CellType.door) and neighbor.cellType == CellType.arrow):
                        if checkConnection(cell, endpoint):
                            endpoints += 1
                            usedCells.append(cell)   
    return endpoints

def checkConnection(cell, endpoint):
    """
    Helper func:
    returns true if that cell is connected and thicktypes match
    """
    global usedCells
    cellAtEndpoint = cell.getNeighboringCell(endpoint)
    matchingEndpoint = c.getOppositeEndpoint(endpoint)
    
    if cell.cellType == CellType.door:
        if (cellAtEndpoint not in usedCells) and (matchingEndpoint in cellAtEndpoint.endpoints):
            return True
    ## arrow or wire cell
    elif (cellAtEndpoint not in usedCells) and (matchingEndpoint in cellAtEndpoint.endpoints):
        if (cell.thickType == cellAtEndpoint.thickType):
            return True
    return False
    
def gopherEatTimer(probEnter):
    """
    decides how long the gopher should eat based on the gopher's detection of threat.
    """
    idealTimer = probEnter * 5
    initialProbs = [0.05, 0.05, 0.05, 0.05, 0.05]
    for i in range(5):
        if idealTimer <= i + 1:
            initialProbs[i] = 0.6
            if i == 0:
                initialProbs[1] = 0.2
                initialProbs[2] = 0.1
            elif i == 4:
                initialProbs[3] = 0.2
                initialProbs[2] = 0.1
            else:
                initialProbs[i+1] = 0.15
                initialProbs[i-1] = 0.15
            break
    return np.random.choice([1,2,3,4,5], p=initialProbs, size=1)[0]