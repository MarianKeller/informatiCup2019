import numpy as np

from gameWrapper import GameWrapper


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
    connections = game.getConnections(city)
    connectivity = 0
    for connection in connections:
        connectivity += game.getPopulation(connection)
    return connectivity


def getHighestPathogenInfectivity(game: GameWrapper, city):
    pathogens = game.getPathogensCity(city)
    worstPathogen = None
    highestInfectivity = 0

    for pathogen in pathogens:
        curInfectivity = game.getPathogenInfectivity(pathogen)
        if curInfectivity > highestInfectivity:
            worstPathogen = pathogen
            highestInfectivity = curInfectivity

    return (worstPathogen, highestInfectivity)


def getHighestPathogenMobility(game: GameWrapper, city):
    pathogens = game.getPathogensCity(city)
    worstPathogen = None
    highestMobility = 0

    for pathogen in pathogens:
        curMobility = game.getPathogenMobility(pathogen)
        if curMobility > highestMobility:
            worstPathogen = pathogen
            highestMobility = curMobility

    return (worstPathogen, highestMobility)


def getHighestPathogenDuration(game: GameWrapper, city):
    pathogens = game.getPathogensCity(city)
    worstPathogen = None
    highestDuration = 0

    for pathogen in pathogens:
        curDuration = game.getPathogenDuration(pathogen)
        if curDuration > highestDuration:
            worstPathogen = pathogen
            highestDuration = curDuration

    return (worstPathogen, highestDuration)


def getHighestPathogenLethality(game: GameWrapper, city):
    pathogens = game.getPathogensCity(city)
    worstPathogen = None
    highestLethality = 0

    for pathogen in pathogens:
        curLethality = game.getPathogenLethality(pathogen)
        if curLethality > highestLethality:
            worstPathogen = pathogen
            highestLethality = curLethality

    return (worstPathogen, highestLethality)


def getHighestPathogenPrevalence(game: GameWrapper, city):
    pathogens = game.getPathogensCity(city)
    worstPathogen = None
    highestPrevalence = 0.0

    for pathogen in pathogens:
        curPrevalence = game.getPathogenPrevalenceCity(pathogen, city)
        if curPrevalence > highestPrevalence:
            worstPathogen = pathogen
            highestPrevalence = curPrevalence

    return (worstPathogen, highestPrevalence)


def getWorldPopulation(game: GameWrapper):
    worldPopulation = 0
    for city in game.getCities():
        worldPopulation += game.getPopulation(city)
    return worldPopulation


def getPathogenPrevalencesGlobal(game: GameWrapper):
    worldPopulation = getWorldPopulation(game)

    globalPrevalence = {}
    for pathogen in game.getPathogensGlobal():
        globalPrevalence[pathogen] = 0.0

    for city in game.getCities():
        for pathogen in game.getPathogensCity(city):
            globalPrevalence[pathogen] += game.getPathogenPrevalenceCity(
                pathogen, city) * game.getPopulation(city)/worldPopulation
    
    return globalPrevalence


def getMaxConnectedVictims(game: GameWrapper, city, pathogen):
    worstConnection = None
    maxVictims = 0

    # TODO if connection is closed, will city appear as valid choice?
    connections = game.getConnections(city)
    for connection in connections:
        pathogens = game.getPathogensCity(connection)
        population = game.getPopulation(connection)
        if pathogen in pathogens and population > maxVictims:
            worstConnection = connection
            maxVictims = population

    return (worstConnection, maxVictims)


# TODO normalize inputs (helps to reduce search space)


inputVectorSize = 26  # update when necessary


def vectorizeState(game: GameWrapper):
    rounds = game.getRound()
    points = game.getPoints()
    cities = game.getCities()
    pathogenPrevalencesGlobal = getPathogenPrevalencesGlobal(game)

    gameStateDict = {}
    for city in cities:
        for pathogen in game.getPathogensCity(city):
            stateList = []

            # independent of city
            stateList.append(rounds)
            stateList.append(points)

            # dependent on city, non-indicator
            stateList.append(game.getPopulation(city))
            stateList.append(game.getEconomy(city))
            stateList.append(game.getGovernment(city))
            stateList.append(game.getHygiene(city))
            stateList.append(game.getAwareness(city))

            # dependent on pathogen, non-indicator
            stateList.append(game.getPathogenInfectivity(pathogen))
            stateList.append(game.getPathogenMobility(pathogen))
            stateList.append(game.getPathogenDuration(pathogen))
            stateList.append(game.getPathogenLethality(pathogen))

            # dependent on pathogen and city, non-indicator
            stateList.append(game.getPathogenPrevalenceCity(pathogen, city))

            # dependent on city, indicator
            latitude = game.getLatitude(city)
            stateList.append(climateZoneIsTropical(latitude))
            stateList.append(climateZoneIsSubTropical(latitude))
            stateList.append(climateZoneIsModerate(latitude))
            stateList.append(climateZoneIsArctic(latitude))

            stateList.append(getConnectivity(game, city))
            stateList.append(getHighestPathogenInfectivity(game, city)[1])
            stateList.append(getHighestPathogenMobility(game, city)[1])
            stateList.append(getHighestPathogenLethality(game, city)[1])
            stateList.append(
                round(getHighestPathogenPrevalence(game, city)[1], 4))

            # dependent on pathogen, indicator
            stateList.append(pathogenPrevalencesGlobal[pathogen])
            stateList.append(int(game.hasVaccineBeenDeveloped(pathogen)))
            stateList.append(int(game.hasMedicationBeenDeveloped(pathogen)))

            # dependent on pathogen and city, indicator
            stateList.append(getMaxConnectedVictims(game, city, pathogen)[1])

            # TODO missing indicator values
            # TODO add indicator for maximum number of reachable victims (to close airport)

            stateList.append(1)  # bias
            stateVec = np.array(stateList)
            gameStateDict[city, pathogen] = stateVec

    return gameStateDict
