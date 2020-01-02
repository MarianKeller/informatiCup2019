ratingToIndex = {"--": 1, "-": 2, "o": 3, "+": 4, "++": 5}


def getRound(game):
    return game["round"]


def getOutcome(game):
    return game["outcome"]


def getPoints(game):
    return game["points"]


def getCities(game):
    return [city for city in game["cities"]]


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


def getEconomy(game, city):
    return ratingToIndex[game["cities"][city]["economy"]]


def getGovernment(game, city):
    return ratingToIndex[game["cities"][city]["government"]]


def getHygiene(game, city):
    return ratingToIndex[game["cities"][city]["hygiene"]]


def getAwareness(game, city):
    return ratingToIndex[game["cities"][city]["awareness"]]


def getCityEvents(game, city):
    return game["cities"][city].get("events", [])


def getPathogens(game, city):
    events = getCityEvents(game, city)
    return [event["pathogen"]["name"] for event in events if event["type"] == "outbreak"]


def getPathogenInfectivity(game, pathogen):
    events = getGameEvents(game)
    for event in events:
        if event["type"] == "pathogenEncountered" and event["pathogen"]["name"] == pathogen:
            return ratingToIndex[event["pathogen"]["infectivity"]]
    return 0


def getPathogenMobility(game, pathogen):
    events = getGameEvents(game)
    for event in events:
        if event["type"] == "pathogenEncountered" and event["pathogen"]["name"] == pathogen:
            return ratingToIndex[event["pathogen"]["mobility"]]
    return 0


def getPathogenDuration(game, pathogen):
    events = getGameEvents(game)
    for event in events:
        if event["type"] == "pathogenEncountered" and event["pathogen"]["name"] == pathogen:
            return ratingToIndex[event["pathogen"]["duration"]]
    return 0


def getPathogenLethality(game, pathogen):
    events = getGameEvents(game)
    for event in events:
        if event["type"] == "pathogenEncountered" and event["pathogen"]["name"] == pathogen:
            return ratingToIndex[event["pathogen"]["lethality"]]
    return 0


def getPathogenPrevalenceCity(game, city, pathogen):
    events = getCityEvents(game, city)
    for event in events:
        if event["type"] == "outbreak" and event["pathogen"]["name"] == pathogen:
            return event["prevalence"]
    return 0.0


# TODO identified as bottleneck of the program, use memoization (could lead to speedup of ~1/3) / move to preprocessing.py
# FIXME incorrect calculation
def getPathogenPrevalenceWorld(game, pathogen):
    prevalence = 0.0
    cities = getCities(game)
    for city in cities:
        prevalence = prevalence + \
            getPathogenPrevalenceCity(game, city, pathogen)
    return prevalence


def hasVaccineBeenDeveloped(game, pathogen):
    # TODO
    return False


def hasMedicationBeenDeveloped(game, pathogen):
    # TODO
    return False


def doEndRound():
    return {"type": "endRound"}


def doPutUnderQuarantine(city, rounds):
    return {"type": "putUnderQuarantine", "city": city, "rounds": rounds}


def doCloseAirport(city, rounds):
    return {"type": "closeAirport", "city": city, "rounds": rounds}


def doCloseConnection(fromCity, toCity, rounds):
    return {"type": "closeConnection", "fromCity": fromCity, "toCity": toCity, "rounds": rounds}


def doDevelopVaccine(pathogen):
    return {"type": "developVaccine", "pathogen": pathogen}


def doDeployVaccine(pathogen, city):
    return {"type": "deployVaccine", "pathogen": pathogen, "city": city}


def doDevelopMedication(pathogen):
    return {"type": "developMedication", "pathogen": pathogen}


def doDeployMedication(pathogen, city):
    return {"type": "deployMedication", "pathogen": pathogen, "city": city}


def doExertInfluence(city):
    return {"type": "exertInfluence", "city": city}


def doCallElections(city):
    return {"type": "callElections", "city": city}


def doApplyHygienicMeasures(city):
    return {"type": "applyHygienicMeasures", "city": city}


def doLaunchCampaign(city):
    return {"type": "launchCampaign", "city": city}


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


def costDeployVaccine():
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
