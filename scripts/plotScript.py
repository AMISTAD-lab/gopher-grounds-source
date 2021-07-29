import matplotlib.pyplot as plt
import database.plot as plot2
from classes.Encoding import Encoding

def generate_all_visuals(show=False):
    encoder = Encoding([9, 6, 3, 0, 1, 2, 5, 8, 11, 10, 7, 4])

    plot2.createLethalityCoherenceHeatMap('coherence', log=True, save=True)
    plot2.createLethalityCoherenceHeatMap('random', log=True, save=True)
    plot2.createLethalityCoherenceHeatMap('functional', log=True, save=True)
    plot2.createLethalityCoherenceHeatMap('multiobjective', log=True, save=True)
    plot2.createLethalityCoherenceHeatMap('binary-distance', log=True, save=True)
    plot2.createLethalityCoherenceHeatMap('uniform-random', log=True, save=True)

    plot2.createVectorMaps('lethality', save=True, name='VectorMapProd')
    plot2.createVectorMaps('coherence', save=True, name='VectorMapProd')

    plot2.createGenerationBoxPlot(save=True)

    plot2.createAverageOptimalFitnessLinePlot(save=True)
    plot2.createAverageGenerationLinePlot(cumulative=False, end=500, save=True)

    if show:
        plt.show()
