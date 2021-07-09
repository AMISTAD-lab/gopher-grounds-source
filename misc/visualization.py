from typing import List
import os
from PIL import Image
import webbrowser
from classes.Trap import Trap
import geneticAlgorithm.utils as utils
import geneticAlgorithm.encoding as enc
import libs.simulation as sim
import libs.visualize as vis

def getCellsFromStr(strEncoding: str) -> Trap:
    ''' Takes in a string encoding and returns a trap '''
    decoded = enc.singleDecoding(utils.convertStringToEncoding(strEncoding))
    cells = utils.createTrap(decoded).saveCells()

    return cells

def getImages(cells: List[str], activeList: List[int]) -> List[Image.Image]:
    ''' Get images from the the cells given, with activity determined by activeList '''

    # Define lists to generate image names
    cellTypes = ["gopher", "door", "wire", "arrow", "dirt", "food", "floor"]
    angleTypes = ["lacute", "racute", "lright", "rright", "lobtuse", "robtuse", "straight"]
    thickTypes = ["skinny", "normal", "wide"]

    imgList = []
    flattened = [col for row in cells for col in row]
    for i, cell in enumerate(flattened):
        cellCh, angleCh, thickCh, rotationCh = cell
        isActive = activeList[i]
        
        # Create subfields of image path
        cell = cellTypes[int(cellCh)] if cellCh != 'x' else ''
        angle = angleTypes[int(angleCh)] if angleCh != 'x' else ''
        thick = thickTypes[int(thickCh)] if thickCh != 'x' else ''
        active = 'active' if isActive else 'inactive'
        rotation = 45 * int(rotationCh) if rotationCh != 'x' else 0

        # Create image path and load it
        imageName = './animation/{cell}{thick}/{cell}{angle}{thick}{active}.png'.format(
                cell=cell, angle=angle, thick=thick, active=active
            )
        image = Image.open(imageName).rotate(-rotation)

        # Rotate the image
        imgList.append(image)

    # Add row of dirt at the bottom
    dirtImage = './animation/dirt/dirtinactive.png'
    for _ in range(3):
        imgList.append(Image.open(dirtImage))

    return imgList

def createImage(images: List[Image.Image], showGopher=True) -> Image.Image:
    ''' Takes in a list of 15 images and creates a trap image from it '''
    # Define constants for image
    width, height = images[0].width, images[0].height
    numRows, numCols = 5, 3

    # Create new background image on which to paste
    fullImage = Image.new('RGB', (numCols * width, numRows * height))
    
    # Add all background images for the trap
    for i in range(numRows):
        for j in range(numCols):
            x = j * width
            y = i * height
            fullImage.paste(images[j + i * numCols], (x, y))

    # Show the gopher and use the gopher as a mask to keep background transparent
    if showGopher:
        gopherImage = Image.open('./animation/gopher/gopheralive.png')
        fullImage.paste(gopherImage, (width, 4 * height), gopherImage)
    
    return fullImage

def convertTrapToImage(strEncoding: List[str], imageName: str, showGopher=True, showPDF=False):
    ''' Takes in the string encoding of a trap and converts it to an image '''
    cells = getCellsFromStr(strEncoding)
    images = getImages(cells, 12 * [0])
    finalImage = createImage(images, showGopher)

    finalImage.save(f'./images/traps/{imageName}.pdf')

    if showPDF:
        finalImage.show(title=f'{imageName}.png')

def simulateTrapInBrowser(trapEncoding, hunger=0, intention=False, noAnimation=False, gopherState=[1, 4, 0, 1], frame = 0):
    """Takes in a list encoding and simulates the trap in the browser"""
    decodedList = enc.singleDecoding(trapEncoding)
    simulationInfo = sim.simulateTrap(utils.createTrap(decodedList), intention, hunger=hunger, forceEnter=True)[:3]
    vis.writeTojs([simulationInfo], noAnimation, gopherState, frame)

    # opens the animation in the web browser
    webbrowser.open_new_tab("file://" + os.path.realpath("./animation/animation.html"))