import simulation as sim
import classes.Trap as TrapClass
import classes.Wire as WireClass
import classes.Arrow as ArrowClass
import classes.Floor as FloorClass
import classes.Door as DoorClass
import classes.Food as FoodClass
from enums.Angle import *
from enums.Rotation import *
from enums.Thick import *
import algorithms as alg
import numpy as np
import copy
import random
from encoding import *
from designedTraps import *
import visualize as vis
import os
import webbrowser

cellAlphabet = [x for x in range(93)]
population = traps

def createTrap(configuration):
    """Takes in a board configuration and wraps that configuration in a trap class"""
    return TrapClass.Trap(len(configuration[0]), len(configuration), False, chosenBoard = configuration)

def randomFitness(_):
    """Assigns a random fitness to each configuration (choosing uniformly at random)"""
    return np.random.random()

def functionalFitness(configuration, numSimulations = 100, printStatistics = False):
    """
    Assigns a fitness based on the function of the given configuration.
    To do so, we run simulations to get a confidence interval on whether the gopher dies or not 
    or compute the the given configuration's probability of killing a gopher
    """
    # NOTE: Default probability of entering is 0.8 (found in magicVariables.py)
    # Simulate the trap running numSimulations times
    numberAlive = 0
    hungerLevels = 5
    for hunger in range(hungerLevels):
        for _ in range(int(numSimulations / hungerLevels)):
            numberAlive += int(sim.simulateTrap(createTrap(configuration), False, hunger = hunger / 5)[3])

    # Calculate statistics
    proportion = 1 - numberAlive / numSimulations

    if printStatistics:
        stderr = np.sqrt(proportion * (1 - proportion) / numSimulations)

        upperCI = proportion + 1.96 * stderr
        lowerCI = proportion - 1.96 * stderr

        print("Proportion: ", proportion)
        print("Std Error: ", round(stderr, 3))
        print("CI: [", round(lowerCI, 3), ", ", round(upperCI, 3), "]")

    return proportion

def coherentFitness(configuration):
    """Assigns a fitness based on the coherence of a given configuration"""
    return alg.getCoherenceValue(createTrap(configuration))

def initializePopulation(cellAlphabet, populationSize = 50):
    """Initializes the population by sampling from the search space"""
    population = []
    for _ in range(populationSize):
        # Temporary variable to store configuration as it is generated
        member = []
        for i in range(12):
            cellCode = random.randrange(2, len(cellAlphabet), 1)
            
            # Ensuring the board is valid
            if i == 4:
                cellCode = 1 # Food
            elif i == 7:
                cellCode = 2 # Floor
            elif i == 10:
                cellCode = 0 # Door

            member.append(cellCode)

        population.append(member)

    return listDecoding(population)

def checkTermination(fitnesses, measure, threshold):
    """Checks termination as a function of the given fitnesses.
       Stops when measure ('all', 'mean', 'median') of fitness meets threshold
    """
    if (measure not in ['all', 'mean', 'median']):
        raise ValueError('measure must be \'all\', \'mean\', or \'median\'.')

    # Ensure if all fitnesses meet threshold (if we are using this metric)
    if measure == 'all':
        for i in range(len(fitnesses)):
            if fitnesses[i] < threshold:
                return False

    # Check if mean or median threshold is met (if we are using either metric)
    elif (measure == 'mean' and np.mean(fitnesses) < threshold) \
        or (measure == 'median' and np.median(fitnesses) < threshold):
        return False

    # If we get to this part, then all thresholds are met, and we can terminate
    return True

def selectionFunc(population, fitnesses, elitism=False):
    """Performs a roulette wheel-style selection process, 
        giving greater weight to members with greater fitnesses"""
    # "Normalize" all fitnesses such that they sum to 1
    fitnessSum = np.sum(fitnesses)
    scaledFitnesses = fitnesses / fitnessSum if fitnessSum else 0 * fitnesses
    newPopulation = random.choices(population, weights = scaledFitnesses if fitnessSum else None, k=(len(population) - 2) if elitism else len(population))
    
    if elitism:
        # Keep the individuals with the two highest fitnesses for the next generation
        index1 = np.argmax(scaledFitnesses)
        index2 = 0
        for i in range(len(scaledFitnesses)):
            if i != index1 and scaledFitnesses[index2] < scaledFitnesses[i]:
                index2 = i
        newPopulation.append(population[index1])
        newPopulation.append(population[index2])

    return newPopulation



def crossoverFunc(encodedPop, fitnessFunc, debug = False):
    """Crosses-over two members of the population to form a new population (one-point crossover)"""
    # Get two members to crossover (use index to replace in list at end)
    member1_i = random.randrange(0, len(encodedPop), 1)
    member2_i = random.randrange(0, len(encodedPop), 1)
    
    if debug:
        print("original:")
        print(encodedPop[member1_i])
        print(encodedPop[member2_i])
        print()
    
    while member1_i == member2_i:
        member2_i = random.randrange(0, len(encodedPop), 1)

    # Cut occurs between (index - 1) and index
    index = random.randrange(1, len(encodedPop[member1_i]-3), 1)
    if debug:
        print("index:")
        print(index)
        print()

    # Calculate the left and right ends of the new members
    left1 = encodedPop[member1_i][:index]
    right1 = encodedPop[member1_i][index:]
    left2 = encodedPop[member2_i][:index]
    right2 = encodedPop[member2_i][index:]

    if debug:
        print("parts:")
        print(left1, right1)
        print(left2, right2)
        print()

    # Need to allocate arrays before-hand to prevent really weird error
    # Error mutates encodedPop[member1_i] but not encodedPop[member2_i]
    firstList = np.append(left1, right2)
    secondList = np.append(left2, right1)

    # Compute and update fitness of first List
    decodedFirstList = singleDecoding1(firstList)[:4]
    firstFitness = fitnessFunc(decodedFirstList) 
    firstList[12]= firstFitness
    # Compute and update fitness of second List
    secondList = np.append(left2, right1)
    decodedSecondList = singleDecoding1(secondList)[:4]
    secondFitness = fitnessFunc(decodedSecondList)
    secondList[12]= secondFitness

    # Replace these members in the encoded population
    encodedPop[member1_i] = firstList
    encodedPop[member2_i] = secondList
    
    if debug:
        print("is:")
        print(encodedPop[member1_i])
        print(encodedPop[member2_i])

    return encodedPop


def mutationFunc(cellAlphabet, encodedPop, fitnessFunc):
    """Performs one a single point mutation on a random member of the population"""
    # Get the index of the member in the encoded population and the index of the cell to mutate
    member_i = random.randrange(0, len(encodedPop), 1)
    index = random.randrange(0, len(encodedPop[member_i])-3, 1)

    # Ensure the flipped tile is not one of the required fixed tiles
    while (index == 4) or (index == 7) or (index == 10):
        index = random.randrange(0, len(encodedPop[member_i]), 1)

    # Change the member of the encoded population and the generated index (not door or food)
    encodedPop[member_i][index] = cellAlphabet[random.randrange(2, len(cellAlphabet), 1)]
    newDecoded = singleDecoding1(encodedPop[member_i])[:4]
    newFitness = fitnessFunc(newDecoded)
    encodedPop[member_i][12] = newFitness
    return encodedPop

def geneticAlgorithm(cellAlphabet, fitnessFunc, measure, threshold, maxIterations = 10000,
 showLogs = True, improvedCallback = True, callbackFactor = 0.99):
    """Finds a near-optimal solution in the search space using the given fitness function"""
    fitnesses = np.array([0 for i in range(15)])

    while(np.count_nonzero(fitnesses)==0):
        initialPop = initializePopulation(cellAlphabet)
        population = []
        # Add the fitness info row
        for member in initialPop:
            member = np.append(member, [[fitnessFunc(member),0,0]], axis=0)
            population.append(member)

        population = np.array(population)
        fitnesses = [member[4][0] for member in population]

    counter = 0

    while not checkTermination(fitnesses, measure, threshold) and counter < maxIterations:
        if showLogs and (counter % 50 == 0):
            print("Generation ", counter, ":")
            print("Min fitness: ", round(min(fitnesses), 3))
            print("Max fitness: ", round(max(fitnesses), 3))
            print("Mean fitness: ", round(np.mean(fitnesses), 3))
            print("Median fitness:", round(np.median(fitnesses), 3))
            print("------------------------")
            print()

        originalPop = copy.deepcopy(population)
        originalFit = copy.deepcopy(fitnesses)

        population = selectionFunc(population, fitnesses)
        encodedPop = listEncoding1(population)
        encodedPop = crossoverFunc(encodedPop, fitnessFunc)
        encodedPop = mutationFunc(cellAlphabet, encodedPop, fitnessFunc)
        
        population = listDecoding1(encodedPop)
        
        fitnesses = np.array([member[4][0] for member in population])

        
        # Dismisses the new pop if its fitness is less than (old pop's fitness * callbackFactor).
        # callbackFactor should be in the interval [0, 1], where 0 is equivalent to having improvedCallback=False.
        if improvedCallback:
            if measure == 'mean' and np.mean(fitnesses) < callbackFactor*np.mean(originalFit):
                population = originalPop
                fitnesses = originalFit
            else:
                if np.median(fitnesses) < callbackFactor*np.median(originalFit):
                    population = originalPop
                    fitnesses = originalFit

        counter += 1

    if showLogs:
        print("Generation ", counter, ":")
        print("Min fitness: ", round(min(fitnesses), 3))
        print("Max fitness: ", round(max(fitnesses), 3))
        print("Mean fitness: ", round(np.mean(fitnesses), 3))
        print("Median fitness:", round(np.median(fitnesses), 3))
        print("------------------------")
        print()

    # Delete the fitness info row
    finalPopulation = []
    for member in population:
        finalPopulation.append(np.delete(member, 4, 0))

    return np.array(finalPopulation)

def exportGeneticOutput(outputFile, cellAlphabet, fitnessFunc, measure, threshold, maxIterations = 10000, showLogs = True):
    """
    Runs the genetic algorithm with the given parameters and writes a new file with the list encodings in it (to preserve the output)
    """
    finalPopulation = geneticAlgorithm(cellAlphabet, fitnessFunc, measure, threshold, maxIterations, showLogs)
    with open(outputFile, 'w') as out:
        for i, population in enumerate(listEncoding(finalPopulation)):
            out.write(str(i) + ": ")
            
            # Standardize spacing
            if i < 10:
                out.write(" ")
            
            out.write(np.array2string(population) + '\n')

def simulateTrapInBrowser(listEncoding):
    """Takes in a list encoding and simulates the trap in the browser"""
    decodedList = singleDecoding(listEncoding)
    simulationInfo = sim.simulateTrap(createTrap(decodedList), False)[:3]
    vis.writeTojs([simulationInfo], False)

    # opens the animation in the web browser
    webbrowser.open_new_tab('file://' + os.path.realpath('./animation/animation.html'))

#exportGeneticOutput('geneticAlgorithm.txt', cellAlphabet, coherentFitness, 'mean', 0.8)
#simulateTrapInBrowser([9, 36, 76, 78, 1, 13, 84, 2, 4, 90, 0, 16])


#print(geneticAlgorithm(cellAlphabet, coherentFitness, 'mean', 1))
print(geneticAlgorithm(cellAlphabet, functionalFitness, 'median', 0.65))
#print(geneticAlgorithm(cellAlphabet, randomFitness, 'mean', 0.7))
