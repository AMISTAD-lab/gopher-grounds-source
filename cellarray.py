from classes.Door import *
from classes.Floor import *
from classes.Food import *
from classes.Dirt import *
from classes.Wire import *
from classes.Arrow import *
from classes.Cell import *
import algorithms as al

cells = []

#add door
cells.append(Cell(0,0, CellType.door, None))

#add food
cells.append(Cell(0,0, CellType.food, None))

#add floor
cells.append(Cell(0,0, CellType.floor, None))

#add straight wires
for x in [0, 2]: 
    for y in range(3):
        cells.append(Cell(0, 0, CellType.wire, None, angleType=AngleType.straight, rotationType=RotationType(x), thickType=ThickType(y)))

#add right angle wires
for x in [0, 2, 4, 6]: 
    for y in range(3):
        cells.append(Cell(0, 0, CellType.wire, None, angleType=AngleType.rright, rotationType=RotationType(x), thickType=ThickType(y)))

#add arrows
for angle in range(6):
    for x in [0, 2, 4, 6]:
        for y in range(3):
            cells.append(Cell(0, 0, CellType.arrow, None, angleType=AngleType(angle), rotationType=RotationType(x), thickType=ThickType(y)))

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
            return (inputCell.rotationType.value % 4 == listCell.rotationType.value)

        if bothAngled:
             # Input cells can be left or right angled, but list cells are only right angled
            isRight = (inputCell.angleType == AngleType.rright)
            if isRight:
                return isRight and inputCell.rotationType == listCell.rotationType
            else:
                return (inputCell.rotationType.value + 2) % 8 == listCell.rotationType.value
        else:
            return False

    if inputCell.cellType == CellType.arrow:
        return inputCell.angleType == listCell.angleType and inputCell.rotationType == listCell.rotationType

    raise Exception("Undefined cell type in compareCells")

#testing
'''
cell1 = Cell(0,0, CellType.wire, None, angleType=AngleType.straight, rotationType=RotationType.up, thickType=ThickType.skinny)   
cell2 = Cell(0,0, CellType.arrow, None, angleType=AngleType.robtuse, rotationType=RotationType.up, thickType=ThickType.wide)
cell3 = Cell(0,3, CellType.wire, None,  angleType=AngleType.lright, rotationType=RotationType.left, thickType=ThickType.wide)
cell4 = Food(2,0, None)

print(findIndex(cell1))
print(findIndex(cell2))
print(findIndex(cell3))
print(findIndex(cell4))
'''

# cell1 = Cell(0, 0, CellType.wire, None, angleType=AngleType.rright, rotationType=RotationType(6), thickType=ThickType(0))
# cell2 = Cell(0, 0, CellType.wire, None, angleType=AngleType.lright, rotationType=RotationType(4), thickType=ThickType(0))
# print(compareCells(cell2, cell1))