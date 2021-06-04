#!/usr/bin/env python3
import legacy.experiment as experiment
from geneticAlgorithm.utils import *
from geneticAlgorithm.fitnessFunctions import *
from geneticAlgorithm.main import *
from geneticAlgorithm.encoding import singleEncoding
import geneticAlgorithm.experiment as geneticExperiment
import argparse
from legacy.designedTraps import *
import geneticAlgorithm.utils as util

parser = argparse.ArgumentParser(description="Commands to run the experiment")
subparsers = parser.add_subparsers(help='sub-command help', dest='command')

legacy = subparsers.add_parser('legacy', help='runs experiment or simulates legacy code (gopher\'s gambit)')
legacyParsers = legacy.add_subparsers(help='legacy parsers', dest='legacy')

# legacyParser.runExperiment flags
legacyExperimentParser = legacyParsers.add_parser('runExperiment', help='runs experiment')
legacyExperimentParser.add_argument('output', help='the output file name')
legacyExperimentParser.add_argument('inputToVary', help='independent variable to vary (probReal, nTrapsWithoutFood, maxProjectileStrength, defaultProbEnter)')
legacyExperimentParser.add_argument('numSimulations', help='number of simluations to run per param value', type=int)

# legacyParser.simulate flags
simulateParser = legacyParsers.add_parser('simulate', help='simulates experiment')
simulateParser.add_argument('--intention', '-i', help='turns on intention gopher', action='store_true')
simulateParser.add_argument('--cautious', '-c', help='if gopher is cautious', action='store_true')
simulateParser.add_argument('--defaultProbEnter', '-d', help='probability of gopher entering trap (not for intention)', type=float, default=0.8)
simulateParser.add_argument('--probReal', '-p', help='percentage of traps that are designed as opposed to random', type=float, default=0.2)
simulateParser.add_argument('--nTrapsWithoutFood', '-n', help='the amount of traps a gopher can survive without entering (due to starvation)', type=int, default=4)
simulateParser.add_argument('--maxProjectileStrength', '-m', help='the maximum projectile strength (thickWire strength)', type=float, default=.45)

# genetic algorithm parser
geneticParser = subparsers.add_parser('genetic-algorithm', help='generates a trap using the genetic algorithm')
geneticSubparsers = geneticParser.add_subparsers(help='genetic algorithm subparsers', dest='genetic')

# generate trap flags
generateTrap = geneticSubparsers.add_parser('generate', help='generates a trap')
generateTrap.add_argument('function', help='a choice of {random, coherence, functional, combined}')
generateTrap.add_argument('--measure', '-m', help='the measure for the threshold (max, mean, median, all)', default='max')
generateTrap.add_argument('--threshold', '-t', help='the threshold to use for termination in [0, 1]', type=float, default=0.8)
generateTrap.add_argument('--max-iterations', '-i', help='the maximum number of iterations to run', type=int, default=10000)
generateTrap.add_argument('--no-logs', '-nl', help='turns off logs as generations increase', action='store_false')
generateTrap.add_argument('--no-improved-callback', '-nc', help='turn off improved callback', action='store_false')
generateTrap.add_argument('--export', '-e', help='whether or not to export data to file (changed with -o flag)',  action='store_true')
generateTrap.add_argument('--output-file', '-o', help='the output file to which we write', default='geneticAlgorithm.txt')
generateTrap.add_argument('--show', '-s', help='show output in browser', action='store_true')

# run experiment flags
geneticExperimentParser = geneticSubparsers.add_parser('runExperiment', help='runs an experiment')
geneticExperimentParser.add_argument('function', help='a choice of {random, coherence, functional, combined}')
geneticExperimentParser.add_argument('--measure', '-m', help='the measure for the threshold (max, mean, median, all)', default='max')
geneticExperimentParser.add_argument('--threshold', '-t', help='the threshold to use for termination in [0, 1]', type=float, default=0.8)
geneticExperimentParser.add_argument('--max-iterations', '-i', help='the maximum number of iterations to run', type=int, default=10000)
geneticExperimentParser.add_argument('--no-logs', '-nl', help='turns on logs for generations', action='store_false')
geneticExperimentParser.add_argument('--no-improved-callback', '-nc', help='turn off improved callback', action='store_false')
geneticExperimentParser.add_argument('--export', '-e', help='whether or not to export data to file (changed with -o flag)',  action='store_true')
geneticExperimentParser.add_argument('--output-file', '-o', help='the output file to which we write', default='experiment.txt')
geneticExperimentParser.add_argument('--num-simulations', '-s', help='the number of simulations of the trap to run', type=int, default=10000)
geneticExperimentParser.add_argument('--no-print-stats', '-np', help='turn off statistic printing', action='store_false')
geneticExperimentParser.add_argument('--conf-level', '-c', help='set the confidence level', type=float, default=0.95)
geneticExperimentParser.add_argument('--intention', '-in', help='give the simulated gopher intention', action='store_true')

# run batch experiments flags
geneticExperimentParser = geneticSubparsers.add_parser('runBatchExperiments', help='runs an experiment')
geneticExperimentParser.add_argument('function', help='a choice of {random, coherence, functional, combined}')
geneticExperimentParser.add_argument('--num-experiments', '-e', help='number of experiments to run', type=int, default=10)
geneticExperimentParser.add_argument('--threshold', '-t', help='the threshold to use for termination in [0, 1]', type=float, default=0.8)
geneticExperimentParser.add_argument('--max-iterations', '-i', help='the maximum number of iterations to run', type=int, default=10000)
geneticExperimentParser.add_argument('--show_logs', '-l', help='turns on logs for generations', action='store_true')
geneticExperimentParser.add_argument('--no-improved-callback', '-nc', help='turn off improved callback', action='store_false')
geneticExperimentParser.add_argument('--output-file', '-o', help='the output file to which we write', default='experiment.txt')
geneticExperimentParser.add_argument('--num-simulations', '-s', help='the number of simulations of the trap to run', type=int, default=10000)
geneticExperimentParser.add_argument('--conf-level', '-c', help='set the confidence level', type=float, default=0.95)
geneticExperimentParser.add_argument('--intention', '-in', help='give the simulated gopher intention', action='store_true')

# simulate trap flags
simulateTrap = geneticSubparsers.add_parser('simulate', help='simulates a trap given an input string')
simulateTrap.add_argument('trap', help='the encoded trap as a string (surrounded by \'\'s)')

args = parser.parse_args()

if args.command == 'legacy' and args.legacy == 'runExperiment':
    experiment.runExperiment(args.output, args.inputToVary, args.numSimulations)

elif args.command == 'legacy' and args.legacy == 'simulate':
    trapInfo = experiment.simulate({
        "intention" : args.intention, #if gopher has intention
        "cautious" : args.cautious, # only used if intention, fakes a FSC test to confirm intention > cautiousness
        "defaultProbEnter" : args.defaultProbEnter, #probability of gopher entering trap (not for intention)
        "probReal" : args.probReal, #percentage of traps that are designed as opposed to random
        "nTrapsWithoutFood" : args.nTrapsWithoutFood, #the amount of traps a gopher can survive without entering (due to starvation)
        "maxProjectileStrength" : args.maxProjectileStrength, #thickWire strength
    })

    print(trapInfo[1])

elif args.command == 'genetic-algorithm' and args.genetic == 'simulate':
    strList = args.trap
    strList = strList.strip()[1:-1] # getting the numbers
    digitList = strList.split(',') # splitting number strings by digits
    simulateTrapInBrowser([int(digit.strip()) for digit in digitList])

elif args.command == 'genetic-algorithm':
    # Defining the fitness function
    fitnessFunc = lambda x : 0
    if args.function == 'random':
        fitnessFunc = randomFitness
    elif args.function == 'coherence':
        fitnessFunc = coherentFitness
    elif args.function == 'functional':
        fitnessFunc = functionalFitness
    elif args.function == 'combined':
        fitnessFunc = combinedFitness
    else:
        raise Exception(args.function, ' is not a real fitness function value. Please try again')

    if args.genetic == 'generate':
        # Running the simulation
        bestTrap = []
        bestFitness = 0
        if args.export:
            bestTrap, bestFitness = exportGeneticOutput(
                args.output_file,
                cellAlphabet,
                fitnessFunc,
                args.threshold,
                args.measure,
                args.max_iterations,
                args.no_logs,
                args.no_improved_callback
            )
        else:
            finalPopulation, bestTrap, bestFitness = geneticAlgorithm(
                cellAlphabet,
                fitnessFunc,
                args.threshold,
                args.measure,
                args.max_iterations,
                args.no_logs,
                args.no_improved_callback
            )

        print('Trap (encoded):\t', bestTrap)
        print('Fitness:\t', round(bestFitness, 3))

        if args.show:
            simulateTrapInBrowser(bestTrap)
    
    elif args.genetic == 'runExperiment':
        trap, fitness, prop, stderr, ci = geneticExperiment.runExperiment(
            fitnessFunc, 
            args.threshold, 
            args.measure, 
            args.max_iterations, 
            args.no_logs, 
            args.no_improved_callback, 
            args.num_simulations, 
            args.conf_level, 
            args.intention, 
            args.no_print_stats, 
            args.export, 
            args.output_file
        )
    elif args.genetic == 'runBatchExperiments':
        geneticExperiment.runBatchExperiments(
            args.num_experiments,
            fitnessFunc,
            args.threshold,
            args.num_simulations,
            args.conf_level,
            args.show_logs,
            args.output_file,
            args.intention,
            args.no_improved_callback
        )


