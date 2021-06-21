from classes.Cell import *
from enums.Cell import *
from enums.Angle import *
from enums.Rotation import *
from enums.Thick import *
import libs.simulation as s

class Door(Cell):
    def __init__(self, x, y, ownerBoard, angleType=AngleType.na, rotationType=RotationType.up, active=False):
        endpoints = [(rotationType.value + 2) % 8, (rotationType.value + 6) % 8]
        super().__init__(x, y, CellType.door, ownerBoard, angleType, rotationType, endpoints=endpoints, thickType=ThickType.na, active=active)

    def updateCell(self, timeStep):
        if s.gopher.x == self.x and s.gopher.y == self.y:
            self.launchSignal(timeStep)

    def launchSignal(self, timeStep):
        self.attemptTransfer(timeStep)