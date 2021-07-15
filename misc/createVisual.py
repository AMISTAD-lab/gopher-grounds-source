import csv
import math
import os
from database.client import client
import misc.visualization as vis

path = './visualizations/{}Visualization.csv'

def getVisualizationData(func, fitness, numGenerations, trial = 1):
    cursor = client.cursor()

    cursor.execute(f' \
        SELECT [trap], MAX([{fitness}]), [generation] FROM frequencies \
        WHERE [function]=:function AND [trial]=:trial AND [generation] < :generations GROUP BY generation;',
        { 'function': func, 'trial': trial, 'generations': numGenerations }
    )

    with open(path.format(func), 'w+', newline='') as fWrite:
        writer = csv.writer(fWrite)

        writer.writerow(['Trap', 'Fitness', 'Generation'])

        for entry in cursor.fetchall():
            writer.writerow(entry)

def createImages(func):
    if func == 'functional':
        dirName = 'blogFunct'
    elif func == 'coherence':
        dirName = 'blogCoher'
    elif func == 'multiobjective':
        dirName = 'blogMulti'
    
    if not os.path.exists(f'./images/traps/{dirName}'):
        os.mkdir(f'./images/traps/{dirName}')
    
    with open(path.format(func), 'r', newline='') as fRead:
        for i, (trap, fitness, _) in enumerate(csv.reader(fRead)):
            if i == 0:
                continue
            
            vis.convertTrapToImage(trap, f'{dirName}/trap{i}', save=True, ext='png', tag=f'{i}', fitness=f'{round(float(fitness), 3)}')

def createCombined():
    for i in range(1, 101):
        print(f"Starting trap {i}")
        imgPaths = [f'./images/traps/blog{func}/trap{i}.png' for func in ('Funct', 'Coher', 'Multi')]
        vis.combineThreeImages(imgPaths, 'trap{}{}Combined'.format((2 - int(math.log10(i))) * '0', i), save=True, labels=['FUNCTIONAL', 'COHERENCE', 'MULTIOBJECTIVE'])

createCombined()