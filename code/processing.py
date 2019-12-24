import gameWrapper as gw

def climateZone(latitude, longitude):
    # TODO implement
    pass


def getConnectivity(city):
    """Rank connectivity to other cities using PageRank algorithm (random surfer)"""
    # TODO implement
    pass


def getVictimConnectivity(city):
    """Rank connectivity to uninfected cities using PageRank algorith"""
    # TODO implement
    pass


def getWorstPathogenInfectivity(city):
    # TODO implement
    pass


def getWorstPathogenMobility(city):
    # TODO implement
    pass

def getWorstPathogenDuration(city):
    # TODO implement
    pass

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
        cityStateVector.append(climateZone(gw.getLatitude(city), gw.getLongitude(city)))
        cityStateVector.append(gw.getPopulation(city))
        cityStateVector.append(gw.getEconomy(city))
        cityStateVector.append(gw.getGovernment(city))
        cityStateVector.append(gw.getHygiene(city))
        cityStateVector.append(gw.getAwareness(city))
    
        # dependent of city indicator

