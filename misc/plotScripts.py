# import matplotlib.pyplot as plt
# import database.plot as plot2
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

vis.convertTrapToImage('[47, 6, 86, 25, 1, 29, 26, 2, 62, 72, 0, 9]', 'example', save=True)
vis.createAnnotatedTrap(save=True, show=False)
vis.createSplitTrap(5, save=True, show=False)

# plt.show()