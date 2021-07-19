import matplotlib.pyplot as plt
import database.plot as plot2

# plot2.createLethalityCoherenceHeatMap('coherence', log=True, save=True)
# plot2.createLethalityCoherenceHeatMap('random', log=True, save=True)
# plot2.createLethalityCoherenceHeatMap('functional', log=True, save=True)
# plot2.createLethalityCoherenceHeatMap('multiobjective', log=True, save=True)
# plot2.createLethalityCoherenceHeatMap('binary-distance', log=True, save=True)
# plot2.createLethalityCoherenceHeatMap('uniform-random', log=True, save=True)

# plot2.createVectorMaps('lethality')
# plot2.createVectorMaps('coherence', save=True)

# plot2.createLethVCohGenScatter('multiobjective')

# plot2.createGenerationBoxPlot(save=True)

# plot2.createAverageOptimalFitnessLinePlot(save=True)
plot2.createAverageGenerationLinePlot(cumulative=False, end=500, save=True)

# plt.show()