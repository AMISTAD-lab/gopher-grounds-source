#!/usr/bin/env python3
import argparse
import geneticAlgorithm.fitnessFunctions as functions 
import geneticAlgorithm.experiment as geneticExperiment
from classes.Encoding import Encoding
from geneticAlgorithm.main import geneticAlgorithm
import geneticAlgorithm.utils as util
import legacy.experiment as experiment
import misc.visualization as vis

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
generateTrap.add_argument('function', help='a choice of {random, coherence, functional, multiobjective}')
generateTrap.add_argument('--max-generations', '-g', help='the maximum number of iterations to run', type=int, default=10000)
generateTrap.add_argument('--no-logs', '-nl', help='turns off logs as generations increase', action='store_false')
generateTrap.add_argument('--output-file', '-o', help='the output file to which we write', default='geneticAlgorithm.txt')
generateTrap.add_argument('--show', '-s', help='show output in browser', action='store_true')
generateTrap.add_argument('--permutation', '-p', help='the permutation for the encoding', default=None)

# run experiment flags
geneticExperimentParser = geneticSubparsers.add_parser('runExperiment', help='runs an experiment')
geneticExperimentParser.add_argument('function', help='a choice of {random, coherence, functional, multiobjective, binary-distance}')
geneticExperimentParser.add_argument('--max-generations', '-g', help='the maximum number of iterations to run', type=int, default=10000)
geneticExperimentParser.add_argument('--no-logs', '-nl', help='turns on logs for generations', action='store_false')
geneticExperimentParser.add_argument('--num-simulations', '-s', help='the number of simulations of the trap to run', type=int, default=5000)
geneticExperimentParser.add_argument('--no-print-stats', '-np', help='turn off statistic printing', action='store_false')
geneticExperimentParser.add_argument('--permutation', '-p', help='the permutation for the encoding', default=None)

# run batch experiments flags
geneticExperimentParser = geneticSubparsers.add_parser('runBatchExperiments', help='runs an experiment')
geneticExperimentParser.add_argument('function', help='a choice of {random, coherence, functional, multiobjective, binary-distance}')
geneticExperimentParser.add_argument('--num-experiments', '-e', help='number of experiments to run', type=int, default=10)
geneticExperimentParser.add_argument('--max-generations', '-g', help='the maximum number of iterations to run', type=int, default=10000)
geneticExperimentParser.add_argument('--output-suffix', '-o', help='a suffix to append to the output file name', default='Generated')
geneticExperimentParser.add_argument('--num-simulations', '-s', help='the number of simulations of the trap to run', type=int, default=5000)
geneticExperimentParser.add_argument('--no-overwrite', '-nw', help='overwrites the experiment csv file', action='store_false')
geneticExperimentParser.add_argument('--permutation', '-p', help='the permutation for the encoding', default=None)

# simulate trap flags
simulateTrap = geneticSubparsers.add_parser('simulate', help='simulates a trap given an input string')
simulateTrap.add_argument('trap', help='the encoded trap as a string (surrounded by \'\'s)')
simulateTrap.add_argument('--hunger', help='set the hunger for the simulated gopher (0, 1)', type=float, default=0)
simulateTrap.add_argument('--intention', '-in', help='give the simulated gopher intention', action='store_true')
simulateTrap.add_argument('--no-animation', '-na', help='turns off animation', action='store_true')
simulateTrap.add_argument('--gopher-state', '-g', help='sets the gopher\'s state as \'[x, y, rotation, state]\'', default='[-1, -1, 0, 1]')
simulateTrap.add_argument('--frame', '-f', help='the frame of the grid to print', type=int, default=0)
simulateTrap.add_argument('--permutation', '-p', help='the permutation for the encoding', default=None)
simulateTrap.add_argument('--brave', '-b', help='make the simulated gopher brave', action='store_true')

showTrap = geneticSubparsers.add_parser('show-trap', help='shows (and, optionally, saves) a trap given an input string')
showTrap.add_argument('trap', help='the encoded trap as a string (surrounded by \'\'s)')
showTrap.add_argument('--save', '-s', help='whether or not to save the trap created', action='store_true')
showTrap.add_argument('--output', '-o', help='the name of the file (no extensions) to be saved', default='generatedTrap')
showTrap.add_argument('--ext', '-e', help='the extension type', default='pdf')
showTrap.add_argument('--no-pdf', '-np', help='do not show PDF', action='store_false')
showTrap.add_argument('--no-gopher', '-ng', help='do not show the gopher', action='store_false')
showTrap.add_argument('--permutation', '-p', help='the permutation for the encoding', default='1')

createGif = geneticSubparsers.add_parser('create-gif', help='simulates a trap and saves each frame in the images/traps/gif folder')
createGif.add_argument('trap', help='the encoded trap as a string (surrounded by \'\'s)')
createGif.add_argument('--permutation', '-p', help='the permutation for the encoding', default='1')

# get fitness trap flags
fitnessParser = geneticSubparsers.add_parser('check-fitnesses', help='returns the fitness of the trap')
fitnessParser.add_argument('trap', help='the encoded trap as a string (surrounded by \'\'s)')
fitnessParser.add_argument('--permutation', '-p', help='the permutation for the encoding (1 is preset)', default=None)

args = parser.parse_args()

# Defining variables repeated
if 'permutation' in args and args.permutation == '1':
    args.permutation = '[9, 6, 3, 0, 1, 2, 5, 8, 11, 10, 7, 4]'

encoder = Encoding(util.convertStringToEncoding(args.permutation)) if args.permutation else Encoding()
trap = util.convertStringToEncoding(args.trap) if 'trap' in args else None

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
    gopherState = util.convertStringToEncoding(args.gopher_state)
    vis.simulateTrapInBrowser(trap, encoder, args.hunger, args.intention, args.no_animation, gopherState, args.frame, args.brave)

elif args.command == 'genetic-algorithm' and args.genetic == 'show-trap':
    vis.convertTrapToImage(args.trap, args.output, encoder, save=args.save, showGopher=args.no_gopher, show=args.no_pdf, ext=args.ext)

elif args.command == 'genetic-algorithm' and args.genetic == 'create-gif':
    vis.create_gif_from_trap(args.trap, encoder)

elif args.command == 'genetic-algorithm' and args.genetic == 'check-fitnesses':
    print('Coherence fitness:\t', round(functions.getCoherence(trap, encoder), 3))
    print('Functional fitness:\t', round(functions.getLethality(trap, encoder), 3))
    print('Combined fitness:\t', round(functions.getCombined(trap, encoder), 3))

elif args.command == 'genetic-algorithm':
    if args.genetic == 'generate':
        # Running the simulation
        bestTrap = []
        bestFitness = 0
        finalPopulation, bestTrap, bestFitness = geneticAlgorithm(
            args.function,
            encoder,
            args.max_generations,
            args.no_logs,
        )

        print('Trap (encoded):\t\t', bestTrap)
        print('Coherence fitness:\t', round(functions.getCoherence(bestTrap, encoder), 3))
        print('Functional fitness:\t', round(functions.getLethality(bestTrap, encoder), 3))
        print('Combined fitness:\t', round(functions.getCombined(bestTrap, encoder), 3))

        if args.show:
            vis.simulateTrapInBrowser(bestTrap, encoder)
    
    elif args.genetic == 'runExperiment':
        trap, fitness, prop, stderr, ci, intention = geneticExperiment.runExperiment(
            args.function,
            encoder,
            maxGenerations=args.max_generations,
            showLogs=args.no_logs,
            numSimulations=args.num_simulations,
            printStatistics=False,
        )

        print('Trap (Encoded):\t ', trap)
        print('Fitness\t:\t ', fitness)
        print('Proportion Dead:', prop)
        print('Standard Error:\t', stderr)
        print('Conf. Interval:\t', ci)
        print('Intention?:\t', 'Yes' if intention else 'No')

    elif args.genetic == 'runBatchExperiments':
        geneticExperiment.runBatchExperiments(
            numExperiments=args.num_experiments,
            functionName=args.function,
            encoder=encoder,
            numSimulations=args.num_simulations,
            maxGenerations=args.max_generations,
            overwrite=args.no_overwrite,
            suffix=args.output_suffix,
        )
