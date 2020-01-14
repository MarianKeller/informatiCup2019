import json
from hashlib import blake2s

import numpy
from bottle import BaseRequest, post, request, route, run

import requests
from deap import algorithms, base, creator, tools

geneticServerPort = 50122
geneticServerUrl = "http://localhost:50122"
geneticServerIP = "0.0.0.0"

trainingServerUrl = "http://localhost:50124"


def hashBlake2(val, hSize=32):
    h = blake2s(digest_size=hSize)
    h.update(val)
    return h.hexdigest()


class FitnessServer(object):
    def __init__(self):
        self.genomeFitnessDictionary = {}

    def launchCallbackServer(self, path):
        route(path, "POST", self.computeFitness)

    def computeFitness(self):
        params = request.json
        genomeId = params["genomeId"]
        fitnessVect = []
        for [genomeNr, result, rounds] in params["gameResults"]:
            intResult = int(result == "win")
            fitnessVect.append([0.5 + ((-1) ** (intResult+1))*(1/rounds)*0.5])
        self.genomeFitnessDictionary[genomeId] = numpy.median(fitnessVect)
        self.callbackFunction(genomeId, self.genomeFitnessDictionary[genomeId])
        self.resultsArrived = self.resultsArrived + 1
        print(fitnessVect, " median: ", self.genomeFitnessDictionary[genomeId])
        return "ACK"

    def evaluateGenome(self, genome, callbackFunction):
        self.callbackFunction = callbackFunction
        genomeId = str(hashBlake2(genome.tostring(), 10))
        self.launchCallbackServer("/genomeperformance/" + genomeId)

        genomeRunCount = 20

        postData = {"genomeId": genomeId,
                    "callbackUrl": geneticServerUrl + "/genomeperformance/" + genomeId,
                    "runCount": genomeRunCount,
                    "genome": genome.tolist()}

        requests.post(trainingServerUrl + "/startwithgenome", json=postData)
        return genomeId

    def getSyncFitnessList(self, genomeList):
        genomeIds = []
        genomeFitness = []
        self.resultsArrived = 0
        for genome in genomeList:
            genomeId.append(self.evaluateGenome(genome))
        while self.resultArrived <= len(genomeList):
            pass
        for genomeId in genomeIds:
            genomeFitness.append(genomeFitnessDictionary[genomeId])
        return genomeFitness

    def getSyncFitness(self, genome):
        self.resultsArrived = 0
        genomeId = self.evaluateGenome(genome)
        while self.resultArrived <= len(genomeList):
            pass
        return self.genomeFitnessDictionary[genomeId]


def resultReady(genomeId, medianFitness):
    print("result: ", medianFitness)


# fitServ = fitnessServer() # TODO
# fitServ.evaluateGenome(numpy.random.rand(12, 31), resultReady) # TODO
BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
run(host=geneticServerIP, port=geneticServerPort, quiet=True)
