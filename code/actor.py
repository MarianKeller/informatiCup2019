import numpy as np

import gameWrapper as gw
import preprocessor as pre

possibleActions = [
    lambda city, pathogen, roundsQuar, roundsAir, toCity, roundsCon: gw.doEndRound(),
    lambda city, pathogen, roundsQuar, roundsAir, toCity, roundsCon: gw.doPutUnderQuarantine(
        city, roundsQuar),
    lambda city, pathogen, roundsQuar, roundsAir, roundsCon, toCity: gw.doCloseAirport(
        city, roundsAir),
    lambda city, pathogen, roundsQuar, roundsAir, roundsCon, toCity: gw.doCloseConnection(
        city, toCity, roundsCon),
    lambda city, pathogen, roundsQuar, roundsAir, roundsCon, toCity: gw.doDevelopVaccine(
        pathogen),
    lambda city, pathogen, roundsQuar, roundsAir, rounroundsCondsClose, toCity: gw.doDeployVaccine(
        pathogen, city),
    lambda city, pathogen, roundsQuar, roundsAir, roundsCon, toCity: gw.doDevelopMedication(
        pathogen),
    lambda city, pathogen, roundsQuar, roundsAir, roundsCon, toCity: gw.doDeployMedication(
        pathogen, city),
    lambda city, pathogen, roundsQuar, roundsAir, roundsCon, toCity: gw.doExertInfluence(
        city),
    lambda city, pathogen, roundsQuar, roundsAir, roundsCon, toCity: gw.doCallElections(
        city),
    lambda city, pathogen, roundsQuar, roundsAir, roundsCon, toCity: gw.doApplyHygienicMeasures(
        city),
    lambda city, pathogen, roundsQuar, roundsAir, roundsCon, toCity: gw.doLaunchCampaign(
        city)
]

actionCosts = [
    lambda roundsQuar, roundsAir, roundsCon: gw.costEndRound(),
    lambda roundsQuar, roundsAir, roundsCon: gw.costPutUnderQuarantine(
        roundsQuar),
    lambda roundsQuar, roundsAir, roundsCon: gw.costCloseAirport(roundsAir),
    lambda roundsQuar, roundsAir, roundsCon: gw.costCloseConnection(roundsCon),
    lambda roundsQuar, roundsAir, roundsCon: gw.costDevelopVaccine(),
    lambda roundsQuar, roundsAir, roundsCon: gw.costDeployVaccine(),
    lambda roundsQuar, roundsAir, roundsCon: gw.costDevelopMedication(),
    lambda roundsQuar, roundsAir, roundsCon: gw.costDeployMedication(),
    lambda roundsQuar, roundsAir, roundsCon: gw.costExertInfluence(),
    lambda roundsQuar, roundsAir, roundsCon: gw.costCallElections(),
    lambda roundsQuar, roundsAir, roundsCon: gw.costApplyHygienicMeasures(),
    lambda roundsQuar, roundsAir, roundsCon: gw.costLaunchCampaign()
]


# width weightMat = length stateVec
# height weightMat = length possibleActions
# width roundsMat = length stateVec
# height roundsMat = 3
# all of the above are optimized by the genetic algorithm
def action(game, weightMat, roundsMat):
    gameStateDict = pre.vectorizeState(game)
    budget = gw.getPoints(game)

    weightedActions = []
    for city, pathogen in gameStateDict.keys():
        inputStateVec = gameStateDict[city, pathogen]
        actionWeightVec = np.dot(inputStateVec, weightMat)
        numberRoundsVec = np.dot(inputStateVec, roundsMat)

        roundsQuarantine = numberRoundsVec[0]
        roundsCloseAirport = numberRoundsVec[1]
        roundsCloseConnection = numberRoundsVec[2]

        connectionToClose = pre.getMaxConnectedVictims(game, city, pathogen)

        for i in range(len(actionWeightVec)):
            weight = actionWeightVec[i]
            action = possibleActions[i](
                city, pathogen, roundsQuarantine, roundsCloseAirport, roundsCloseConnection, connectionToClose)
            cost = actionCosts[i](
                roundsQuarantine, roundsCloseAirport, roundsCloseConnection)
            weightedActions.append(weight, action, cost)

        sortedActions = [action for action in sorted(
            weightedActions, reverse=True)[1:2]]

        for (action, cost) in sortedActions:
            if cost <= budget:
                return action
