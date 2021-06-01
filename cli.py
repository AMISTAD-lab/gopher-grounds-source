import experiment
from geneticAlgorithm.utils import *
from geneticAlgorithm.fitnessFunctions import *
from geneticAlgorithm.main import *
from geneticAlgorithm.encoding import singleEncoding
import argparse

parser = argparse.ArgumentParser(description="Commands to run the experiment")
subparsers = parser.add_subparsers(help='sub-command help', dest='command')

# runExperiment flags
runExperimentParser = subparsers.add_parser('runExperiment', help='runs experiment')
runExperimentParser.add_argument('output', help='the output file name')
runExperimentParser.add_argument('inputToVary', help='independent variable to vary (probReal, nTrapsWithoutFood, maxProjectileStrength, defaultProbEnter)')
runExperimentParser.add_argument('numSimulations', help='number of simluations to run per param value', type=int)

# simulate flags
simulateParser = subparsers.add_parser('simulate', help='simulates experiment')
simulateParser.add_argument('--intention', '-i', help='if gopher has intention', type=bool, default=True)
simulateParser.add_argument('--cautious', '-c', help='if gopher is cautious', type=bool, default=False)
simulateParser.add_argument('--defaultProbEnter', '-d', help='probability of gopher entering trap (not for intention)', type=float, default=0.8)
simulateParser.add_argument('--probReal', '-p', help='percentage of traps that are designed as opposed to random', type=float, default=0.2)
simulateParser.add_argument('--nTrapsWithoutFood', '-n', help='the amount of traps a gopher can survive without entering (due to starvation)', type=int, default=4)
simulateParser.add_argument('--maxProjectileStrength', '-m', help='the maximum projectile strength (thickWire strength)', type=float, default=.45)

# genetic algorithm flags
geneticParser = subparsers.add_parser('genetic-algorithm', help='generates a trap using the genetic algorithm')
geneticParser.add_argument('function', help='a choice of {random, coherence, functional}')
geneticParser.add_argument('--measure', '-m', help='the measure for the threshold (max, mean, median, all)', default='max')
geneticParser.add_argument('--threshold', '-t', help='the threshold to use for termination in [0, 1]', type=float, default=0.8)
geneticParser.add_argument('--maxIterations', '-i', help='the maximum number of iterations to run', type=int, default=10000)
geneticParser.add_argument('--log', '-l', help='whether or not to print the logs as generations increase', type=bool, default=True)
geneticParser.add_argument('--improvedCallback', '-c', help='whether or not to use improved callback', type=bool, default=True)
geneticParser.add_argument('--export', '-e', help='whether or not to export data to file (changed with -o flag)', type=bool, default=False)
geneticParser.add_argument('--outputFile', '-o', help='the output file to which we write', default='geneticAlgorithm.txt')
geneticParser.add_argument('--show', '-s', help='show output in browser', type=bool, default=False)

args = parser.parse_args()

if args.command == 'runExperiment':
    experiment.runExperiment(args.output, args.inputToVary, args.numSimulations)
elif args.command == 'simulate':
    trapInfo = experiment.simulate({
        "intention" : args.intention, #if gopher has intention
        "cautious" : args.cautious, # only used if intention, fakes a FSC test to confirm intention > cautiousness
        "defaultProbEnter" : args.defaultProbEnter, #probability of gopher entering trap (not for intention)
        "probReal" : args.probReal, #percentage of traps that are designed as opposed to random
        "nTrapsWithoutFood" : args.nTrapsWithoutFood, #the amount of traps a gopher can survive without entering (due to starvation)
        "maxProjectileStrength" : args.maxProjectileStrength, #thickWire strength
    })

    print(trapInfo[1])
elif args.command == 'genetic-algorithm':
    # Defining the fitness function
    fitnessFunc = lambda x : 0
    if args.function == 'random':
        fitnessFunc = randomFitness
    elif args.function == 'coherence':
        fitnessFunc = coherentFitness
    elif args.function == 'functional':
        fitnessFunc = functionalFitness
    else:
        raise Exception(args.function, ' is not a real fitness function value. Please try again')

    # Running the simulation
    bestTrap = []
    bestFitness = 0
    if args.export:
        bestTrap, bestFitness = exportGeneticOutput(args.outputFile, cellAlphabet, fitnessFunc, args.threshold,  args.measure, args.maxIterations, args.log)
    else:
        finalPopulation = geneticAlgorithm(cellAlphabet, fitnessFunc, args.threshold, args.measure, args.maxIterations, args.log, args.improvedCallback)

        for member in finalPopulation:
            currFitness = fitnessFunc(member)
            if currFitness > bestFitness:
                bestTrap = singleEncoding(member)
                bestFitness = currFitness

    print('Trap (encoded):\t', bestTrap)
    print('Fitness:\t', round(bestFitness, 3))

    if args.show:
        simulateTrapInBrowser(bestTrap)
