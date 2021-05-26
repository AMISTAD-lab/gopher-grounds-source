from classGopher import *

import algorithms as alg
import math as m
import numpy as np

gopher = None    
    
def simulateTrap(trap, intention, hunger=0, maxSteps=20):
    """runs a simulation of a single trap and returns the relevant data"""
    center_x = m.ceil(trap.rowLength / 2) - 1
    global gopher
    gopher = Gopher(center_x, trap.colLength, trap, intention)
    gopher.hunger = hunger
    step = 0
    initialboard = trap.saveCells()
    initialboard.append(["4xxx"]*trap.rowLength) #add dirt beneath trap
    activeCells = []
    gopherStuff = []
    thoughtReal = False
    while gopher.alive and not gopher.left and step < maxSteps:
        gopherInfo, state = updateSimulation(trap, step)
        if gopher.thoughtReal:
            thoughtReal = True
        activeCells.append(state)
        gopherStuff.append(gopherInfo)
        step += 1
    return [initialboard, activeCells, gopherStuff, gopher.alive, gopher.hasEaten, thoughtReal]

def updateSimulation(trap, step):
    """steps through the simulation"""
    global gopher
    gopher.updateCell()
    for cell in alg.flatten(trap.board):
        cell.updateCell(step)
    state = trap.saveState()
    state.append([0]*trap.rowLength) #add inactive dirt beneath trap
    gopherInfo = [gopher.x, gopher.y, gopher.rotationType.value, gopher.state()]
    return gopherInfo, state

def viewRun(initialboard, activeCells, gopherCells):
    """view a simulation run step by step in terminal instead of with animation"""
    rowLength = len(initialboard[0])
    colLength = len(initialboard)
    active = lambda x,y,step: "A" if activeCells[step][y][x] == 1 else "I"
    for step in range(len(activeCells)):
        displayBoard = []
        for y in range(colLength):
            row = []
            for x in range(rowLength):
                if gopherCells[step][:2] == [x,y]:
                    row.append("GPR" + str(gopherCells[step][2]) + str(gopherCells[step][3]))
                else:
                    row.append(initialboard[y][x] + active(x,y,step))
            displayBoard.append(row)
        print("STEP", step)
        print(alg.formatMatrix(displayBoard))