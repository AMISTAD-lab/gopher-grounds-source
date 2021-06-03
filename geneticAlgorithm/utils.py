from typing import Any
import numpy as np
import os
import webbrowser
import simulation as sim
import geneticAlgorithm.encoding as encoding
import classes.Trap as TrapClass
from geneticAlgorithm.main import geneticAlgorithm
import visualize as vis
from classes.Wire import Wire
from classes.Arrow import Arrow
from enums.Angle import AngleType
from enums.Rotation import RotationType
from geneticAlgorithm.cellarray import compareCells

cellAlphabet = [x for x in range(93)]

def createTrap(configuration):
    """Takes in a board configuration and wraps that configuration in a trap class"""
    return TrapClass.Trap(len(configuration[0]), len(configuration), False, chosenBoard = configuration)

def getProbabilityDistribution(probEnter = 0.8):
    """Calculates the probability distribution of eating time from the given probability of entrance"""
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

    return initialProbs

def getTimeEat(hunger, defaultProbEnter = 0.8):
    """Returns an array where the ith element is the probability that a gopher will eat for (i + 1) time steps"""
    hungerWeight = hunger ** 10
    probEnter = defaultProbEnter * (1 - hungerWeight) + hungerWeight
    return np.array(getProbabilityDistribution(probEnter))

def getLeaveTime(timeLeft, timeRight, timeEat):
    """Get the time it takes for the gopher to leave a trap"""
    if timeLeft < 0:
        timeLeft = 3 + timeEat
    if timeRight < 0:
        timeRight = 3 + timeEat
    
    return min(timeLeft, timeRight, 3 + timeEat)

def gopherDeathProb(arrowData, leaveTime):
    """
    Returns the probability that a gopher dies given the information of a arrow
    """
    time, cell, thickness = arrowData

    # If time < 0, then arrow does not hit, and gopher does not die
    if time < 0:
        return 0
    
    pass

def getArrowData(configuration):
    """
    Takes in a board configuration and returns 2 tuples (for left and right paths) where the first element is the time at which the arrow fires (or -1 if the arrow does not fire),
    the second element is the cell that was hit (1, 2, 3 is door, floor, food respectively), and the third element is the thickness of the wire
    """
    # Initializing variables
    wire_angles = [AngleType.rright, AngleType.straight, AngleType.straight, AngleType.rright, AngleType.straight, AngleType.rright, AngleType.straight, AngleType.straight, AngleType.rright]
    
    # Left path
    left_indices = [
        (0, 3), (0, 2), (0, 1),
        (0, 0), (1, 0), (2, 0),
        (2, 1), (2, 2), (2, 3)
    ]
    wire_left_rotations = [
        RotationType.left, RotationType.up, RotationType.up,
        RotationType.up, RotationType.right, RotationType.right,
        RotationType.up, RotationType.up, RotationType.up
    ]
    arrow_left_angles = [
        (AngleType.racute, ), (AngleType.robtuse, AngleType.rright), (AngleType.rright, ),
        (AngleType.racute, ), (AngleType.rright, ), (AngleType.racute, ),
        (AngleType.rright, AngleType.robtuse), (AngleType.racute, AngleType.rright, AngleType.robtuse), (AngleType.rright, AngleType.racute)
    ]
    arrow_left_rotations = [
        RotationType.left, RotationType.up, RotationType.up,
        RotationType.up, RotationType.right, RotationType.right,
        RotationType.down, RotationType.down, RotationType.down
    ]
    arrow_hits_left = [
        (2, ), (3, 2), (3, ),
        (3, ), (4, ), (3, ),
        (3, 2), (3, 2, 1), (1, 2)
    ]

    # Right path
    right_indices = [
        (2, 3), (2, 2), (2, 1),
        (2, 0), (1, 0), (0, 0),
        (0, 1), (0, 2), (0, 3)
    ]
    wire_right_rotations = [
        RotationType.down, RotationType.up, RotationType.up,
        RotationType.right, RotationType.right, RotationType.up,
        RotationType.up, RotationType.up, RotationType.left]
    arrow_right_angles = [
        (AngleType.lacute, ), (AngleType.lobtuse, AngleType.lright), (AngleType.lright, ),
        (AngleType.lacute, ), (AngleType.lright, ), (AngleType.lacute, ),
        (AngleType.lright, AngleType.lobtuse), (AngleType.lacute, AngleType.lright, AngleType.lobtuse), (AngleType.lacute, AngleType.lright)
    ]
    arrow_right_rotations = [
        RotationType.right, RotationType.up, RotationType.up,
        RotationType.up, RotationType.left, RotationType.left,
        RotationType.down, RotationType.down, RotationType.down
    ]
    arrow_hits_right = [
        (2, ), (3, 2), (3, ),
        (3, ), (4, ), (3, ),
        (3, 2), (3, 2, 1), (2, 1)
    ]

    # Initializing shared resources
    both_indices = (left_indices, right_indices)
    both_hits = (arrow_hits_left, arrow_hits_right)
    wire_rotations = []
    arrow_angles = arrow_rotations = []
    retData = []

    for i, indices in enumerate(both_indices):
        # Setting current angles
        if indices == left_indices:
            wire_rotations = wire_left_rotations
            arrow_angles = arrow_left_angles
            arrow_rotations = arrow_left_rotations
        else:
            wire_rotations = wire_right_rotations
            arrow_angles = arrow_right_angles
            arrow_rotations = arrow_right_rotations
        thickness = None
        
        for j, (x, y) in enumerate(indices):
            currCell = configuration[y][x]

            if not (isinstance(currCell, (Wire, Arrow))):
                break

            if isinstance(currCell, Wire):
                if j == 0:
                    thickness = currCell.thickType

                # The `listCell` argument requires that cells are in standard form (found in cell array file)
                if not compareCells(currCell, Wire(0, 0, None, wire_angles[j], wire_rotations[j], thickness)):
                    break

                continue

            if isinstance(currCell, Arrow):
                sameRotation = currCell.rotationType == arrow_rotations[j]
                sameThickness = currCell.thickType == thickness if thickness else True

                if (currCell.angleType in arrow_angles[j] and sameRotation and sameThickness):
                    indexOfAngle = arrow_angles[j].index(currCell.angleType)
                    retData.append((j + 1, both_hits[i][j][indexOfAngle], thickness))
                    break

    return retData[0], retData[1]

def zapsGopher(configuration):
    """Takes in a board configuration and returns True if the board is able to zap the gopher by tracing the coherence of a path around the left and right of the board"""
    wire_angles = [AngleType.rright, AngleType.straight, AngleType.straight, AngleType.rright, AngleType.straight, AngleType.rright, AngleType.straight, AngleType.straight, AngleType.rright]
    
    # Left path
    left_indices = [(0, 3), (0, 2), (0, 1), (0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3)]
    wire_left_rotations = [RotationType.left, RotationType.up, RotationType.up, RotationType.up, RotationType.right, RotationType.right, RotationType.up, RotationType.up, RotationType.up]
    arrow_left_angles = [
        AngleType.racute, (AngleType.robtuse, AngleType.rright), AngleType.rright,
        AngleType.racute, AngleType.rright, AngleType.racute,
        (AngleType.rright, AngleType.robtuse), (AngleType.racute, AngleType.rright, AngleType.robtuse), (AngleType.rright, AngleType.racute)
    ]
    arrow_left_rotations = [
        RotationType.left, RotationType.up, RotationType.up,
        RotationType.up, RotationType.right, RotationType.right,
        RotationType.down, RotationType.down, RotationType.down
    ]

    # Right path
    right_indices = [(2, 3), (2, 2), (2, 1), (2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (0, 3)]
    wire_right_rotations = [RotationType.down, RotationType.up, RotationType.up, RotationType.right, RotationType.right, RotationType.up, RotationType.up, RotationType.up, RotationType.left]
    arrow_right_angles = [
        AngleType.lacute, (AngleType.lobtuse, AngleType.lright), AngleType.lright,
        AngleType.lacute, AngleType.lright, AngleType.lacute,
        (AngleType.lright, AngleType.lobtuse), (AngleType.lacute, AngleType.lright, AngleType.lobtuse), (AngleType.lright, AngleType.lacute)
    ]
    arrow_right_rotations = [
        RotationType.right, RotationType.up, RotationType.up,
        RotationType.up, RotationType.left, RotationType.left,
        RotationType.down, RotationType.down, RotationType.down
    ]

    # Initializing shared resources
    both_indices = (left_indices, right_indices)
    wire_rotations = []
    arrow_angles = arrow_rotations = []
    zapsGopher = [None, None]

    for i, indices in enumerate(both_indices):
        # Setting current angles
        if indices == left_indices:
            wire_rotations = wire_left_rotations
            arrow_angles = arrow_left_angles
            arrow_rotations = arrow_left_rotations
        else:
            wire_rotations = wire_right_rotations
            arrow_angles = arrow_right_angles
            arrow_rotations = arrow_right_rotations
        thickness = None
        
        for j, (x, y) in enumerate(indices):
            currCell = configuration[y][x]

            if not (isinstance(currCell, (Wire, Arrow))):
                break

            if isinstance(currCell, Wire):
                if j == 0:
                    thickness = currCell.thickType

                # The `listCell` argument requires that cells are in standard form (found in cell array file)
                if not compareCells(currCell, Wire(0, 0, None, wire_angles[j], wire_rotations[j], thickness)):
                    zapsGopher[i] = False
                    break

                continue

            if isinstance(currCell, Arrow):
                sameRotation = currCell.rotationType == arrow_rotations[j]
                sameThickness = currCell.thickType == thickness if thickness else True

                if (isinstance(arrow_angles[j], tuple)):
                    zapsGopher[i] = currCell.angleType in arrow_angles[j] and sameRotation and sameThickness
                    break
                else:
                    zapsGopher[i] = currCell.angleType == arrow_angles[j] and sameRotation and sameThickness
                    break

    return zapsGopher[0] or zapsGopher[1]

def exportGeneticOutput(outputFile, cellAlphabet, fitnessFunc, threshold, measure = "max", maxIterations = 10000, showLogs = True, improvedCallback=True):
    """
    Runs the genetic algorithm with the given parameters and writes a new file with the unique list encodings and counts.
    Returns a tuple of the (encoded) trap with highest fitness and the highest fitness
    """
    # Run the simluation and keep track of the unique values in the genetic algorithm
    finalPopulation, bestTrap, bestFitness = geneticAlgorithm(cellAlphabet, fitnessFunc, threshold, measure, maxIterations, showLogs, improvedCallback)

    # Find counts and fitnesses of each element in final population
    uniquePopulation = []
    freqs = {}
    fitnesses = {}

    for member in finalPopulation:
        memberEnc = encoding.singleEncoding(member)
        memberStr = np.array2string(memberEnc)
        if memberStr not in freqs:
            uniquePopulation.append(memberEnc)
            freqs[memberStr] = 0
        
        if memberStr not in fitnesses:
            fitnesses[memberStr] = round(fitnessFunc(member), 3)

        freqs[memberStr] += 1

    with open(outputFile, "w") as out:
        for member in uniquePopulation:
            memberStr = np.array2string(member)

            # Write to the file
            out.write(str(freqs[memberStr]) + ":\t")

            out.write("[ ")
            
            # Convert to array form
            for j, digit in enumerate(member):
                out.write(str(digit))
                
                if j < len(member) - 1:
                    out.write(", ")
            
            out.write(" ],\tfitness: ")
            out.write(str(fitnesses[memberStr]))

            out.write("\n")
    
    return bestTrap, bestFitness

def simulateTrapInBrowser(listEncoding, hunger=0):
    """Takes in a list encoding and simulates the trap in the browser"""
    decodedList = encoding.singleDecoding(listEncoding)
    simulationInfo = sim.simulateTrap(createTrap(decodedList), False, hunger=hunger, forceEnter=True)[:3]
    vis.writeTojs([simulationInfo], False)

    # opens the animation in the web browser
    webbrowser.open_new_tab("file://" + os.path.realpath("./animation/animation.html"))