import shutil as sh 
import legacy.experiment as exp

newjsFileName = "animation/animation.js" # will write and read files in the animation folder.
singleTemplateName = "animation/singleTrapTemplate.js"
multipleTemplateName = "animation/multipleTrapTemplate.js"

def writeTojs(trapList, isSingle = True):
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
    jsTemplateName = singleTemplateName if isSingle else multipleTemplateName
    newFile = open(newjsFileName, "w") # create new file
    newFile.close()
    sh.copy(jsTemplateName, newjsFileName) # copy contents of template to new file
    jsFile = open(newjsFileName, "a") # open the file to append to
    jsFile.write("function getInput(){\n")
    jsFile.write("trapList = " + str(trapList) + ";\n")
    jsFile.write("}")
    jsFile.close()
