from classes.Door import *
from classes.Floor import *
from classes.Food import *
from classes.Dirt import *
from classes.Wire import *
from classes.Arrow import *
from classes.Cell import *
import algorithms as al

cells = []

#add floor
cells.append(Cell(0,0, CellType.floor, None))

#add door
cells.append(Cell(0,0, CellType.door, None))

#add food
cells.append(Cell(0,0, CellType.food, None))

#add straight wires
for x in range(0,3,2): 
    for y in range(3): 
        cells.append(Cell(0,0, CellType.wire, None, angleType=AngleType.straight, rotationType=RotationType(x), thickType=ThickType(y)))

#add right angle wires
for x in range(0,7,2): 
    for y in range(3): 
        cells.append(Cell(0,0, CellType.wire, None, angleType=AngleType.rright, rotationType=RotationType(x), thickType=ThickType(y)))

#add arrows
for angle in range(6):
    for x in range(0,7,2):
        for y in range(3):
            cells.append(Cell(0,0, CellType.arrow, None, angleType=AngleType(angle), rotationType=RotationType(x), thickType=ThickType(y)))


def find_index(cell):
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

#testing
'''
cell1 = Cell(0,0, CellType.wire, None, angleType=AngleType.straight, rotationType=RotationType.up, thickType=ThickType.skinny)   
cell2 = Cell(0,0, CellType.arrow, None, angleType=AngleType.robtuse, rotationType=RotationType.up, thickType=ThickType.wide)
cell3 = Cell(0,3, CellType.wire, None,  angleType=AngleType.lright, rotationType=RotationType.left, thickType=ThickType.wide)
cell4 = Food(2,0, None)

print(find_index(cell1))
print(find_index(cell2))
print(find_index(cell3))
print(find_index(cell4))
'''