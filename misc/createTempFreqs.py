import csv
import database.setup as dbSetup
import database.library as dbLibrary

def createTest(func: str, maxLines = 100):
    with open(f'./frequencies/{func}.csv', 'r') as fRead, open(f'./miniFrequencies/{func}.csv', 'w+') as fWrite:
        reader = csv.reader(fRead)
        writer = csv.writer(fWrite)
        for i, row in enumerate(reader):
            writer.writerow(row)

            if i > maxLines:
                break

# func = 'multiobjective'
# createTest(func, 2e6)
# dbSetup.setupTables(overwrite=True)
# dbSetup.loadDatabases()

