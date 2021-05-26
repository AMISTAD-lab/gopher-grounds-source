from typeCell import *
from classFloor import *
from typeRotation import *
import algorithms as alg
import numpy as np
import magicVariables as mv

class Gopher:
    def __init__(self, start_x, start_y, ownerBoard, intention, rotationType=RotationType.up):
        self.intention = intention
        self.ownerBoard = ownerBoard
        self.rotationType = rotationType
        self.alive = True
        self.hit = False
        self.x = start_x
        self.y = start_y
        self.entering = False
        self.leaving = False
        self.left = False
        self.hasEaten = False
        self.eatingTimer = 0
        self.initialTimer = 0
        self.hunger = 0
        self.thoughtReal = False

    def state(self):
        """returns the state of the gopher as an integer"""
        if not self.alive:
            state = 0
        elif self.hit:
            state = 2
        else:
            state = 1
        return state

    def updateCell(self):
        """decides what the gopher should do and does it (named updateCell for ease in calling)"""
        if self.hit:
            self.hit = False
        if self.entering:
            self.rotationType = RotationType.up
            self.enter()
        elif self.leaving:
            self.rotationType = RotationType.down
            self.leave()
        elif self.eatingTimer > 0:
            self.eat()
        else:
            if self.intention:
                self.thoughtReal = mv.DECISION_ALG(self.ownerBoard)
                enterGivenTrap = 1 - self.thoughtReal
                if self.hunger == 1:
                    probEnter = 1
                else:
                    probEnter = enterGivenTrap
            else:
                enterGivenTrap = mv.DEFAULT_PROB_ENTER
                hungerWeight = self.hunger**10
                probEnter = enterGivenTrap * (1 - hungerWeight) + hungerWeight
            if np.random.binomial(n=1, p=probEnter):
                self.initialTimer = alg.gopherEatTimer(enterGivenTrap)
                self.entering = True
                self.leaving = False
            else:
                self.entering = False
                self.leaving = False
                self.left = True

    def enter(self):
        """moves the gopher towards the center of the trap"""
        self.y -= 1
        if self.ownerBoard.board[self.y][self.x].cellType == CellType.food:
            self.eatingTimer = self.initialTimer
            self.entering = False
            self.leaving = False
    
    def leave(self):
        "moves the gopher to the exit of the trap"
        self.y += 1
        self.eatingTimer = 0
        if self.ownerBoard.board[self.y-1][self.x].cellType == CellType.door:
            self.entering = False
            self.leaving = False
            self.left = True

    def eat(self):
        """has the gopher consume food, or leave if done eating"""
        self.eatingTimer -= 1
        if self.eatingTimer <= 0:
            self.hasEaten = True
            self.leaving = True
            self.entering = False

    def trapTriggered(self):
        """tells gopher to leave once a projectile is fired"""
        self.leaving = True
        self.entering = False

    def hitByProjectile(self, projectile, timeStep):
        """determines if gopher is killed when hit by a projectile, 
        and tells gopher to leave if still alive"""
        if np.random.binomial(1, projectile.strength) == 1:
            self.alive = False
        else:
            self.hit = True
            self.leaving = True
            self.entering = False
            


