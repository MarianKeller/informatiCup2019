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
    if rating == "--":
        return 1

    if rating == "-":
        return 2

    if rating == "o":
        return 3

    if rating == "+":
        return 4

    if rating == "++":
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
    if "events" in game["cities"][city].keys():
        return game["cities"][city]["events"]
    else:
        return []


def getPathogens(game, city):
    events = getCityEvents(game, city)
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
    return 0


def getPathogenMobility(game, pathogen):
    events = getGameEvents(game)
    for event in events:
        if event["type"] == "pathogenEncountered" and event["pathogen"]["name"] == pathogen:
            return ratingToIndex(event["pathogen"]["mobility"])
    return 0


def getPathogenDuration(game, pathogen):
    events = getGameEvents(game)
    for event in events:
        if event["type"] == "pathogenEncountered" and event["pathogen"]["name"] == pathogen:
            return ratingToIndex(event["pathogen"]["duration"])
    return 0


def getPathogenLethality(game, pathogen):
    events = getGameEvents(game)
    for event in events:
        if event["type"] == "pathogenEncountered" and event["pathogen"]["name"] == pathogen:
            return ratingToIndex(event["pathogen"]["lethality"])
    return 0


def getPathogenPrevalenceCity(game, city, pathogen):
    events = getCityEvents(game, city)
    for event in events:
        if event["type"] == "outbreak" and event["pathogen"]["name"] == pathogen:
            return event["prevalence"]
    return 0


# testing revealed that prevalence is not always available; is it available at all?
# TODO find out if a pathogen has a world-prevalence; if no, get it by iteration through all cities
def getPathogenPrevalenceWorld(game, pathogen):
    events = getGameEvents(game)
    for event in events:
        if event["type"] == "pathogenEncountered" and event["pathogen"]["name"] == pathogen and "prevalence" in event:
            return ratingToIndex(event["prevalence"])
    return 0


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
