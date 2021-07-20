import libs.algorithms as alg

#DEFAULTS#
WIDE_PROJECTILE_STRENGTH = 0.45 #thick wire
NORMAL_PROJECTILE_STRENGTH = WIDE_PROJECTILE_STRENGTH * (2/3) #.3, normal wire
SKINNY_PROJECTILE_STRENGTH = WIDE_PROJECTILE_STRENGTH * (1/3) #.15, thin wire
DECISION_ALG = alg.isTrap

DEFAULT_PROB_ENTER = 0.8 #probability of gopher entering trap (not intention)
PROB_REAL = 0
