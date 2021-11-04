import matplotlib.pyplot as plt
import database.plot as plot

def generate_all_visuals(show=False):
    # plot.createLethalityCoherenceHeatMap('coherence', log=True, save=True)
    # plot.createLethalityCoherenceHeatMap('random', log=True, save=True)
    # plot.createLethalityCoherenceHeatMap('functional', log=True, save=True)
    # plot.createLethalityCoherenceHeatMap('multiobjective', log=True, save=True)
    # plot.createLethalityCoherenceHeatMap('binary-distance', log=True, save=True)
    # plot.createLethalityCoherenceHeatMap('uniform-random', log=True, save=True)

    # plot.createVectorMaps('lethality', save=True, name='VectorMapProd')
    # plot.createVectorMaps('coherence', save=True, name='VectorMapProd')

    plot.createGenerationBoxPlot(save=True)

    plot.createAverageOptimalFitnessLinePlot(save=True)
    plot.createAverageGenerationLinePlot(cumulative=False, end=500, save=True)

    if show:
        plt.show()
