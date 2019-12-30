#TODO always test if rounds > 0 for do actions, else throw error
#TODO always check if city is valid, else throw error (?)

def getRound(game):
    return game["round"]


def getOutcome(game):
    return game["outcome"]


def getPoints(game):
    return game["points"]


def getCities(game):
    cities = []
    for city in game["cities"].keys():
        cities.append(city)
    return cities


def getGameEvents(game):
    return game["events"]


def getLatitude(game, city):
    return game["cities"][city]["latitude"]


def getLongitude(game, city):
    return game["cities"][city]["longitude"]


def getPopulation(game, city):
    return game["cities"][city]["population"]


def getConnections(game, city):
    return game["cities"][city]["connections"]


def ratingToIndex(rating):
    if  rating == "--":
        return 1

    if  rating == "-":
        return 2

    if  rating == "o":
        return 3

    if  rating == "+":
        return 4

    if  rating == "++":
        return 5


def getEconomy(game, city):
    return ratingToIndex(game["cities"][city]["economy"])


def getGovernment(game, city):
    return ratingToIndex(game["cities"][city]["government"])


def getHygiene(game, city):
    return ratingToIndex(game["cities"][city]["hygiene"])


def getAwareness(game, city):
    return ratingToIndex(game["cities"][city]["awareness"])


def getCityEvents(game, city):
    if events in game["cities"][city]:
        return game["cities"][city]
    else
        return []


def getPathogens(game, city):
    events = getCityEvents(game, city)
    if events is None:
        return None
    else:
        pathogens = []
        for event in events:
            if event["type"] == "outbreak":
                pathogens.append(event["pathogen"]["name"])
        return pathogens


def getPathogenInfectivity(game, pathogen):
    events = getGameEvents(game)
    for event in events:
        if event["type"] == "pathogenEncountered" and event["pathogen"]["name"] == pathogen:
            return ratingToIndex(event["pathogen"]["infectivity"])


def getPathogenMobility(game, pathogen):
    events = getGameEvents(game)
    for event in events:
        if event["type"] == "pathogenEncountered" and event["pathogen"]["name"] == pathogen:
            return ratingToIndex(event["pathogen"]["mobility"])


def getPathogenDuration(game, pathogen):
    events = getGameEvents(game)
    for event in events:
        if event["type"] == "pathogenEncountered" and event["pathogen"]["name"] == pathogen:
            return ratingToIndex(event["pathogen"]["duration"])


def getPathogenLethality(game, pathogen):
    events = getGameEvents(game)
    for event in events:
        if event["type"] == "pathogenEncountered" and event["pathogen"]["name"] == pathogen:
            return ratingToIndex(event["pathogen"]["lethality"])


def getPathogenPrevalenceCity(game, city, pathogen):
    events = getCityEvents(game)
    for event in events:
        if event["type"] == "outbreak" and event["pathogen"]["name"] == pathogen:
            return ratingToIndex(event["prevalence"])


def getPathogenPrevalenceWorld(game, pathogen):
    events = getGameEvents(game)
    for event in events:
        if event["type"] == "pathogenEncountered" and event["pathogen"]["name"] == pathogen:
            return ratingToIndex(event["prevalence"])


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
