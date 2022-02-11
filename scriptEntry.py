# import misc.visualization as vis
from classes.Encoding import Encoding

# vis.create_gif_from_trap('[19  4  4 10 61  2 47  5 17  0  2  1]', Encoding(code=1))


import geneticAlgorithm.utils as utils
trap = '[12  6 15 18  1 46  7  2 92 19  0 46]'

print(utils.convertStringToEncoding(trap))
print(Encoding().decode(utils.convertStringToEncoding(trap)))
print(len(Encoding().decode(utils.convertStringToEncoding(trap))))
print(utils.createTrap(Encoding().decode(utils.convertStringToEncoding(trap))))

