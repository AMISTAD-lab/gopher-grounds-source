import math
import random
from PIL import Image, ImageDraw
from typing import List, Tuple
from classes.Trap import Trap
from classes.Encoding import Encoding
import geneticAlgorithm.utils as utils

def getCellsFromStr(strEncoding: str, encoder: Encoding) -> Trap:
    ''' Takes in a string encoding and returns a trap '''
    decoded = encoder.decode(utils.convertStringToEncoding(strEncoding))
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
        imageName = f'./animation/{cell}{thick}/{cell}{angle}{thick}{active}.png'
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

def getPoint(point: Tuple[int, int]) -> Tuple[int, int]:
    ''' Returns the coordinates of the center of a cell '''
    image_width = 3072; image_height = 4096
    width, height = image_width // 3, image_height // 4
    return ((point[0] + 0.5) * width, (point[1] + 0.5) * height)    

def arrowedLine(im, ptA, ptB, width=40, color=(0,255,0)):
    """Draw line from ptA to ptB with arrowhead at ptB"""
    # Get drawing context
    draw = ImageDraw.Draw(im)
    # Draw the line without arrows

    # Now work out the arrowhead
    # = it will be a triangle with one vertex at ptB
    # - it will start at 95% of the length of the line
    # - it will extend 8 pixels either side of the line
    x0, y0 = ptA
    x1, y1 = ptB
    # Now we can work out the x,y coordinates of the bottom of the arrowhead triangle
    yb = 0.90 * (y1 - y0) + y0
    xb = 0.90 * (x1 - x0) + x0

    # Work out the other two vertices of the triangle
    # Check if line is vertical
    if x0==x1:
        vtx0 = (xb-150, yb)
        vtx1 = (xb+150, yb)

        if (y0 < y1):
            scale = 0.95
        else:
            scale = 1.05
        line_coords = (ptA, (x1, scale * y1))
    # Check if line is horizontal
    elif y0==y1:
        if (x0 < x1):
            scale = 0.95
        else:
            scale = 1.05

        vtx0 = (xb, yb+150)
        vtx1 = (xb, yb-150)

        line_coords = (ptA, (scale * x1, y1))
    else:
        alpha = math.atan2(y1 - y0, x1 - x0) - 90 * math.pi / 180
        a = 100*math.cos(alpha)
        b = 100*math.sin(alpha)
        vtx0 = (xb+a, yb+b)
        vtx1 = (xb-a, yb-b)

        line_coords = (ptA, (x1 + 0.12 * x1, y1 - 0.07 * alpha * x1))

    draw.line(line_coords, width=width, fill=color)

    #draw.point((xb,yb), fill=(255,0,0))    # DEBUG: draw point of base in red - comment out draw.polygon() below if using this line
    #im.save('DEBUG-base.png')              # DEBUG: save

    # Now draw the arrowhead triangle
    draw.polygon([vtx0, vtx1, ptB], fill=color)
    return im
