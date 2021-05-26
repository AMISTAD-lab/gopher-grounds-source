from typeDirection import *
from typeThick import *
import simulation as s
import magicVariables as mv


class Projectile:

    def __init__(self, start_x, start_y, direction, thickType, ownerBoard, timeStep):
        self.direction = direction
        self.strength = self.assignStrength(thickType) 
        self.x = start_x
        self.y = start_y  
        self.ownerBoard = ownerBoard
        self.landProjectile(timeStep)

  
    def landProjectile(self, timeStep):
        """this method figures out where the projectile lands when moving in the given direction"""
        s.gopher.trapTriggered() #tells gopher that trap has been triggered
        while self.x >= 0 and self.x < self.ownerBoard.rowLength and self.y >= 0 and self.y < self.ownerBoard.colLength:
            #while in bounds of trap
            if self.checkHitGopher(timeStep):
                break
            if self.direction in [DirectionType.right, DirectionType.upperright, DirectionType.lowerright]:
                self.x += 1
            if self.direction in [DirectionType.left, DirectionType.upperleft, DirectionType.lowerleft]:
                self.x -= 1
            if self.direction in [DirectionType.up, DirectionType.upperleft, DirectionType.upperright]:
                self.y -= 1
            if self.direction in [DirectionType.down, DirectionType.lowerleft, DirectionType.lowerright]:
                self.y += 1
    

    def checkHitGopher(self, timeStep):
        """determines if the gopher has been hit and tells the gopher it has been hit if so""" 
        if self.x == s.gopher.x and self.y == s.gopher.y:
            s.gopher.hitByProjectile(self, timeStep)
            return True
        return False

    def assignStrength(self, thicktype):
        """assigns strength based on thick type"""
        if(thicktype == ThickType.skinny):
            return mv.SKINNY_PROJECTILE_STRENGTH
        elif(thicktype == ThickType.normal):
            return mv.NORMAL_PROJECTILE_STRENGTH
        elif(thicktype == ThickType.wide):
            return mv.WIDE_PROJECTILE_STRENGTH
        else:
            raise Exception("Invalid thicktype")



    

