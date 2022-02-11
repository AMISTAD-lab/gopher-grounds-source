import csv
import math
import os
from classes.Encoding import Encoding
from database.client import client
import misc.visualization as vis

path = './visualizations/{}Visualization.csv'

def getVisualizationData(func, numGenerations, trial = 1):
    cursor = client.cursor()

    if func == 'functional':
        fitness = 'lethality'
    elif func == 'coherence':
        fitness = 'coherence'
    elif func == 'multiobjective':
        fitness = 'combined'

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

def createImages(func, encoder):
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
            
            vis.convertTrapToImage(trap, f'{dirName}/trap{i}', encoder, save=True, ext='png', tag=f'{i}', fitness=f'{round(float(fitness), 3)}')

def createCombined():
    for i in range(1, 101):
        print(f"Starting trap {i}")
        imgPaths = [f'./images/traps/blog{func}/trap{i}.png' for func in ('Funct', 'Coher', 'Multi')]
        vis.combineThreeImages(imgPaths, f'trap{i:03d}Combined', save=True, labels=['FUNCTIONAL', 'COHERENCE', 'MULTIOBJECTIVE'])

encoder = Encoding(code=1)
for func in ('functional', 'coherence', 'multiobjective'):
    # getVisualizationData(func, 100)
    createImages(func, encoder)

createCombined()
# ffmpeg -r 10/3 -s 1920x1080 -i images/traps/blogCombined/trap%03dCombined.png -vcodec libx264 -crf 25 -pix_fmt yuv420p ./images/traps/blog_video.mp4