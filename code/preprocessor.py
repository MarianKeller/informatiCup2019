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

    return worstPathogen, highestInfectivity


def getHighestPathogenMobility(game: GameWrapper, city):
    pathogens = game.getPathogensCity(city)
    worstPathogen = None
    highestMobility = 0

    for pathogen in pathogens:
        curMobility = game.getPathogenMobility(pathogen)
        if curMobility > highestMobility:
            worstPathogen = pathogen
            highestMobility = curMobility

    return worstPathogen, highestMobility


def getHighestPathogenDuration(game: GameWrapper, city):
    pathogens = game.getPathogensCity(city)
    worstPathogen = None
    highestDuration = 0

    for pathogen in pathogens:
        curDuration = game.getPathogenDuration(pathogen)
        if curDuration > highestDuration:
            worstPathogen = pathogen
            highestDuration = curDuration

    return worstPathogen, highestDuration


def getHighestPathogenLethality(game: GameWrapper, city):
    pathogens = game.getPathogensCity(city)
    worstPathogen = None
    highestLethality = 0

    for pathogen in pathogens:
        curLethality = game.getPathogenLethality(pathogen)
        if curLethality > highestLethality:
            worstPathogen = pathogen
            highestLethality = curLethality

    return worstPathogen, highestLethality


def getHighestPathogenPrevalence(game: GameWrapper, city):
    pathogens = game.getPathogensCity(city)
    worstPathogen = None
    highestPrevalence = 0.0

    for pathogen in pathogens:
        curPrevalence = game.getPathogenPrevalenceCity(pathogen, city)
        if curPrevalence > highestPrevalence:
            worstPathogen = pathogen
            highestPrevalence = curPrevalence

    return worstPathogen, highestPrevalence


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

    return worstConnection, maxVictims


# TODO normalize inputs (helps to reduce search space)


inputVectorSize = 26  # update when necessary


def vectorizeState(game: GameWrapper):
    rounds = game.getRound()
    points = game.getPoints()
    cities = game.getCities()
    pathogenPrevalencesGlobal = getPathogenPrevalencesGlobal(game)

    for city in cities:
        for pathogen in game.getPathogensCity(city):
            stateList = []
            latitude = game.getLatitude(city)
            stateVec = np.array([
                # independent of city
                rounds,
                points,

                # dependent on city, non-indicator
                game.getPopulation(city),
                game.getEconomy(city),
                game.getEconomy(city),
                game.getHygiene(city),
                game.getAwareness(city),

                # dependent on pathogen, non-indicator
                game.getPathogenInfectivity(pathogen),
                game.getPathogenMobility(pathogen),
                game.getPathogenDuration(pathogen),
                game.getPathogenLethality(pathogen),

                # dependent on pathogen and city, non-indicator
                game.getPathogenPrevalenceCity(pathogen, city),

                # dependent on city, indicator
                climateZoneIsTropical(latitude),
                climateZoneIsSubTropical(latitude),
                climateZoneIsModerate(latitude),
                climateZoneIsArctic(latitude),
                getConnectivity(game, city),
                getHighestPathogenInfectivity(game, city)[1],
                getHighestPathogenMobility(game, city)[1],
                getHighestPathogenLethality(game, city)[1],
                round(getHighestPathogenPrevalence(game, city)[1], 4),

                # dependent on pathogen, indicator
                pathogenPrevalencesGlobal[pathogen],
                int(game.hasVaccineBeenDeveloped(pathogen)),
                int(game.hasMedicationBeenDeveloped(pathogen)),

                # dependent on pathogen and city, indicator
                getMaxConnectedVictims(game, city, pathogen)[1],

                # TODO missing indicator values
                # TODO add indicator for maximum number of reachable victims (to close airport)

                # bias
                1
            ])

            yield city, pathogen, stateVec
