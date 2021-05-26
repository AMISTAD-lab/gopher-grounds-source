from enums.Cell import *
from enums.Angle import *
from enums.Rotation import *
from enums.Thick import *
import classes.Cell as c

class Food(c.Cell):
    def __init__(self, x, y, ownerBoard, angleType=AngleType.na, rotationType=RotationType.na, thickType=ThickType.na, active=False):
        super().__init__(x, y, CellType.food, ownerBoard)
