import numpy as np
import os
import webbrowser
import classes.Trap as TrapClass
import geneticAlgorithm.encoding as encoding
from geneticAlgorithm.main import geneticAlgorithm
import libs.simulation as sim
import libs.visualize as vis

def createTrap(configuration):
    """Takes in a board configuration and wraps that configuration in a trap class"""
    return TrapClass.Trap(len(configuration[0]), len(configuration), False, chosenBoard = configuration)

def convertStringToEncoding(strEncoding):
    """Takes in an encoding as a string and returns that encoding as a list"""
    strList = strEncoding.strip()[1:-1] # getting the numbers
    digitList = strList.split(',') # splitting number strings by digits
    return [int(digit.strip()) for digit in digitList]

def convertEncodingToString(encoding):
    """Takes in an encoding and returns the string version of it"""
    encodingStr = '[ '
    for i, elem in enumerate(encoding):            
        encodingStr += '{}'.format(str(elem))
        if i < len(encoding) - 1:
            encodingStr += ', '
    encodingStr += ' ]'
    return encodingStr

def convertStringToDecoding(strEncoding):
    """ Takes in a string encoding and returns the decoded trap """
    return encoding.singleDecoding(convertStringToEncoding(strEncoding))

def exportGeneticOutput(outputFile, cellAlphabet, fitnessFunc, threshold, maxGenerations = 10000, showLogs = True):
    """
    Runs the genetic algorithm with the given parameters and writes a new file with the unique list encodings and counts.
    Returns a tuple of the (encoded) trap with highest fitness and the highest fitness
    """
    # Run the simluation and keep track of the unique values in the genetic algorithm
    finalPopulation, bestTrap, bestFitness = geneticAlgorithm(cellAlphabet, fitnessFunc, threshold, maxGenerations, showLogs)

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

def simulateTrapInBrowser(listEncoding, hunger=0, intention=False, noAnimation=False, gopherState=[1, 4, 0, 1], frame = 0):
    """Takes in a list encoding and simulates the trap in the browser"""
    decodedList = encoding.singleDecoding(listEncoding)
    simulationInfo = sim.simulateTrap(createTrap(decodedList), intention, hunger=hunger, forceEnter=True)[:3]
    vis.writeTojs([simulationInfo], noAnimation, gopherState, frame)

    # opens the animation in the web browser
    webbrowser.open_new_tab("file://" + os.path.realpath("./animation/animation.html"))
