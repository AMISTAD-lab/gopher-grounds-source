"""
permutation.py is the code that calculates the M_g(x) distribution found in Section A.1 of
The Gopher's Gambit. 

Run using python3; eg. python3 permutation.py
"""

import copy
import numpy as np

TOTAL_VARIABLE_CELLS = 9  # All traps have 9 "variable" cells that can be either floor, wire, or arrow cells.
ratioDict = {}  


def generateDict(n):
	""" Loops through all possible numbers of connections from 0 through n.
	Inputs: 
		n: Number of possible connections (usually 10)"""
	for k in range(0, n + 1):
		choiceList = []
		choiceList = nCkHelp(n, k, choiceList)

def nCkHelp(n, k, choiceList):
	""" Generates a list of k intact connections given n possible cells.
	Inputs:
		n: Number of possible connections (usually 10)
		k: Number of intact connections to choose
		choiceList: The current intact connections that have been chosen."""
	if len(choiceList) == k: # Base case
		numP, numPossibleFloors = findNumPossibilities(n, k, choiceList) 
		storeResult(numP, numPossibleFloors, k)  # Store ratios in dictionary.
	else:  # Recursive case
		if len(choiceList) > 0:  
			lastChoice = choiceList[-1] 
		else:
			lastChoice = -1  # This is -1 so that the loop will start with 0
		choiceList = copy.deepcopy(choiceList)
		for choice in range(lastChoice + 1, n):
			nCkHelp(n, k, choiceList + [choice])	

def storeResult(numP, numPossibleFloors, k):
	""" Calculates and stores the data for one configuration of connections.
	Inputs:
		numP: Number of possibilities NOT taking into account cells with 91 possibilities
		numPossibleFloors: The number of cells with 91 possibilities.
		k: The minimum number of intact connections."""
	global ratioDict

	# Loop through different possible numbers of floor cells. 
	for numFloors in range(0, numPossibleFloors + 1): 
		# There are 90 ways to get a non-floor cell. 
		factor91 = 90 ** (numPossibleFloors - numFloors) 
		# Find number of ways to get this number of floors. Use nCk.
		numWays = int(np.math.factorial(numPossibleFloors)/(np.math.factorial(numFloors) * np.math.factorial(numPossibleFloors - numFloors)))
		# Updated number to add to dictionary.
		numToAdd = numP * factor91 * numWays

		# Determine the ratio tuple: (# minimum connections, # nonblank tiles).
		nonblankTiles = TOTAL_VARIABLE_CELLS - numFloors
		ratioTuple = (k, nonblankTiles)
		# Add tuple and value to dictionary if it is not yet there, otherwise
 			# simply add to the existing value.
		if ratioTuple not in ratioDict:
			ratioDict[ratioTuple] = numToAdd
		else:
			ratioDict[ratioTuple] = ratioDict[ratioTuple] + numToAdd

def simplifyRatioTuple(num, denom):
	""" Simplifies the tuple, which represents the numerator and denominator of a fraction.
	Inputs: 
		num: The numerator
		denom: The denominator 
	Return:
		(num, denom): The simplified ratio tuple """
	# Group anything with numerator 0 into the (0, 1) category
	if num == 0:
		return (0.0, 1.0)
	elif num != 0 and denom == 0:
		raise Exception("ERROR: All cells are floor cells, but connections were found.")

	gcd = int(np.gcd(num, denom))
	num = num/gcd
	denom = denom/gcd
	return (num, denom) 


def findNumPossibilities(n, k, choiceList):
	""" Counts the number of each cell type (eg. 1, 9, 91), as well as the number of groups. 
	Also calculates the part of total number that has to do with cells of type 1, 9, and number of groups (thickness types).
	Does not include part for the cells that have 91 possibilities. 
	Inputs:
		n: Number of possible connections (usually 10)
		k: Number of intact connections to choose
		choiceList: The current intact connections that have been chosen.
	Return:
		numP, numPossibleFloors: 
		numP is the total number of ways to acheive configuration without taking into account cells assigned the number 91.
		numPossibleFloors is the number of cells assigned the number 91.
		"""
	numPossibleFloors = 0
	cellPossibilities = []
	connections = [i in choiceList for i in range(n)]
	for i in range(n-1):
		leftConnection = connections[i]
		rightConnection = connections[i+1]

		if leftConnection and rightConnection:
			cellPossibilities.append(1)
		elif leftConnection or rightConnection:
			cellPossibilities.append(9)
		else:
			numPossibleFloors += 1
	# Initialize number of groups appropriately. There is one group if there is at least one intact connection.
	if len(choiceList) > 0:  
		numGroups = 1
	else:
		numGroups = 0
	# Count the number of groups. Incremement whenever we find non-adjacent connections.
	for i in range(1, len(choiceList)):
		if choiceList[i] - choiceList[i-1] > 1:
			numGroups += 1
	# Calculate the number of possible ways to acheive this configuration.
	numP = 1
	for p in cellPossibilities:
		numP *= p
	numP *= (3**numGroups)
	return numP, numPossibleFloors

def printDict(dictIn):
	"""Prints out a dictionary where the keys are decimals. 
	Formats decimals to three decimal places. 
	Input:
		dictIn: The dictionary to print."""
	for key in dictIn:
		print("%.3f" % key, ":", dictIn[key])

def printRatioDict(dictIn):
	"""Prints out a dictionary explicitly with each line as "key:value"
	Input:
		dictIn: The dictionary to print."""
	for key in dictIn:
		print(key, ":", dictIn[key])

def simplifyAllTuples(dictIn):
	""" Consolodates equivalent tuples by simplifying fractions. 
		eg. the values for the keys (1, 2), (2, 4), (3, 6), etc. will all be added together
		and put in the key (1, 2).
	Inputs:
		dictIn: The dictionary. Should have keys that are unsimplified ratio tuples.
	Return: 
		newDict: A new version of the dictionary with simplified ratio keys. """
	newDict = {}
	for key in dictIn:
		newKey = simplifyRatioTuple(key[0], key[1])
		if newKey in newDict:
			newDict[newKey] = newDict[newKey] + dictIn[key]
		else:
			newDict[newKey] = dictIn[key]
	return newDict

def getDecimalDict(dictIn):
	""" Turns the keys from fraction tuples into decimals.
	Inputs:
		dictIn: The dictionary whose keys will be converted to decimals. 
		Should have keys that are simplified ratio tuples
	Return:
		decimalDict: A copy of the original dictionary with keys converted to decimals"""
	decimalDict = {}
	for key in dictIn:
		if (key[1] == 0):
			newKey = 0.0
		else:	
			newKey = float(key[0]/(key[1] + 0.0))
		decimalDict[newKey] = dictIn[key]
	return decimalDict

def sortAndPrintDict(dictIn):
	""" Sorts the dictionary by key from lowest to highest, prints out its values
	Inputs: 
	 	dictIn: The dictionary to sort and print. Should already be in decimal (as opposed to ratio) form."""
	keys = list(dictIn.keys())
	keys.sort()
	for index in range(0, len(keys)):
		key = keys[index]
		if index != len(keys) - 1:
			print("%.3f" % key, ":", dictIn[key])
		else:
			print("%.3f" % key, ":", dictIn[key])
		

def getExactNums(dictIn):
	""" Determines the exact number of configurations with exactly a given number of connections and 
	exactly a given number of nonempty cells.
	Does so by subtracting the ratio with one more connection/the same number of nonempty cells
	Inputs: 
		dictIn: The dictionary. Should have keys that are unsimplified ratio tuples.
	Return:
		dictIn: The same dictionary, but with new values."""
	for key in dictIn:
		keyToFind = (key[0] + 1, key[1])
		if keyToFind in dictIn:
			dictIn[key] = dictIn[key] - dictIn[keyToFind]
	return dictIn

def getCumulativeNums(dictIn):
	""" Modify values of dictionary to include all the configurations with at least the given 
	ratio of connections/nonempty cells, instead of exactly the given ratio of connections/nonempty cells.
	Inputs: 
		dictIn: The dictionary. Must be in decimal form already.
	Return: 
		dictIn: The new dictionary, but with cumulative values"""
	keys = list(dictIn.keys())
	keys.sort()
	# Loop through keys backward, so we only have to add the value of the key with index one greater than this key.
	# subtract 1 because there is nothing to add for the largest ratio.
	for reverseIndex in reversed(range(0, len(keys) - 1)):
		dictIn[keys[reverseIndex]] = dictIn[keys[reverseIndex]] + dictIn[keys[reverseIndex + 1]]
	return dictIn


generateDict(10)  # Populates ratioDict with keys: (at least c connections, exactly t nonemtpy cells), and values: number of configurations
exactNumDict = getExactNums(ratioDict)  # Returns dictionary with keys: (exactly c connections, exactly t nonempty cells), values: number of configurations.
simplifiedRatioDict = simplifyAllTuples(exactNumDict)  # Simplifies the keys to their simplified ratios of (exactly c connections, exactly t nonempty cells)
decimalDict = getDecimalDict(simplifiedRatioDict)  # Turns all keys into floats
cumulativeNumDict = getCumulativeNums(decimalDict)  # Calculates the cumulative numbers (i.e. the Mg(x) distribution)
sortAndPrintDict(decimalDict)  # Prints out the dictionary after sorting by key.
