/**  template.js 
Created on June 23, 2020 by Cynthia Hom
js file for the third experiment's animation.

This file is ultimately used as a template. The "writeTojs()" function in visualize.py will make a copy of this file,
call it animation.js, and add run-specific data by writing a getInput() method to animation.js.
animation.js is then used by animation.html to run the animation.*/


// select/create HTML elements
var gridContainer = document.getElementById("gridContainer");
var gopher = document.createElement("img");
gopher.id = "gopher";

var trapList = [] // Contains all the info for the steps of the animation and the traps to show.

var fps = 2; // show two frames per second

var trapNum = 0;	// the number of the trap to start the animation at
var trapFrameNum = 0; // current step of the trap 
var frameNum = 0; // frame count for the overall animation

// Calls init only once document has loaded.
$(document).ready(function () {
	init();
});

/** Called when file is run. */
function init() 
{
	getInput(); // get input that is written to the file.
	animate();
}

/** The animation. Calls draw. */
function animate(){
	timer = setTimeout(function(){
		requestAnimationFrame(animate);  
	}, 1000/fps); // repaint fps frames per second

	// animation ends after last trap has been run 
	if (trapNum >= trapList.length) 
	{
		// show the proper ending screen 
		showEndingImage();
		console.log("ANIMATION FINISHED");
		clearTimeout(timer);
		return;
	}

	draw();
	updateVars();
}

/** Draws one frame */
function draw(){
	console.log("trapFrameNum is " + trapFrameNum);
	if (frameNum < getNumStartSteps())
	{
		// show the first trap
		updateGrid(trapList[trapNum][0]);
	}
	// if moving to a trap or moving away from trap, update the grid and make gopher rotate. 
	else if (areChangingTraps())
	{
		updateGrid(getCurrentlyDisplayedGrid());
	}
	// otherwise, simply update the active states of the grid and the gopher position/rotation.
	else
	{
		updateActiveStates(); 
	}
	updateGopher();
}

/** Updates variables to move to next frame, etc. */
function updateVars(){
	frameNum++;
	trapFrameNum++;
	// if we have just finished starting sequence, then don't make gopher "move to" the trap again!
	if (frameNum == getNumStartSteps()){
		trapFrameNum = getTrapWidth();
	}
	// if done with this trap, then switch traps. If on the last trap, don't make gopher go to next trap. Note: not sure if this will work as well for hunger. 
	else if ((trapFrameNum > getCurrentGopherList().length + 2 * getTrapWidth()) ||
		(trapNum == trapList.length - 1 && trapFrameNum >= getCurrentGopherList().length + getTrapWidth()))
	{
		console.log("FINISHED TRAP #" + trapNum);
		trapNum++;	// move on to next trap.

		// reset trapFrameNum
		trapFrameNum = 0;
	}
}


/** Updates whether or not cells are active or not for the trap part of the animation. */
function updateActiveStates()
{
	activeStateList = trapList[trapNum][1][trapFrameNum - getTrapWidth()];
	// loop through, and give appropriate img element the correct src.
	for (let row = 0; row < activeStateList.length; row++){
		for (let col = 0; col < activeStateList[0].length; col++){
			cell = [row + 1, col + 1];
			if (!isValidGridPos(cell)){
				throw new Error("ERROR: Not a valid grid position");
				return;
			}

			// get image. Must use gridContainer, because otherwise we can't change the src attribute.
			let image = gridContainer.children[getNth(cell) - 1].children[0]; // subtract 1 because .children returns an array.
			// make sure image exists first
			if (image == undefined){
				throw new Error("ERROR: Image is undefined");
				return;
			}
			isActiveNum = activeStateList[row][col]; 
			image.src = getImageName(getCurrentlyDisplayedGrid()[row][col], isActiveNum);  // set image src
		}
	}
}

/** Moves the gopher and updates its image. */
function updateGopher(){
	// don't update the gopher on the very first frame of the simulation.
	if (frameNum <= 0)
		return;

	let gopherTuple = []
	// if we are changing traps, make gopher turn to right and be in center of trap area.
		// otherwise, make gopher do what it is supposed to according to input. 
	if (frameNum > 0 && frameNum < getNumStartSteps()){
		gopherTuple = [frameNum - 1, getTrapHeight() - 1, 2, 1]; // x then y. Subtract 1 because move mehtod adds one. Gopher state is 1, which is normal.
		gopher.src = getGopherImageName(gopherTuple); // update gopher image
		gopher.style.transform = "rotate(90deg)";
	}
	else if (frameNum != 0 && areChangingTraps()){
		gopherTuple = getCurrentGopherList()[0]; // make gopher show up in center, ie. same state as its first step in trap animation.
		gopher.style.transform = "rotate(90deg)";
	}else if (frameNum != 0){
		gopherTuple = getCurrentGopherList()[trapFrameNum - getTrapWidth()];
		gopher.src = getGopherImageName(gopherTuple); // update gopher image
		gopher.style.transform = "rotate(" + getRotInDegrees(gopherTuple[2]) + "deg)"; // fourth element is rotation. 
	}
	moveGopher(gopherTuple);
}

/** 
 * Moves the gopher to a given cell.
 *	@param Array gopherTuple: array of the form [x, y, rotation, state] that determines location and state of gopher.
 */
function moveGopher(gopherTuple){
	let cell = [gopherTuple[1] + 1, gopherTuple[0] + 1]; // row first then col
	// check if the grid position is valid first!
	if (isValidGridPos(cell))
	{
		$("div.gridDiv:nth-of-type(" + String(getNth(cell)) +")").append(gopher); // prepend so gopher is on top
	}
	else{
		throw new Error("ERROR: Not a vailid grid position.");
	}
}

/** 
 * Removes any existing grid and sets up a new one. 
 * @param Array gridListIn: the new 2-d array to display 
 */
function updateGrid(gridListIn)
{	
	// remove existing grid by deleting all gridElements.
	gridContainer.innerHTML = "";

	// set up number of columns in grid. 
	gridContainer.style.gridTemplateColumns = "repeat(" + String(gridListIn[0].length) + ", 1fr)";

	// set up elements: loop through terrain, adding div element
	for (let row = 0; row < gridListIn.length; row++)
	{
		for (let col = 0; col < gridListIn[0].length; col++)
		{
			// create div element, set its position.
			let div = document.createElement("div");
			div.style.gridColumnStart = col + 1;
			div.style.gridRowStart = row + 1; // add 1 because col, rows in gridlayout start at 1. 
			div.style.gridColumnEnd = col + 2;
			div.style.gridRowEnd = row + 2;
			div.classList.add("gridDiv");

			// NOTE: if setting up terrain ONCE and then just updating specific cells 
				// (i.e where gopher is, then keep this here. Otherwise, set up images each frame.)
			let image = document.createElement("img");
			activeStateList = trapList[trapNum][1][0];
			image.src = getImageName(gridListIn[row][col], "0");// activeStateList[row][col]); // initialize board to its initial state. 
			image.style.transform = "rotate(" + getRotInDegrees(gridListIn[row][col][3]) + "deg)"; // fourth element is rotation. 
			//image.classList.add(".gridImage");
			div.appendChild(image);

			// add to grid Container
			gridContainer.appendChild(div);
		}
	}
}


/** Shows the proper ending screen. */
function showEndingImage()
{
	// simply make a grid with only one element, just like before.
	gridContainer.innerHTML = "";
	gridContainer.style.gridTemplateColumns = "repeat(1, 1fr)"
	let div = document.createElement("div");
	div.style.gridColumnStart = 1;
	div.style.gridRowStart = 1; // add 1 because col, rows in gridlayout start at 1. 
	div.style.gridColumnEnd = 2;
	div.style.gridRowEnd = 2;
	div.classList.add("gridDiv");
	let image = document.createElement("img");

	// We need the endsWith because gopher.src contains entire file path.
	if (gopher.src.endsWith("gopher/gopherdead.png")){
		image.src = "endingscreens/gopherzapped.png";
	}else{
		image.src = "endingscreens/gopherstarved.png";
	}
	div.appendChild(image);
	gridContainer.appendChild(div);
}

/** 
 * Returns a 2d array corresponding to the currently displayed grid. 
 * @return Array gridArr: The currently displayed grid.
 */
function getCurrentlyDisplayedGrid(){
	// if we are not in the middle of changing traps, just return the grid. Otherwise, calc the grid.
	if (!areChangingTraps()){
		return trapList[trapNum][0];
	}
	
	// create an array initialized to all dirt
	let gridArr = makeDirtArray();

	// if moving toward a trap, then show the trap slowly coming into view. Replace
		// the columns of dirt with trap columns.
	if (trapFrameNum < getTrapWidth()){
		// start at first column of trap, replace as many columns as trapFrameNum dictates.
		for (let trapCol = 0; trapCol <= trapFrameNum; trapCol++)
		{
			gridCol = getTrapWidth() - 1 - trapFrameNum + trapCol; // which grid column to replace with this trap column.
			gridArr = replaceCol(gridArr, gridCol, trapCol); 
		}
	}
	// if moving away from a trap, then show trap slowly moving away from view.
	else{
		// trapCol is the first col to show. Goes from 0 to 3. AND show all columns after trapCol.
		let animNum = trapFrameNum - (getTrapWidth() + getCurrentGopherList().length);
		for (let trapCol = animNum; trapCol < getTrapWidth(); trapCol++) 
		{
			gridCol = trapCol - animNum; // grid column to change is dependent upon which stage of animation we are at. Further along we are, the more columns shift to left.
			gridArr = replaceCol(gridArr, gridCol, trapCol);
		}
	}
	return gridArr;
}


/** --------------- Helper methods ----------*/
/** 
 * Returns the number of steps that it takes for the gopher to "walk" to the trap. 
 * @return int the number of steps 
*/
function getNumStartSteps(){
	// number of steps to the door is Math.floor((getTrapWidth() + 1)/2).
	// add one more step so we have one step at beginning with just the trap itself.
	return Math.floor((getTrapWidth() + 1)/2) + 1; 
}

/** 
 * Returns the gopher Image name depending on its tuple. 
 * @param  Array  gopherTuple: the array of the form [x, y, rotation, state] that determines location and state of gopher.
 * @return String the image name to display for the gopher. 
 */
function getGopherImageName(gopherTuple){
	let stateNum = gopherTuple[3];
	let states = ["dead", "alive", "hit"];
	return "gopher/gopher" + states[stateNum] + ".png";
}

/** 
 * Returns a cell name given a cell code.
 * Cell code is the contents of the array that is passed in, eg. 41xx.
 * Note: This is NOT used for gopher images! 
 * @param  String cellCode: 	the string of characters used to determine which cell image to display
 * @param  int    isActiveNum: 	1 if cell is active, 1 if inactive 
 * @return String imgName: 		the string name corresponding to the image to display.
*/
function getImageName(cellCode, isActiveNum){
	let cellType = getCellType(cellCode.charAt(0));
	let thickType = getThickType(cellCode.charAt(2));
	let imgName = cellType + thickType + "/" + cellType + getAngleType(cellCode.charAt(1)) + 
		thickType + getIsActive(isActiveNum) + ".png";
	return imgName;
}

/** 
 * Interprets the char corresponding to cell type.
 * @param  char   cellTypeIn: the character corresponding to a cell type
 * @return String  		      the type of cell to display
 */
function getCellType(cellTypeIn){
	let cellTypes = ["gopher", "door", "wire", "arrow", "dirt", "food", "floor"];
	return cellTypes[parseInt(cellTypeIn)];
}

/** 
 * Interprets the char corresponding to angle type.
 * @param  char angleTypeIn: the character corresponding to an angle type
 * @return String  		   	 the type of angle to display
 */
function getAngleType(angleTypeIn){
	if (angleTypeIn == 'x'){
		return "";
	}
	let angleTypes = ["lacute", "racute", "lright", "rright", "lobtuse", "robtuse", "straight"];
	return angleTypes [parseInt(angleTypeIn)];
}

/** 
 * Interprets the char corresponding to thick type.
 * @param  char thickTypeIn: the character corresponding to an angle type
 * @return String  		   	 the thick type to display
 */
function getThickType(thickTypeIn){
	if (thickTypeIn == 'x'){
		return "";
	}
	let thickTypes = ["skinny", "normal", "wide"]
	return thickTypes[parseInt(thickTypeIn)];
}

/** 
 * Interpret the rotation char. Return the rotation from top in degrees
 * @param  char rotTypeIn: the character corresponding to an angle type
 * @return String  		   the rotation type to display
 */
function getRotInDegrees(rotTypeIn){
	if (rotTypeIn == 'x')
		return 0;
	return 45 * parseInt(rotTypeIn);
}

/** 
 * Return "active" if input is 1, "inactive" otherwise 
 * @param  int isActiveNumIn: the integer corresponding to the active state.
 * @return String 			  "active" if the cell should be active, "inactive" otherwise.
 */
function getIsActive(isActiveNumIn){
	if(isActiveNumIn == 1){
		return "active";
	}
	else if (isActiveNumIn == 0){
		return "inactive";
	}
	throw new Error("ERROR: isActiveNumIn is neither 1 nor 0.");
	return;
}



/** 
 * Replaces the gridCol column in gridArr with the trapCol column in the trap array. 
 * Assumes that gridArr and trap array have the same number of rows. 
 * @param Array gridArr: the grid to change
 * @param int   gridCol: the number of the column to change
 * @param int   trapCol: the number of the column in the trap to replace the gridCol with
 * @return Array         the new grid array
 */
function replaceCol(gridArr, gridCol, trapCol){
	// loop through all rows, change that column.
	for (let row = 0; row < gridArr.length; row++){
		gridArr[row][gridCol] = trapList[trapNum][0][row][trapCol]; // Don't add 0 to make it inactive, this is done in updateGRid()
	}
	return gridArr
}

/** 
 * Returns a 2-d array of all dirt, with same size as the current trap board.
 * @return Array the 2-d array
 */
function makeDirtArray(){
	// create an array initialized to all dirt
	let gridArr = []
	for (let row = 0; row < getTrapHeight(); row++){
		gridArr.push([])
		for (let col = 0; col < getTrapWidth(); col++){
			gridArr[row].push('4xxx');
		}
	}
	return gridArr;
}

/**
 * Returns the width of the current trap.
 * @return int the width, in units of grid cells.
 */
function getTrapWidth(){
	let grid = trapList[trapNum][0]; // first element is the grid
	return grid[0].length;
}

/**
 * Returns the height of the current trap.
 * @return int the height, in units of grid cells.
 */
function getTrapHeight(){
	let grid = trapList[trapNum][0]; // first element is the grid
	return grid.length;
}

/** 
 * Returns a 2d array consisting of all the gopher tuples for this part of the animation. 
 * @return Array 	the current gopher tuples
*/
function getCurrentGopherList(){
	return trapList[trapNum][2]; // third element in each tuple is gopherList
}

/** 
 * Determines if the inputted position is a valid grid position. 
 * @param  Array   gridPos: array of the form [row, col] that represents a grid position
 * @return boolean        	true if valid, false otherwise
 */
function isValidGridPos(gridPos){
	currentlyDisplayedGrid = getCurrentlyDisplayedGrid();
	if (gridPos[0] <= 0 || gridPos[0] <= 0){ // row/column lines start at 1
		return false;
	} else if (gridPos[0] > currentlyDisplayedGrid.length || gridPos[1] > currentlyDisplayedGrid[0].length){ // and end at length
		return false;
	}
	return true;
}

/** Determines if we are currently in the middle of switching from one trap to the next
 * @return boolean 		true if switching traps, false otherwise
 */
function areChangingTraps(){
	return (trapFrameNum < getTrapWidth()) || (trapFrameNum >= getCurrentGopherList().length + getTrapWidth());
}

/** 
 * Calculates the cell number. Upper leftmost cell is #1. Read across rows and move down columns.
 * @param  Array gridPos: array of the form [row, col]. Note that row and col both start at 1, NOT 0. 
 * @return int 			  the cell number of the grid position.
 */
function getNth(gridPos){
 	return (gridPos[0] - 1) * getCurrentlyDisplayedGrid()[0].length + gridPos[1]; // row * total num columns + col
}
