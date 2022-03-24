import experiment_1.experiment1Algos as alg1
import experiment_2.experiment2Algos as alg2
import experiment_2.createImage as image2
import experiment_3.experiment3Algos as alg3
import experiment_3.createImage as image3
import geneticAlgorithm.constants as constants




fitnessFuncs = ['random', 'functional', 'coherence', 'multiobjective']
inputToVary = "default"
numSimulations = 1000
numFiles = 25

############################################# Experiment 1 ############################################
for fitnessFunc in fitnessFuncs:
     alg1.scExperiment(fitnessFunc, numFiles)

############################################# Experiment 2 ############################################
for fitnessFunc in fitnessFuncs:
     filename = constants.getExperimentResultPath(number=2, func=fitnessFunc, suff='_expData')
     alg2.runExperiment(filename, inputToVary, numSimulations, numFiles, fitnessFunc)
     image2.statusOverTime(filename, fitnessFunc)


############################################# Experiment 3 ############################################
for fitnessFunc in fitnessFuncs:
     filename = constants.getExperimentResultPath(number=3, func=fitnessFunc, suff='_expData')
     alg3.runExperiment(filename, inputToVary, numSimulations, numFiles, fitnessFunc)
     image3.statusOverTime(filename, fitnessFunc)