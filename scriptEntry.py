import libs.simulation as s
import geneticAlgorithm.utils as u
from classes.Encoding import Encoding

encoder = Encoding(code=1)
trap = [68, 2, 2, 2, 2, 2, 2, 2, 2, 0, 2, 1] # firing trap, but not hitting
trapinfo = s.simulateTrap(u.createTrap(encoder.decode(trap)), False, is_brave=True)
print(trapinfo)