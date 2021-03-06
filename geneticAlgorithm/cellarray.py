from classes.Arrow import Arrow
from classes.Door import Door
from classes.Floor import Floor
from classes.Food import Food
from classes.Wire import Wire

from enums.Angle import AngleType
from enums.Cell import CellType
from enums.Rotation import RotationType
from enums.Thick import ThickType

cells = []

#add door
cells.append(Door(0,0, None))

#add food
cells.append(Food(0,0, None))

#add floor
cells.append(Floor(0,0, None))

#add straight wires
for x in [0, 2]: 
    for y in range(3):
        cells.append(Wire(0, 0, None, angleType=AngleType.straight, rotationType=RotationType(x), thickType=ThickType(y)))

#add right angle wires
for x in [0, 2, 4, 6]: 
    for y in range(3):
        cells.append(Wire(0, 0, None, angleType=AngleType.rright, rotationType=RotationType(x), thickType=ThickType(y)))

#add arrows
for angle in range(6):
    for x in [0, 2, 4, 6]:
        for y in range(3):
            cells.append(Arrow(0, 0, None, angleType=AngleType(angle), rotationType=RotationType(x), thickType=ThickType(y)))

def findIndex(cell):
    """
    Takes a given cell and finds the index associated with that cell. Two-way casting is necessary for encoding/decoding
    """
    for i in range(len(cells)):
        if compareCells(cell, cells[i]):
            return i

    return None

def compareCells(inputCell, listCell):
    """
    Takes in two cells and returns true if and only if they are functionally the same cell
    """
    # If not the same cell type or thickness, then they are definitely not the same cell
    if inputCell.cellType != listCell.cellType:
        return False

    if inputCell.thickType != listCell.thickType:
            return False

    if inputCell.cellType in [CellType.floor, CellType.food, CellType.door]:
        return True
    
    if inputCell.cellType == CellType.wire:
        bothStraight = inputCell.angleType == AngleType.straight and listCell.angleType == AngleType.straight
        bothAngled = inputCell.angleType != AngleType.straight and listCell.angleType != AngleType.straight

        # If the wires have different shapes, then they aren't the same
        if not (bothStraight or bothAngled):
            return False

        if bothStraight:
            return (inputCell.rotationType.value % 4 == listCell.rotationType.value % 4)

        if bothAngled:
             # Input cells can be left or right angled, but list cells are only right angled
            isRight = (inputCell.angleType == AngleType.rright)
            if isRight:
                return inputCell.rotationType == listCell.rotationType
            else:
                return (inputCell.rotationType.value + 2) % 8 == listCell.rotationType.value
        else:
            return False

    if inputCell.cellType == CellType.arrow:
        return inputCell.angleType == listCell.angleType and inputCell.rotationType == listCell.rotationType

    raise Exception("Undefined cell type in compareCells")
