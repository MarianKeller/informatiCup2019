#TODO always test if rounds > 0 for do actions, else throw error
#TODO always check if city is valid, else throw error (?)
#TODO use hungarian notation (?)


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


def doEndRound():
    return {"type" : "endRound"}


def doPutUnderQuarantine(city, rounds):
    return {"type" : "putUnderQuarantine", "city" : city, "rounds": rounds}


def doCloseAirport(city, rounds):
    {"type" : "closeAirport", "city" : "<Name einer Stadt: S>", "rounds" : "<Anzahl Runden: R, natürliche Zahl > 0>"}


def doCloseConnection(fromCity, toCity, rounds):
    {"type" : "closeConnection", "fromCity" : fromCity, "toCity" : toCity, "rounds" : rounds}


def doDevelopVaccine(pathogen):
    {"type" : "developVaccine", "pathogen" : pathogen}


def doDeployVaccine(pathogen, city):
    {"type" : "deployVaccine", "pathogen" : pathogen, "city" : city}


def doDevelopMedication(pathogen):
    {"type" : "developMedication", "pathogen" : pathogen}


def doDeployMedication(pathogen, city):
    {"type" : "deployMedication", "pathogen" : pathogen, "city" : city}


def doExertInfluence(city):
    {"type": "exertInfluence", "city" : city}


def doCallElections(city):
    {"type" : "callElections", "city" : city}


def doApplyHygienicMeasures(city):
    {"type" : "applyHygienicMeasures", "city" : city}


def doLaunchCampaign(city):
    {"type" : "launchCampaign", "city" : city}


def costEndRound():
    return 0


def costPutUnderQuarantine(rounds):
    return 10 * rounds + 20


def costCloseAirport(rounds):
    return 5 * rounds + 15


def costCloseConnection(rounds):
    return 3 * rounds + 3


def costDevelopVaccine():
    return 40
    

def getCostDeployVaccine():
    return 5


def costDevelopMedication():
    return 20


def costDeployMedication():
    return 10


def costExertInfluence():
    return 3


def costCallElections():
    return 3


def costApplyHygienicMeasures():
    return 3


def costLaunchCampaign():
    return 3
