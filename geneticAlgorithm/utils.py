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
    arrow_left_prob = []

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
