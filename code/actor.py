import gameWrapper as gw
import preprocessing as pre


def action(game, recommendationVector):
    gameStateMatrix = pre.vectorizeState(game)
    for i in range(len(gameStateMatrix)):
        cityStateVector = gameStateMatrix[i]
        print("city:", gw.getCities(game)[i] + ",\t\tvector:", cityStateVector)

    action = gw.doEndRound()
    return action
