import preprocessing as pre
import gameWrapper as gw


def action(game):
    gameStateMatrix = pre.vectorizeState(game)
    for i in range(len(gameStateMatrix)):
        cityStateVector = gameStateMatrix[i]
        print("city:", gw.getCities(game)[i] + ",\t\tvector:", cityStateVector)

    action = gw.doEndRound()
    return action
