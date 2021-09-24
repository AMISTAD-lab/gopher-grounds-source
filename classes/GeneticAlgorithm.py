import numpy as np
import time
from typing import Callable
from classes.Encoding import Encoding
import geneticAlgorithm.fitnessFunctions as functions
import geneticAlgorithm.library as geneticLib

class GeneticAlgorithm():
    '''
    Class can be used as a template for creating a genetic algorithm.
    The user must provide self-consistent initialization, selection, recombination, and mutation functions, as well as a valid encoder instance.
    Then, the run() method (with the respective arguments) will generate a trap using the genetic algorithm instance created and return relevant data.
    '''
    def __init__(self, init_pop_func: Callable = None, select_func : Callable = None, mutat_func : Callable = None, cross_func : Callable = None, encoder : Encoding = None):
        self.init_pop_func = init_pop_func if init_pop_func else geneticLib.initializePopulation
        self.select_func = select_func if select_func else geneticLib.selectionFunc
        self.mutat_func = mutat_func if mutat_func else geneticLib.mutationFunc
        self.cross_func = cross_func if cross_func else geneticLib.crossoverFunc
        self.encoder = encoder if encoder else Encoding()
    
    def run(self, functionName, maxGenerations = 10000, showLogs = True, trial = None, barData={}, writer=None):
        """
        Finds a near-optimal solution in the search space using the given fitness function
        Returns a 3-tuple of (finalPopulation, bestTrap (encoded), bestFitness)
        """
        fitnessFunc = functions.getFunctionFromName(functionName)
        fitnesses = np.array(20 * [0])
        population = np.array([])

        if fitnessFunc == functions.getBinaryDistance:
            functions.targetTrap = geneticLib.generateTrap(self.encoder)

        # Destructure population into CSV format
        getWriteData = lambda population, fitnesses : [
                [
                    trial, generation, trap, functionName,
                    round(fitnesses[i], 4),
                    round(functions.getLethality(trap, self.encoder), 4),
                    round(functions.getCoherence(trap, self.encoder), 4),
                    round(functions.getCombined(trap, self.encoder), 4),
                ]
                for i, trap in enumerate(population)
            ]

        # Sampling the (encoded) population until we get one non-zero member
        while(np.count_nonzero(fitnesses) == 0):
            population = geneticLib.initializePopulation(self.encoder)
            fitnesses = fitnessFunc(population, self.encoder)
        
        # Recalculate frequencies
        fitnesses = fitnessFunc(population, self.encoder)

        generation = 0
        startTime = lastTime = time.time()

        writeData = getWriteData(population, fitnesses)

        currMax = np.argmax(fitnesses)
        maxFitness, bestTrap = fitnesses[currMax], population[currMax]

        while generation < maxGenerations:
            if showLogs and (generation % 50 == 0):
                print(f"Generation {generation}:")
                print("Current Max fitness\t: {}".format(round(max(fitnesses), 3)))
                print("Global Max fitness\t: {}".format(round(maxFitness, 3)))
                print("Lap Time\t\t: {}".format(round(time.time() - lastTime, 4)))
                print("Total Time\t\t: {}".format(round(time.time() - startTime, 4)))
                print("------------------------")
                print()
                
                # Set last time
                lastTime = time.time()

            # Creating new population using genetic algorithm
            newPopulation = []
            for _ in range(len(population)):
                parent1, parent2 = self.select_func(population, fitnesses)
                child = self.cross_func(parent1, parent2)
                childMutated = self.mutat_func(self.encoder, child)
                newPopulation.append(childMutated)

            # Calculating new fitnesses and updating the optimal solutions
            fitnesses = fitnessFunc(newPopulation, self.encoder)
            population = newPopulation

            currMax = np.argmax(fitnesses)
            if fitnesses[currMax] > maxFitness:
                maxFitness = fitnesses[currMax]
                bestTrap = newPopulation[currMax]

            generation += 1

            # Add new data to the writeData list
            if writer:
                writeData.extend(getWriteData(population, fitnesses))

            if barData:
                barData['counter'] += 1

                numBars, maxSteps = barData['numBars'], barData['maxSteps']
                modulo = maxSteps // numBars if numBars <= maxSteps else 1
                
                if barData['counter'] % modulo == 0:
                    barData['bar'].next(n=max(1, numBars / maxSteps))

        if writer and writeData:
            writer.writerows(writeData)

        if showLogs:
            print(f"Generation {generation}:")
            print("Current Max fitness\t: {}".format(round(max(fitnesses), 3)))
            print("Global Max fitness\t: {}".format(round(maxFitness, 3)))
            print("Lap Time\t\t: {}".format(round(time.time() - lastTime, 4)))
            print("Total Time\t\t: {}".format(round(time.time() - startTime, 4)))
            print("------------------------")
            print()

        return np.array(population), bestTrap, maxFitness
