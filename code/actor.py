import numpy as np

import gameWrapper as gw
import preprocessor as pre


# width weightMatrix = length stateVector + 1
# height weightMatrix = number of output actions
def action(game, weightMatrix):
    gameStateDict = pre.vectorizeState(game)

    action = gw.doEndRound()
    return action
