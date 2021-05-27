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
    ## If we have a floor, food, or door tile
    if cell.angleType == AngleType.na or cell.rotationType == RotationType.na: #avoid angleType doesn't exist Exception
        for i in range(3):
            if cells[i].cellType == cell.cellType:
                return i
    for x in cells:
        if x.angleType == AngleType.na or x.rotationType == RotationType.na: #avoid angleType doesn't exist Exception
            continue
        if x.cellType == cell.cellType and al.findDir(x.rotationType, x.angleType) == al.findDir(cell.rotationType, cell.angleType) and x.thickType == cell.thickType:
            return cells.index(x)
    return None

def checkValidity(board):
    """
    Take in a board and check to see that it is valid (door, floor, and food in proper place)
    """
    # trap[4]  = 1  # Food
    # trap[7]  = 2  # Floor
    # trap[10] = 0  # Door
    return board[4] == 1 and board[7] == 2 and board[10] == 0

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