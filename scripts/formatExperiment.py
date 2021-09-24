import csv
import geneticAlgorithm.utils as utils

input_files = [f'./experiments/{{func}}/{{func}}_new_enc_{i + 1}.csv' for i in range(25)]

for func in ('binary-distance', 'coherence', 'functional', 'multiobjective', 'random'):
    for input_file in input_files:

        input_file = input_file.format(func = func)
        write_data = []

        with open(input_file, 'r', newline='') as out:
            for i, row in enumerate(csv.reader(out)):
                if i == 0:
                    write_data.append(row)
                    continue

                write_data.append([*row[:2], utils.convertStringToEncoding(row[2]), *row[3:]])

        with open(input_file, 'w+', newline='') as out:
            csv.writer(out).writerows(write_data)
