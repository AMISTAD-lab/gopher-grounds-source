#import simulation as sim
import visualize as vis
import legacy.experiment as exp
import os
import webbrowser

# runs the animation.
animationData = exp.simulate(exp.pref)[1] # returns list of initial board, active cells, gopher cells
vis.writeTojs(animationData) # write to the js file.

# opens the animation in the web browser
webbrowser.open_new_tab('file://' + os.path.realpath('./animation/animation.html'))