import csv
from typing import Tuple
import geneticAlgorithm.constants as constants
import misc.csvUtils as csvUtils

def create_test_data(funcs: Tuple[str], num_files=25, num_rows=10000):
    '''
    Takes in a list of fitness function names and creates `num_files`
    test files with the first `num_rows` of the original file in a test_data
    directory
    '''
    file_names = [f'_new_enc_{i + 1}' for i in range(num_files)]

    ## Create test data
    for func in funcs:
        for file in file_names:
            write_data = []
            input_path = constants.frequencyPath.format(enc='new_encoding', func=func, suff=file)
            output_path = f'./test_data/{func}/{func}{file}.csv'

            with open(input_path, 'r', newline='') as out:
                for i, row in enumerate(csv.reader(out)):
                    if i > num_rows:
                        break
                
                    write_data.append(row)
            
            csvUtils.updateCSV(output_path, data=write_data, overwrite=True)
    