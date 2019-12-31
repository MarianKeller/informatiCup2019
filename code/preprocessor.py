import math

import gameWrapper as gw
import numpy as np


def climateZoneIsTropical(latitude):
    absoluteLatitude = abs(latitude)
    return int(absoluteLatitude >= 0 and absoluteLatitude <= 23.5)


def climateZoneIsSubTropical(latitude):
    absoluteLatitude = abs(latitude)
    return int(absoluteLatitude > 23.5 and absoluteLatitude <= 40)


def climateZoneIsModerate(latitude):
    absoluteLatitude = abs(latitude)
    return int(absoluteLatitude > 40 and absoluteLatitude <= 60)


def climateZoneIsArctic(latitude):
    absoluteLatitude = abs(latitude)
    return int(absoluteLatitude > 60 and absoluteLatitude <= 90)


def getConnectivity(game, city):
    """Population sum of destination cities"""
    connections = gw.getConnections(game, city)
    connectivity = 0
    for connection in connections:
        connectivity = connectivity + gw.getPopulation(game, connection)
    return connectivity


def getHighestPathogenInfectivity(game, city):
    pathogens = gw.getPathogens(game, city)
    worstPathogen = None
    highestInfectivity = 0
    for pathogen in pathogens:
        curInfectivity = gw.getPathogenInfectivity(game, pathogen)
        if curInfectivity > highestInfectivity:
            worstPathogen = pathogen
            highestInfectivity = curInfectivity
    return (worstPathogen, highestInfectivity)


def getHighestPathogenMobility(game, city):
    pathogens = gw.getPathogens(game, city)
    worstPathogen = None
    highestMobility = 0
    for pathogen in pathogens:
        curMobility = gw.getPathogenMobility(game, pathogen)
        if curMobility > highestMobility:
            worstPathogen = pathogen
            highestMobility = curMobility
    return (worstPathogen, highestMobility)


def getHighestPathogenDuration(game, city):
    pathogens = gw.getPathogens(game, city)
    worstPathogen = None
    highestDuration = 0
    for pathogen in pathogens:
        curDuration = gw.getPathogenDuration(game, pathogen)
        if curDuration > highestDuration:
            worstPathogen = pathogen
            highestDuration = curDuration
    return (worstPathogen, highestDuration)


def getHighestPathogenLethality(game, city):
    pathogens = gw.getPathogens(game, city)
    worstPathogen = None
    highestLethality = 0
    for pathogen in pathogens:
        curLethality = gw.getPathogenLethality(game, pathogen)
        if curLethality > highestLethality:
            worstPathogen = pathogen
            highestLethality = curLethality
    return (worstPathogen, highestLethality)


def getHighestPathogenPrevalence(game, city):
    pathogens = gw.getPathogens(game, city)
    worstPathogen = None
    highestPrevalence = 0.0
    for pathogen in pathogens:
        curPrevalence = gw.getPathogenPrevalenceCity(game, city, pathogen)
        if curPrevalence > highestPrevalence:
            worstPathogen = pathogen
            highestPrevalence = curPrevalence
    return (worstPathogen, highestPrevalence)


def vectorizeState(game):
    rounds = gw.getRound(game)
    points = gw.getPoints(game)
    cities = gw.getCities(game)

    gameStateDict = {}
    for city in cities:
        for pathogen in gw.getPathogens(game, city):
            stateList = []

            # independent of city
            stateList.append(rounds)
            stateList.append(points)

            # dependent on city, non-indicator
            stateList.append(gw.getPopulation(game, city))
            stateList.append(gw.getEconomy(game, city))
            stateList.append(gw.getGovernment(game, city))
            stateList.append(gw.getHygiene(game, city))
            stateList.append(gw.getAwareness(game, city))

            # dependent on pathogen, non-indicator
            stateList.append(
                gw.getPathogenInfectivity(game, pathogen))
            stateList.append(gw.getPathogenMobility(game, pathogen))
            stateList.append(gw.getPathogenDuration(game, pathogen))
            stateList.append(gw.getPathogenLethality(game, pathogen))
            stateList.append(gw.getPathogenPrevalenceWorld(game, pathogen))

            # dependent on pathogen and city, non-indicator
            stateList.append(
                gw.getPathogenPrevalenceCity(game, city, pathogen))

            # dependent on city, indicator
            latitude = gw.getLatitude(game, city)
            stateList.append(climateZoneIsTropical(latitude))
            stateList.append(climateZoneIsSubTropical(latitude))
            stateList.append(climateZoneIsModerate(latitude))
            stateList.append(climateZoneIsArctic(latitude))

            stateList.append(getConnectivity(game, city))
            stateList.append(
                getHighestPathogenInfectivity(game, city)[1])
            stateList.append(
                getHighestPathogenMobility(game, city)[1])
            stateList.append(
                getHighestPathogenLethality(game, city)[1])
            stateList.append(
                round(getHighestPathogenPrevalence(game, city)[1], 4))

            # TODO missing indicator values

            stateVec = np.array[stateList]
            gameStateDict[city, pathogen] = stateVec

    return gameStateDict
