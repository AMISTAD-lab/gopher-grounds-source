from classCell import *
from typeCell import *
from typeAngle import *
from typeRotation import *
from typeThick import *
import simulation as s

class Door(Cell):
    def __init__(self, x, y, ownerBoard, angleType=AngleType.na, rotationType=RotationType.up, active=False):
        endpoints = [(rotationType.value + 2) % 8, (rotationType.value + 6) % 8]
        super().__init__(x, y, CellType.door, ownerBoard, angleType, rotationType, endpoints=endpoints, thickType=ThickType.na, active=active)

    def updateCell(self, timeStep):
        if s.gopher.x == self.x and s.gopher.y == self.y:
            self.launchSignal(timeStep)

    def launchSignal(self, timeStep):
        self.attemptTransfer(timeStep)