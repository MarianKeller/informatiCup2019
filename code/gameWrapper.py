def getRound(game):
    return game["round"]


def getOutcome(game):
    return game["outcome"]


def getPoints(game):
    return game["points"]


def getCities(game):
    cities = []
    for city in game["cities"]:
        cities.append(city)
    return cities


def getLatitude(city):
    return city["latitude"]


def getLongitude(city):
    return city["longitude"]


def getPopulation(city):
    return city["population"]


def getConnections(city):
    return city["connections"]


def getEconomy(city):
    return city["economy"]


def getHygiene(city):
    return city["hygiene"]


def getAwareness(city):
    return city["awareness"]


def getEvents(city):
    return city["events"]
