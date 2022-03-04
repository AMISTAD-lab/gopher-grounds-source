import experiment_1.experiment1Algos as alg1
import experiment_2.experiment2Algos as alg2
import experiment_2.createImage as image
import geneticAlgorithm.constants as constants

# print(gt.getSmoothedProb('[73 64 70 25 82  7 60 91 34  0  2  1]', 'random')




# alg1.scExperiment("designed", 1)

fitnessFuncs = ["coherence", "functional", "multiobjective","random"]

# for fitnessFunc in fitnessFuncs:
#     filename = constants.getExperimentResultPath(number=2, func=fitnessFunc, suff='_expData')
#     alg2.runExperiment(filename, "default", 5000, 25, fitnessFunc)
#     image.statusOverTime(filename, fitnessFunc)

for fitnessFunc in fitnessFuncs:
    alg1.scExperiment(fitnessFunc, 25)