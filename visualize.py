import shutil as sh 
import geneticAlgorithm.utils as util

newjsFileName = "animation/animation.js" # will write and read files in the animation folder.
template = "animation/template.js"

def writeTojs(trapList, noAnimation=False, gopherState=[1, 4, 0, 1]):
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
    jsTemplateName = template
    newFile = open(newjsFileName, "w") # create new file
    newFile.close()

    sh.copy(jsTemplateName, newjsFileName) # copy contents of template to new file

    gopherState = util.convertEncodingToString(gopherState)

    jsFile = open(newjsFileName, "a") # open the file to append to
    jsFile.write("function getInput(){\n")
    jsFile.write("\ttrapList = " + str(trapList) + ";\n")
    jsFile.write("\tshowAnimation = {};\n".format(str(not noAnimation).lower()))
    jsFile.write("\tgopherDefaultState = {};\n".format(gopherState))
    jsFile.write("}")

    jsFile.close()
