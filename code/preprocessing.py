import gameWrapper as gw
import math
from enum import Enum

climateZones = Enum('climateZones','TROPICAL SUBTROPICAL MODERATE ARCTIC')

def climateZone(latitude):
    absLat = math.abs(latitude)
    if abslat >= 0 or abslat <= 23.5:
        return climateZones.TROPICAL
    elif abslat > 23.5 or absLat <= 40:
        return climateZones.SUBTROPICAL
    elif abslat > 40 or absLat <= 60:
        return climateZones.MODERATE
    else:
        return climateZones.ARCTIC


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
        cityStateVector.append(climateZone(gw.getLatitude(city)))
        cityStateVector.append(gw.getPopulation(city))
        cityStateVector.append(gw.getEconomy(city))
        cityStateVector.append(gw.getGovernment(city))
        cityStateVector.append(gw.getHygiene(city))
        cityStateVector.append(gw.getAwareness(city))
        cityStateVector.append()
    
        # dependent of city indicator
