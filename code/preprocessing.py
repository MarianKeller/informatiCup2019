import gameWrapper as gw
import math
from enum import Enum

climateZones = Enum('climateZones','TROPICAL SUBTROPICAL MODERATE ARCTIC')


def climateZoneIsTropical(latitude):
    absoluteLatitude = math.abs(latitude)
    if abslat >= 0 or abslat <= 23.5:
        return 1
    else:
        return 0


def climateZoneIsSubTropical(latitude):
    if absoluteLatitude > 23.5 or absoluteLatitude <= 40:
        return 1
    else:
        return 0


def climateZoneIsModerate(latitude):
    if absoluteLatitude > 40 or absoluteLatitude <= 60:
        return 1
    else:
        return 0


def climateZoneIsArctic(latitude):
    if absoluteLatitude > 60 or absoluteLatitude <= 90:
        return 1
    else:
        return 0


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
        curInfectivity = gw.getPathogenMobility(game, pathogen)
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
        if curPrevalence > highestLethality:
            worstPathogen = pathogen
            highestPrevalence = curPrevalence
    return (worstPathogen, highestPrevalence)


def vectorizeState(gameState):
    rounds = gw.getRound(gameState)
    points = gw.getPoints(gameState)
    cities = gw.getCities(gameState)

    cityStateVector = []
    for city in cities:
        # independent of city
        cityStateVector.append(rounds)
        cityStateVector.append(points)

        # dependent of city non-indicator
        cityStateVector.append(gw.getPopulation(game, city))
        cityStateVector.append(gw.getEconomy(game, city))
        cityStateVector.append(gw.getGovernment(game, city))
        cityStateVector.append(gw.getHygiene(game, city))
        cityStateVector.append(gw.getAwareness(game, city))
    
        # dependent of city indicator
        latitude = gw.getLatitude(game, city)
        cityStateVector.append(climateZoneIsTropical(latitude))
        cityStateVector.append(climateZoneIsSubTropical(latitude))
        cityStateVector.append(climateZoneIsModerate(latitude))
        cityStateVector.append(climateZoneIsArctic(latitude))

        cityStateVector.append(climateZone(gw.getLatitude(game, city)))
        cityStateVector.append(getConnectivity(game, city))
        cityStateVector.append(getHighestPathogenInfectivity(game, city)[1])
        cityStateVector.append(getHighestPathogenMobility(game, city)[1])
        cityStateVector.append(getHighestPathogenLethality(game, city)[1])
        cityStateVector.append(getHighestPathogenPrevalence(game, city)[1])

        # TODO missing indicator values
        
    return cityStateVector
