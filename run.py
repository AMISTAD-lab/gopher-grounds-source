
#import simulation as sim
import visualize as vis
import experiment as exp

# runs the animation.
animationData = exp.simulate(exp.pref)[1] # returns list of initial board, active cells, gopher cells
vis.writeTojs(animationData) # write to the js file.