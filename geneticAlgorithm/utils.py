from geneticAlgorithm.encoding import *
import classes.Trap as TrapClass
from geneticAlgorithm.main import *
import visualize as vis
import os
import webbrowser
import simulation as sim

def createTrap(configuration):
    """Takes in a board configuration and wraps that configuration in a trap class"""
    return TrapClass.Trap(len(configuration[0]), len(configuration), False, chosenBoard = configuration)


def exportGeneticOutput(outputFile, cellAlphabet, fitnessFunc, threshold, measure = 'max', maxIterations = 10000, showLogs = True):
    """
    Runs the genetic algorithm with the given parameters and writes a new file with the unique list encodings and counts.
    Returns a tuple of the (encoded) trap with highest fitness and the highest fitness
    """
    # Run the simluation and keep the genetic algorithm 
    finalPopulation = geneticAlgorithm(cellAlphabet, fitnessFunc, threshold, measure, maxIterations, showLogs)

    # Find counts and fitnesses of each element in final population
    uniquePopulation = []
    freqs = {}
    fitnesses = {}

    for member in finalPopulation:
        memberEnc = singleEncoding(member)
        memberStr = np.array2string(memberEnc)
        if memberStr not in freqs:
            uniquePopulation.append(memberEnc)
            freqs[memberStr] = 0
        
        if memberStr not in fitnesses:
            fitnesses[memberStr] = round(fitnessFunc(member), 3)

        freqs[memberStr] += 1

    bestTrap = []
    bestFitness = 0

    with open(outputFile, 'w') as out:
        for member in enumerate(uniquePopulation):
            memberStr = np.array2string(member)

            # Check if this member is optimal
            if fitnesses[memberStr] > bestFitness:
                bestTrap = member
                bestFitness = fitnesses[memberStr]

            # Write to the file
            out.write(str(freqs[memberStr]) + ":\t")

            out.write("[")
            
            # Convert to array form
            for j, digit in enumerate(member):
                out.write(str(digit))
                
                if j < len(member) - 1:
                    out.write(', ')
            
            out.write('],\tfitness: ')
            out.write(str(fitnesses[memberStr]))

            out.write('\n')
    
    return bestTrap, bestFitness

def simulateTrapInBrowser(listEncoding):
    """Takes in a list encoding and simulates the trap in the browser"""
    decodedList = singleDecoding(listEncoding)
    simulationInfo = sim.simulateTrap(createTrap(decodedList), False, forceEnter=True)[:3]
    vis.writeTojs([simulationInfo], False)

    # opens the animation in the web browser
    webbrowser.open_new_tab('file://' + os.path.realpath('./animation/animation.html'))