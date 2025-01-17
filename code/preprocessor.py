import math

import numpy as np

from gameWrapper import GameWrapper

# every city has at least one inhabitant
minCityPopulation = 1
maxCityPopulation = 37555

maxWorldPopulation = 756371
minWorldPopulation = math.ceil(maxWorldPopulation/2)

minRounds = 1
maxRounds = 1000

# start with 40 points in round 1, get 20 each following round, can't spend last round
minPoints = 0
maxPoints = 40 + (maxRounds - 2) * 20

minAttribute = 1
maxAttribute = 5


def normalize(value, minimum, maximum):
    """min-max normalization"""
    if value < minimum:
        value = minimum
    if value > maximum:
        value = maximum
    return (value - minimum)/(maximum - minimum)


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


def getPathogenPrevalencesGlobal(game: GameWrapper, worldPopulation):
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

    connections = game.getConnections(city)
    for connection in connections:
        pathogens = game.getPathogensCity(connection)
        population = game.getPopulation(connection)
        if pathogen in pathogens and population > maxVictims:
            worstConnection = connection
            maxVictims = population

    return worstConnection, maxVictims


# update when necessary; also don't forget to normalize any added values to interval [0; 1]
inputVectorSize = 42


def getStateVec(game, city, pathogen, isInfected, pointsNormalized, worldPopulationNormalized, pathogenPrevalencesGlobal):
    latitude = game.getLatitude(city)
    return np.array([
        int(isInfected),

        # independent of city
        pointsNormalized,

        # dependent on city, non-indicator
        normalize(game.getPopulation(city),
                  minCityPopulation, maxCityPopulation),
        normalize(game.getEconomy(city), minAttribute, maxAttribute),
        normalize(game.getGovernment(city),
                  minAttribute, maxAttribute),
        normalize(game.getHygiene(city), minAttribute, maxAttribute),
        normalize(game.getAwareness(city), minAttribute, maxAttribute),
        int(game.isOutbreak(city)),
        int(game.isElectionsCalled(city)),
        int(game.isAntiVaccinationism(city)),
        int(game.isQuarantine(city)),
        int(game.isInfluenceExerted(city)),
        int(game.isCampaignLaunched(city)),
        int(game.isAirportClosed(city)),
        int(game.isHygienicMeasuresApplied(city)),
        int(game.isBioTerrorism(city)),
        int(game.isUprising(city)),

        # dependent on pathogen, non-indicator
        normalize(game.getPathogenInfectivity(
            pathogen), minAttribute, maxAttribute) if isInfected else 0,
        normalize(game.getPathogenMobility(pathogen),
                  minAttribute, maxAttribute) if isInfected else 0,
        normalize(game.getPathogenDuration(pathogen),
                  minAttribute, maxAttribute) if isInfected else 0,
        normalize(game.getPathogenLethality(
            pathogen), minAttribute, maxAttribute) if isInfected else 0,
        normalize(game.getPathogenAge(pathogen),
                  minAttribute, maxAttribute) if isInfected else 0,

        # dependent on pathogen and city, non-indicator
        game.getPathogenPrevalenceCity(pathogen, city) if isInfected else 0,

        # independent of pathogen and city, indicator
        worldPopulationNormalized,

        # dependent on city, indicator
        climateZoneIsTropical(latitude),
        climateZoneIsSubTropical(latitude),
        climateZoneIsModerate(latitude),
        climateZoneIsArctic(latitude),
        normalize(getConnectivity(game, city), 0, maxWorldPopulation),
        normalize(getHighestPathogenInfectivity(
            game, city)[1], minAttribute, maxAttribute),
        normalize(getHighestPathogenMobility(game, city)
                  [1], minAttribute, maxAttribute),
        normalize(getHighestPathogenLethality(game, city)
                  [1], minAttribute, maxAttribute),
        normalize(getHighestPathogenPrevalence(game, city)
                  [1], minAttribute, maxAttribute),

        # dependent on pathogen, indicator
        pathogenPrevalencesGlobal[pathogen] if isInfected else 0,
        int(game.isVaccineInDevelopment(pathogen)) if isInfected else 0,
        int(game.isVaccineAvailable(pathogen)) if isInfected else 0,
        int(game.isMedicationInDevelopment(pathogen)) if isInfected else 0,
        int(game.isMedicationAvailable(pathogen)) if isInfected else 0,
        int(game.isLargeScalePanic()) if isInfected else 0,
        int(game.isEconomicCrisis()) if isInfected else 0,

        # dependent on pathogen and city, indicator
        normalize(getMaxConnectedVictims(game, city, pathogen)[
            1], 0, maxWorldPopulation) if isInfected else 0,

        # bias
        1
    ])


def vectorizeState(game: GameWrapper):
    points = game.getPoints()
    cities = game.getCities()
    worldPopulation = getWorldPopulation(game)
    pathogenPrevalencesGlobal = getPathogenPrevalencesGlobal(
        game, worldPopulation)

    pointsNormalized = normalize(points, minPoints, maxPoints)
    worldPopulationNormalized = normalize(
        worldPopulation, minWorldPopulation, maxWorldPopulation)

    for city in cities:
        for pathogen in game.getPathogensCity(city):
            isInfected = True
            stateVec = getStateVec(game, city, pathogen, isInfected, pointsNormalized, worldPopulationNormalized, pathogenPrevalencesGlobal)
            yield city, pathogen, stateVec
        if game.getPathogensCity(city) == []:
            isInfected = False
            pathogen = None
            stateVec = getStateVec(game, city, pathogen, isInfected, pointsNormalized, worldPopulationNormalized, pathogenPrevalencesGlobal)
            yield city, pathogen, stateVec
