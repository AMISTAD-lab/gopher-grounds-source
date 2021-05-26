from typeCell import *
from typeRotation import *
from typeDirection import *
import classCell as c
import algorithms as alg

class Wire(c.Cell):
    def __init__(self, x, y, ownerBoard, angleType, rotationType, thickType, active=False):
        self.directionType = alg.findDir(rotationType, angleType)
        endpoints = c.getEndpoints(self.directionType, rotationType)
        super().__init__(x, y, CellType.wire, ownerBoard, angleType=angleType, rotationType=rotationType, thickType=thickType, endpoints=endpoints, active=active)

    def updateCell(self, timeStep):
        """will be called once every time step from simulation"""
        if self.active and timeStep > self.activatedTimeStep:
            #do its thing if its active (and not same turn that it was activated) -- important so that this works independent of order of cells updating
            self.attemptTransfer(timeStep)
            self.active = False