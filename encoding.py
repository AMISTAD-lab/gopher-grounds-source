import cellarray as ca
import numpy as np
import itertools
from classes.Door import *
from classes.Floor import *
from classes.Food import *
from classes.Dirt import *
from classes.Wire import *
from classes.Arrow import *
from classes.Cell import *

def flatten_list(listoflist):
    flatten_trap = list(itertools.chain(*listoflist))
    return flatten_trap

def encoding(trap):
    encoded = []
    flatten_trap = flatten_list(trap)
    for cell in flatten_trap:
        encoded.append(ca.find_index(cell))
    return encoded

#testing#
'''
trap7 = [
    [Arrow(0,0, None, angleType=AngleType.racute, rotationType=RotationType.up, thickType=ThickType.wide), Floor(1,0, None),  Floor(2,0, None)],
    [Wire(0,1,None, angleType=AngleType.straight, rotationType=RotationType.up, thickType=ThickType.wide), Food(1,1, None), Arrow(2,1, None, angleType=AngleType.lright, rotationType=RotationType.up, thickType=ThickType.wide)],
    [Wire(0,2,None, angleType=AngleType.straight, rotationType=RotationType.up, thickType=ThickType.wide), Floor(1,2, None), Wire(2,2, None, angleType=AngleType.straight, rotationType=RotationType.up, thickType=ThickType.wide)],
    [Wire(0,3,None, angleType=AngleType.rright, rotationType=RotationType.left, thickType=ThickType.wide), Door(1,3, None), Wire(2,3, None, angleType=AngleType.lright, rotationType=RotationType.right, thickType=ThickType.wide)]
]
print(flatten_list(trap7))
print(encoding(trap7))
'''