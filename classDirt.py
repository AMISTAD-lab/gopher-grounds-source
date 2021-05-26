from typeCell import *
from typeAngle import *
from typeRotation import *
from typeThick import *
import classCell as c

class Dirt(c.Cell):
    def __init__(self, x, y, ownerBoard, angleType=AngleType.na, rotationType=RotationType.na, thickType=ThickType.na, active=False):
        super().__init__(x, y, CellType.dirt, ownerBoard)