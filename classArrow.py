from typeCell import *
from classCell import *
from typeAngle import *
from typeRotation import *
from classProjectile import *
import algorithms as alg

class Arrow(Cell):
    def __init__(self, x, y, ownerBoard, angleType, rotationType, thickType, active=False):
        endpoints = [(rotationType.value + 4) % 8]
        super().__init__(x, y, CellType.arrow, ownerBoard=ownerBoard, angleType=angleType, rotationType=rotationType, thickType=thickType, endpoints=endpoints, active=active)
  

    def updateCell(self, timeStep):
        """this method updates the arrow every time step from simulation"""
        if self.active and timeStep > self.activatedTimeStep:
            #do its thing if its active (and not same turn that it was activated) -- important so that this works independent of order of cells updating
            self.launchProjectile(timeStep)
            self.active = False

    def launchProjectile(self, timeStep):
        direction = alg.findDir(self.rotationType, self.angleType)
        #launch projectile
        Projectile(self.x, self.y, direction, self.thickType, self.ownerBoard, timeStep)