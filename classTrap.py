from classCell import *
from typeCell import *
from classBoard import *
from classFloor import *
from classFood import *
from classArrow import *
from classWire import *
from classDoor import *
import algorithms as alg

class Trap(Board):
    def __init__(self, rowLength, colLength, functional, chosenBoard=None):
        """initializes a trap with a real or random trap (based on functional) or with a given board
        dimensions are always row=3 col=4 for our experiment, and the random generation methods are all for 3x4"""
        self.func = functional
        super().__init__(rowLength, colLength)
        if chosenBoard:
            self.board = super().realTrap(rowLength, colLength, chosenBoard)
        elif functional:
            self.board = super().realTrap(rowLength, colLength)
        else:
            self.board = self.randomBoard()

    def randomBoard(self):
        """sets own board to a random trap"""
        trapboard = sampleRandomBoards(1)[0]
        for cell in alg.flatten(trapboard):
            cell.ownerBoard = self
        return trapboard

def sampleRandomBoards(n):
    """returns a list of randomly generated traps"""
    trapboards = []
    num_left = n
    while num_left > 0:
        trap_stack = generateTrapStack(int(num_left / 0.21)) #generally, just over 21% of traps remain after filtering
        new_boards = trapStackToTrapBoards(trap_stack)
        num_left -= len(new_boards)
        trapboards += new_boards
    trapboards = trapboards[:n]
    return trapboards

def generateTrapStack(n):
    """randomly generates traps in numpy stack form"""
    num_cells = 9
    num_component_types = 9
    num_wire_thicknesses = 3
    num_rotations = 4

    component = np.random.randint(0, num_component_types, size=(n, num_cells))
    thickness = np.random.randint(0, num_wire_thicknesses, size=(n, num_cells))
    rotation = np.random.randint(0, num_rotations, size=(n, num_cells))

    trap_stack = np.dstack((component, thickness, rotation))
    return trap_stack

def trapStackToTrapBoards(trap_stack):
    """converts a given trap stack into a list of trap boards"""
    trapboard_list = []
    for trap_layer in trap_stack:
        prob_keep = probKeep(trap_layer) # correct probability distribution of traps, because generation method is simplified
        if np.random.binomial(n=1, p=prob_keep) == 1:
            cell_list = []
            for cell_info in trap_layer:
                cell = cellInfoToCell(cell_info)
                cell_list.append(cell)
            trapboard = cellListToTrapBoard(cell_list)
            trapboard_list.append(trapboard)
    return trapboard_list

def cellInfoToCell(cell_info):
    """takes the representation of a cell (in a trap stacK) and returns the actual cell"""
    thickTypes = [ThickType.skinny, ThickType.normal, ThickType.wide]
    rotationTypes = [RotationType.up, RotationType.right, RotationType.down, RotationType.left]
    angleTypes = [AngleType.na, AngleType.lacute, AngleType.racute, AngleType.lright, AngleType.rright, AngleType.lobtuse, AngleType.robtuse, AngleType.lright, AngleType.straight]
    component, thickness, rotation = cell_info
    if component == 0: # 0 = floor
        cell = Floor(0,0,None)
        return cell
    else:
        thickType = thickTypes[thickness]
        rotationType = rotationTypes[rotation]
        angleType = angleTypes[component]
        if component <= 6: # 1-6 = arrows
            return Arrow(0,0,None,angleType=angleType,rotationType=rotationType,thickType=thickType)
        else: # 7-8 = wires
            return Wire(0,0,None,angleType=angleType,rotationType=rotationType,thickType=thickType)

def cellListToTrapBoard(cell_list):
    """takes a list of cell objects and creates a trapboard"""
    trapboard = [
        [0, 0, 0],
        [0, Food(1,1,None), 0],
        [0, Floor(1,2,None), 0],
        [0, Door(1,3,None), 0],
    ]
    path = [(0,3),(0,2),(0,1),(0,0),(1,0),(2,0),(2,1),(2,2),(2,3)]
    for i in range(len(cell_list)):
        cell = cell_list[i]
        x, y = path[i]
        cell.x = x
        cell.y = y
        trapboard[y][x] = cell
    return trapboard

def probKeep(trap_layer):
    """returns the probability that a trap should be kept, in order to fix the distribution of random trap generation"""
    num_floor = 0
    num_straight = 0
    for cell_info in trap_layer:
        component, thickness, rotation = cell_info
        if component == 0: # floor
            num_floor += 1
        elif component == 8: #straight
            num_straight += 1
    prob_keep = 1
    prob_keep *= (1/12)**num_floor
    prob_keep *= (1/2)**num_straight
    return prob_keep