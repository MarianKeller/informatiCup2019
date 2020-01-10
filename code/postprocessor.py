import numpy as np

import preprocessor as pre
from gameWrapper import GameWrapper as gw

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

# don't forget to update when a change in possibleActions is made
endRoundPos = 0
putUnderQuarantinePos = 1
closeAirportPos = 2
closeConnectionPos = 3
developVaccinePos = 4
deployVaccinePos = 5
developMedicationPos = 6
deployMedicationPos = 7
exertInfluencePos = 8
callElectionsPos = 9
applyHygienicMeasuresPos = 10
launchCampaignPos = 11

numActionsWithRoundParameter = 3
numPossibleActions = len(possibleActions)

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

# set doManualOptimizations = False during training, could mislead genetic algorithm
def action(game: gw, weightMat, roundsMat, doManualOptimizations):
    budget = game.getPoints()

    weightedActions = []
    for city, pathogen, inputStateVec in pre.vectorizeState(game):
        actionWeightVec = np.dot(weightMat, inputStateVec)
        numberRoundsVec = np.dot(roundsMat, inputStateVec)

        roundsQuarantine = int(round(numberRoundsVec[0]))
        roundsCloseAirport = int(round(numberRoundsVec[1]))
        roundsCloseConnection = int(round(numberRoundsVec[2]))

        connectionToClose = pre.getMaxConnectedVictims(game, city, pathogen)[0]

        # manually set weights for impossible actions
        if connectionToClose is None:
            actionWeightVec[closeConnectionPos] = float("-inf")

        if doManualOptimizations:
            if game.isVaccineInDevelopment(pathogen) or game.isVaccineAvailable(pathogen):
                actionWeightVec[developVaccinePos] = float("-inf")
            else:
                actionWeightVec[deployVaccinePos] = float("-inf")

            if game.isMedicationInDevelopment(pathogen) or game.isMedicationAvailable(pathogen):
                actionWeightVec[developMedicationPos] = float("-inf")
            else:
                actionWeightVec[deployMedicationPos] = float("-inf")

            if game.getEconomy(city) == 5:
                actionWeightVec[exertInfluencePos] = float("-inf")

            if game.getGovernment(city) == 5:
                actionWeightVec[callElectionsPos] = float("-inf")

            if game.getHygiene(city) == 5:
                actionWeightVec[applyHygienicMeasuresPos] = float("-inf")

            if game.getAwareness(city) == 5:
                actionWeightVec[launchCampaignPos] = float("-inf")

        for i in range(len(actionWeightVec)):
            weight = actionWeightVec[i]
            action = possibleActions[i](
                city, pathogen, roundsQuarantine, roundsCloseAirport, roundsCloseConnection, connectionToClose)
            cost = actionCosts[i](
                roundsQuarantine, roundsCloseAirport, roundsCloseConnection)
            weightedActions.append((weight, action, cost))

        # first sort by cost non-descendingly to prefer cheaper action in case of same weight
        weightedActions.sort(key=lambda x: x[2])
        sortedActions = [action[1:] for action in sorted(
            weightedActions, key=lambda x: x[0], reverse=True)]

        for (action, cost) in sortedActions:
            if cost <= budget:
                return action

    return gw.doEndRound()
