import numpy as np
import shutil as sh 
import experiment as exp

newjsFileName = "animation/animation.js" # will write and read files in the animation folder.
jsTemplateName = "animation/template.js"

def writeTojs(trapList):
    """ 
    Inputs:
        trapList: a list with elements of the form [initTrapBoard, activeTrapCells, gopherTrapCells]
            initTrapBoard: initial board for a trap.
            activeTrapCells: list of 2d lists with 1's in positions that are active, 0's otherwise.
            gopherTrapCells: List of tuples (each tuple is: [x, y, rotationType, state])
        terrainList: a list of the form [initTerrainBoard, gopherTerrainCells]
            initTerrainBoard: the initial board for the terrain (just a single 2d list!)
            gopherTerrainCells: list of tuples (each tuple is: [x, y, rotationType]) (state is always alive)
    """  
    newFile = open(newjsFileName, "w") # create new file
    newFile.close()
    sh.copy(jsTemplateName, newjsFileName) # copy contents of template to new file
    jsFile = open(newjsFileName, "a") # open the file to append to
    jsFile.write("function getInput(){\n")
    jsFile.write("trapList = " + str(trapList) + ";\n")
    jsFile.write("}")
    jsFile.close()


# runs the animation.
#animationData = exp.simulate(exp.pref)[1] # returns list of initial board, active cells, gopher cells
#writeTojs(animationData) # write to the js file.