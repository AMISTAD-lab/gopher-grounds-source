from classes.Arrow import Arrow
from classes.Wire import Wire
from enums.Angle import AngleType
from enums.Rotation import RotationType
from geneticAlgorithm.cellarray import compareCells
import geneticAlgorithm.constants as constants

"""
This file contains all of the functions necessary to calculate the function of a trap analytically
"""

def getProbabilityDistribution(probEnter = 0.8):
    """Calculates the probability distribution of eating time from the given probability of entrance"""
    idealTimer = probEnter * 5
    initialProbs = [0.05, 0.05, 0.05, 0.05, 0.05]
    for i in range(5):
        if idealTimer <= i + 1:
            initialProbs[i] = 0.6
            if i == 0:
                initialProbs[1] = 0.2
                initialProbs[2] = 0.1
            elif i == 4:
                initialProbs[3] = 0.2
                initialProbs[2] = 0.1
            else:
                initialProbs[i+1] = 0.15
                initialProbs[i-1] = 0.15

    return initialProbs

def getLeaveTime(timeLeft, timeRight, timeEat):
    """Get the time it takes for the gopher to leave a trap"""
    if timeLeft < 0:
        timeLeft = 3 + timeEat
    if timeRight < 0:
        timeRight = 3 + timeEat
    
    return min(timeLeft, timeRight, 3 + timeEat)

def getArrowData(configuration):
    """
    Takes in a board configuration and returns 2 tuples (for left and right paths) where the first element is the time at which the arrow fires (or -1 if the arrow does not fire),
    the second element is the cell that was hit (1, 2, 3 is door, floor, food respectively), and the third element is the thickness of the wire
    """
    # Initializing variables
    wire_angles = [
        AngleType.rright, AngleType.straight, AngleType.straight,
        AngleType.rright, AngleType.straight, AngleType.rright,
        AngleType.straight, AngleType.straight, AngleType.rright
    ]
    
    # Left path
    left_indices = [
        (0, 3), (0, 2), (0, 1),
        (0, 0), (1, 0), (2, 0),
        (2, 1), (2, 2), (2, 3)
    ]
    wire_left_rotations = [
        RotationType.left, RotationType.up, RotationType.up,
        RotationType.up, RotationType.right, RotationType.right,
        RotationType.up, RotationType.up, RotationType.up
    ]
    arrow_left_angles = [
        (AngleType.racute, ), (AngleType.racute, AngleType.rright, AngleType.robtuse), (AngleType.racute, AngleType.rright),
        (AngleType.racute, ), (AngleType.rright, ), (AngleType.racute, ),
        (AngleType.rright, AngleType.robtuse), (AngleType.racute, AngleType.rright, AngleType.robtuse), (AngleType.rright, AngleType.racute)
    ]
    arrow_left_rotations = [
        RotationType.left, RotationType.up, RotationType.up,
        RotationType.up, RotationType.right, RotationType.right,
        RotationType.down, RotationType.down, RotationType.down
    ]
    arrow_hits_left = [
        (2, ), (1, 2, 3), (2, 3),
        (3, ), (4, ), (3, ),
        (3, 2), (3, 2, 1), (1, 2)
    ]

    # Right path
    right_indices = [
        (2, 3), (2, 2), (2, 1),
        (2, 0), (1, 0), (0, 0),
        (0, 1), (0, 2), (0, 3)
    ]
    wire_right_rotations = [
        RotationType.down, RotationType.up, RotationType.up,
        RotationType.right, RotationType.right, RotationType.up,
        RotationType.up, RotationType.up, RotationType.left]
    arrow_right_angles = [
        (AngleType.lacute, ), (AngleType.lacute, AngleType.lright, AngleType.lobtuse), (AngleType.lacute, AngleType.lright),
        (AngleType.lacute, ), (AngleType.lright, ), (AngleType.lacute, ),
        (AngleType.lright, AngleType.lobtuse), (AngleType.lacute, AngleType.lright, AngleType.lobtuse), (AngleType.lacute, AngleType.lright)
    ]
    arrow_right_rotations = [
        RotationType.right, RotationType.up, RotationType.up,
        RotationType.up, RotationType.left, RotationType.left,
        RotationType.down, RotationType.down, RotationType.down
    ]
    arrow_hits_right = [
        (2, ), (1, 2, 3), (2, 3),
        (3, ), (4, ), (3, ),
        (3, 2), (3, 2, 1), (2, 1)
    ]

    # Initializing shared resources
    both_indices = (left_indices, right_indices)
    both_hits = (arrow_hits_left, arrow_hits_right)
    wire_rotations = []
    arrow_angles = arrow_rotations = []
    retData = []

    for i, indices in enumerate(both_indices):
        # Setting current angles
        if indices == left_indices:
            wire_rotations = wire_left_rotations
            arrow_angles = arrow_left_angles
            arrow_rotations = arrow_left_rotations
        else:
            wire_rotations = wire_right_rotations
            arrow_angles = arrow_right_angles
            arrow_rotations = arrow_right_rotations
        thickness = None
        
        for j, (x, y) in enumerate(indices):
            currCell = configuration[y][x]

            # If not an arrow or wire cell, the path is dead
            if not (isinstance(currCell, (Wire, Arrow))):
                retData.append((-1, -1, -1))
                break

            if isinstance(currCell, Wire):
                if j == 0:
                    thickness = currCell.thickType

                # The `listCell` argument requires that cells are in standard form (found in cell array file)
                if not compareCells(currCell, Wire(0, 0, None, wire_angles[j], wire_rotations[j], thickness)):
                    retData.append((-1, -1, -1))
                    break

                continue

            if isinstance(currCell, Arrow):
                sameRotation = currCell.rotationType == arrow_rotations[j]
                sameThickness = currCell.thickType == thickness if thickness else True

                if (currCell.angleType in arrow_angles[j] and sameRotation and sameThickness):
                    indexOfAngle = arrow_angles[j].index(currCell.angleType)
                    retData.append((j + 2, both_hits[i][j][indexOfAngle], currCell.thickType))
                    break
                else:
                    retData.append((-1, -1, -1))
                    break

    return retData[0], retData[1]

def gopherSurviveProb(arrowData, leaveTime):
    """
    Returns the probability that a gopher survives given the information of a arrow
    """
    time, cell, thickness = arrowData
    thickSurviveProb = [0.15, 0.3, 0.45]

    # If time < 0, then arrow does not hit, and gopher survives
    if time < 0:
        return 1

    # position as a function of time
    pos = lambda t : min(t, 3) if t <= leaveTime else min(leaveTime, 3) - (t - leaveTime)
    hit = int(pos(time) == cell or (pos(time) > 0 and cell == 4))
    return 1 - (hit * thickSurviveProb[thickness.value])

def trapLethality(configuration, defaultProbEnter = constants.DEFAULT_PROB_ENTER):
    """
    Takes in a board configuration and hunger level, and returns the probability the trap will kill the gopher
    """
    sumProb = 0
    leftData, rightData = getArrowData(configuration)

    # using default prob of entering as 0.8, gets the probabilities that a gopher will eat for a certain amount of time
    # we fix default prob enter as 0.8 for baseline gophers
    timeDist = getProbabilityDistribution(defaultProbEnter)
    for i, dist in enumerate(timeDist):
        leaveTime = getLeaveTime(leftData[0], rightData[0], i + 1)
        deathProb = 1 - gopherSurviveProb(leftData, leaveTime) * gopherSurviveProb(rightData, leaveTime)
        sumProb += deathProb * dist

    return sumProb * defaultProbEnter