import libs.algorithms as alg
import scExperiment as sc
import geneticAlgorithm.encoding as encode
import goodTuring as gt

#DEFAULTS#
WIDE_PROJECTILE_STRENGTH = 0.45 #thick wire
NORMAL_PROJECTILE_STRENGTH = WIDE_PROJECTILE_STRENGTH * (2/3) #.3, normal wire
SKINNY_PROJECTILE_STRENGTH = WIDE_PROJECTILE_STRENGTH * (1/3) #.15, thin wire
DECISION_ALG = alg.isTrap

DEFAULT_PROB_ENTER = 0.8 #probability of gopher entering trap (not intention)
PROB_REAL = 0

def initializeVariables(pref):

    global PROB_REAL
    PROB_REAL = pref["probReal"]

    global DECISION_ALG
    if pref["cautious"]:
        DECISION_ALG = lambda trap: alg.cautious(trap, PROB_REAL)
    else:
        DECISION_ALG = alg.isTrap
    
    global DEFAULT_PROB_ENTER
    DEFAULT_PROB_ENTER = pref["defaultProbEnter"]

    global WIDE_PROJECTILE_STRENGTH
    WIDE_PROJECTILE_STRENGTH = pref["maxProjectileStrength"]

    global NORMAL_PROJECTILE_STRENGTH
    NORMAL_PROJECTILE_STRENGTH = WIDE_PROJECTILE_STRENGTH * (2/3)

    global SKINNY_PROJECTILE_STRENGTH
    SKINNY_PROJECTILE_STRENGTH = WIDE_PROJECTILE_STRENGTH * (1/3)


def initializeVariablesNew(pref, fitnessFunc):
    global PROB_REAL
    PROB_REAL = pref["probReal"]

    global DECISION_ALG
    if pref["intention"]==2:
        DECISION_ALG = lambda trap: sc.newIsTrap(encode.singleEncoding(trap.board), trap, fitnessFunc)
    else:
        DECISION_ALG = alg.isTrap
    
    global DEFAULT_PROB_ENTER
    DEFAULT_PROB_ENTER = pref["defaultProbEnter"]

    global WIDE_PROJECTILE_STRENGTH
    WIDE_PROJECTILE_STRENGTH = pref["maxProjectileStrength"]

    global NORMAL_PROJECTILE_STRENGTH
    NORMAL_PROJECTILE_STRENGTH = WIDE_PROJECTILE_STRENGTH * (2/3)

    global SKINNY_PROJECTILE_STRENGTH
    SKINNY_PROJECTILE_STRENGTH = WIDE_PROJECTILE_STRENGTH * (1/3)


def newIsTrap(encodedTrap, trap, fitnessFunc, sigVal=13.29):
    """given a trap and a significant value, determines whether the trap is coherent enough to be considered designed based on the real distribution"""
    p = gt.getSmoothedProb(encodedTrap, fitnessFunc)
    connectionTuple = alg.connectionsPerPiece(trap)
    return alg.functional_specified_complexity(connectionTuple, p) >= sigVal
