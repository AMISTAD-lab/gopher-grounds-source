# import matplotlib.pyplot as plt
# import database.plot as plot2
from geneticAlgorithm.encoding import Encoding
import misc.visualization as vis

# plot2.createLethalityCoherenceHeatMap('coherence', log=True, save=True)
# plot2.createLethalityCoherenceHeatMap('random', log=True, save=True)
# plot2.createLethalityCoherenceHeatMap('functional', log=True, save=True)
# plot2.createLethalityCoherenceHeatMap('multiobjective', log=True, save=True)
# plot2.createLethalityCoherenceHeatMap('binary-distance', log=True, save=True)
# plot2.createLethalityCoherenceHeatMap('uniform-random', log=True, save=True)

# plot2.createVectorMaps('lethality', save=True, name='VectorMapProd')
# plot2.createVectorMaps('coherence', save=True, name='VectorMapProd')

# plot2.createLethVCohGenScatter('multiobjective')

# plot2.createGenerationBoxPlot(save=True)

# plot2.createAverageOptimalFitnessLinePlot(save=True)
# plot2.createAverageGenerationLinePlot(cumulative=False, end=500, save=True)

encoder = Encoding([9, 6, 3, 0, 1, 2, 5, 8, 11, 10, 7, 4])
trap = encoder.from_canonical([47, 6, 86, 25, 1, 29, 26, 2, 62, 72, 0, 9])
vis.convertTrapToImage(f'{trap}', 'example', encoder, show=False, save=True)
vis.createAnnotatedTrap(encoder, save=True, show=False)
vis.createSplitTrap(5, encoder, annotate=True, save=True, show=False)

# plt.show()