class GameWrapper:
    ratingToInt = {"--": 1, "-": 2, "o": 3, "+": 4, "++": 5}

    @classmethod
    def __formatPathogen(cls, pathogen, sinceRound, curRound):
        formattedPathogen = {}
        formattedPathogen["infectivity"] = cls.ratingToInt[pathogen["infectivity"]]
        formattedPathogen["mobility"] = cls.ratingToInt[pathogen["mobility"]]
        formattedPathogen["duration"] = cls.ratingToInt[pathogen["duration"]]
        formattedPathogen["lethality"] = cls.ratingToInt[pathogen["lethality"]]
        formattedPathogen["age"] = curRound - sinceRound
        return formattedPathogen

    def __init__(self, game):
        self.round = game["round"]
        self.outcome = game["outcome"]
        self.points = game["points"]
        self.cities = [city for city in game["cities"]]
        self.globalEvents = game.get("events", [])
        self.latitude = {city: game["cities"][city]
                         ["latitude"] for city in self.cities}
        self.longitude = {city: game["cities"][city]
                          ["longitude"] for city in self.cities}
        self.population = {city: game["cities"][city]
                           ["population"] for city in self.cities}
        self.connections = {city: game["cities"][city]
                            ["connections"] for city in self.cities}
        self.economy = {
            city: GameWrapper.ratingToInt[game["cities"][city]["economy"]] for city in self.cities}
        self.government = {
            city: GameWrapper.ratingToInt[game["cities"][city]["government"]] for city in self.cities}
        self.hygiene = {
            city: GameWrapper.ratingToInt[game["cities"][city]["hygiene"]] for city in self.cities}
        self.awareness = {
            city: GameWrapper.ratingToInt[game["cities"][city]["awareness"]] for city in self.cities}
        self.cityEvents = {city: game["cities"][city].get(
            "events", []) for city in self.cities}

        self.pathogens = {}
        for event in self.globalEvents:
            if event["type"] == "pathogenEncountered":
                pathogen = event["pathogen"]
                self.pathogens[pathogen["name"]] = GameWrapper.__formatPathogen(
                    pathogen, event["round"], self.round)

        self.pathogensCity = {city: [] for city in self.cities}
        self.pathogenPrevalences = {}
        for city in self.cities:
            for event in self.cityEvents[city]:
                if event["type"] == "outbreak":
                    pathogenName = event["pathogen"]["name"]
                    self.pathogensCity[city].append(pathogenName)
                    self.pathogenPrevalences[pathogenName,
                                             city] = event["prevalence"]

    def getRound(self):
        return self.round

    def getOutcome(self):
        return self.outcome

    def getPoints(self):
        return self.points

    def getCities(self):
        return self.cities

    def getGlobalEvents(self):
        return self.globalEvents

    def getPathogensGlobal(self):
        return self.pathogens

    def getLatitude(self, city):
        return self.latitude[city]

    def getLongitude(self, city):
        return self.longitude[city]

    def getPopulation(self, city):
        return self.population[city]

    def getConnections(self, city):
        return self.connections[city]

    def getEconomy(self, city):
        return self.economy[city]

    def getGovernment(self, city):
        return self.government[city]

    def getHygiene(self, city):
        return self.hygiene[city]

    def getAwareness(self, city):
        return self.awareness[city]

    def getCityEvents(self, city):
        return self.cityEvents[city]

    def getPathogensCity(self, city):
        return self.pathogensCity[city]

    def getPathogenInfectivity(self, pathogen):
        return self.pathogens[pathogen]["infectivity"]

    def getPathogenMobility(self, pathogen):
        return self.pathogens[pathogen]["mobility"]

    def getPathogenDuration(self, pathogen):
        return self.pathogens[pathogen]["duration"]

    def getPathogenLethality(self, pathogen):
        return self.pathogens[pathogen]["lethality"]

    def getPathogenAge(self, pathogen):
        return self.pathogens[pathogen]["age"]

    def getPathogenPrevalenceCity(self, pathogen, city):
        return self.pathogenPrevalences[pathogen, city]

    def isVaccineInDevelopment(self, pathogen):
        for event in self.globalEvents:
            if event["type"] == "vaccineInDevelopment":
                return True
        return False

    def isVaccineAvailable(self, pathogen):
        for event in self.globalEvents:
            if event["type"] == "vaccineAvailable":
                return True
        return False

    def isMedicationInDevelopment(self, pathogen):
        for event in self.globalEvents:
            if event["type"] == "medicationInDevelopment":
                return True
        return False

    def isMedicationAvailable(self, pathogen):
        for event in self.globalEvents:
            if event["type"] == "medicationAvailable":
                return True
        return False

    def isLargeScalePanic(self):
        for event in self.globalEvents:
            if event["type"] == "largeScalePanic":
                return True
        return False

    def isEconomicCrisis(self):
        for event in self.globalEvents:
            if event["type"] == "economicCrisis":
                return True
        return False

    def isOutbreak(self, city):
        for event in self.cityEvents[city]:
            if event["type"] == "outbreak":
                return True
        return False

    def isElectionsCalled(self, city):
        for event in self.cityEvents[city]:
            if event["type"] == "electionsCalled":
                return True
        return False

    def isAntiVaccinationism(self, city):
        for event in self.cityEvents[city]:
            if event["type"] == "antiVaccinationism":
                return True
        return False

    def isQuarantine(self, city):
        for event in self.cityEvents[city]:
            if event["type"] == "quarantine":
                return True
        return False

    def isInfluenceExerted(self, city):
        for event in self.cityEvents[city]:
            if event["type"] == "influenceExerted":
                return True
        return False

    def isCampaignLaunched(self, city):
        for event in self.cityEvents[city]:
            if event["type"] == "campaignLaunched":
                return True
        return False

    def isAirportClosed(self, city):
        for event in self.cityEvents[city]:
            if event["type"] == "airportClosed":
                return True
        return False

    def isHygienicMeasuresApplied(self, city):
        for event in self.cityEvents[city]:
            if event["type"] == "hygienicMeasuresApplied":
                return True
        return False

    def isBioTerrorism(self, city):
        for event in self.cityEvents[city]:
            if event["type"] == "bioTerrorism":
                return True
        return False

    def isUprising(self, city):
        for event in self.cityEvents[city]:
            if event["type"] == "uprising":
                return True
        return False

    def getClosedConnections(self, city):
        return [event["city"]
                for event in self.cityEvents[city]
                if event["type"] == "connectionClosed"]

    @staticmethod
    def doEndRound():
        return {"type": "endRound"}

    @staticmethod
    def doPutUnderQuarantine(city, rounds):
        return {"type": "putUnderQuarantine", "city": city, "rounds": rounds}

    @staticmethod
    def doCloseAirport(city, rounds):
        return {"type": "closeAirport", "city": city, "rounds": rounds}

    @staticmethod
    def doCloseConnection(fromCity, toCity, rounds):
        return {"type": "closeConnection", "fromCity": fromCity, "toCity": toCity, "rounds": rounds}

    @staticmethod
    def doDevelopVaccine(pathogen):
        return {"type": "developVaccine", "pathogen": pathogen}

    @staticmethod
    def doDeployVaccine(pathogen, city):
        return {"type": "deployVaccine", "pathogen": pathogen, "city": city}

    @staticmethod
    def doDevelopMedication(pathogen):
        return {"type": "developMedication", "pathogen": pathogen}

    @staticmethod
    def doDeployMedication(pathogen, city):
        return {"type": "deployMedication", "pathogen": pathogen, "city": city}

    @staticmethod
    def doExertInfluence(city):
        return {"type": "exertInfluence", "city": city}

    @staticmethod
    def doCallElections(city):
        return {"type": "callElections", "city": city}

    @staticmethod
    def doApplyHygienicMeasures(city):
        return {"type": "applyHygienicMeasures", "city": city}

    @staticmethod
    def doLaunchCampaign(city):
        return {"type": "launchCampaign", "city": city}

    @staticmethod
    def costEndRound():
        return 0

    @staticmethod
    def costPutUnderQuarantine(rounds):
        return 10 * rounds + 20

    @staticmethod
    def costCloseAirport(rounds):
        return 5 * rounds + 15

    @staticmethod
    def costCloseConnection(rounds):
        return 3 * rounds + 3

    @staticmethod
    def costDevelopVaccine():
        return 40

    @staticmethod
    def costDeployVaccine():
        return 5

    @staticmethod
    def costDevelopMedication():
        return 20

    @staticmethod
    def costDeployMedication():
        return 10

    @staticmethod
    def costExertInfluence():
        return 3

    @staticmethod
    def costCallElections():
        return 3

    @staticmethod
    def costApplyHygienicMeasures():
        return 3

    @staticmethod
    def costLaunchCampaign():
        return 3
