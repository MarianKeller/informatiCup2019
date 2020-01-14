import json
from hashlib import blake2s

import numpy
from bottle import BaseRequest, post, request, route, run

import requests

import individual

trainingServerUrl = "http://localhost:50124"


def hashBlake2(val, hSize=32):
    h = blake2s(digest_size=hSize)
    h.update(val)
    return h.hexdigest()


class FitnessServer(object):
    geneticServerPort = 50122
    geneticServerUrl = "http://localhost:50122"
    geneticServerIP = "0.0.0.0"

    genomeRunCount = 20

    def __init__(self):
        self.genomeFitnessDictionary = {}
        #BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
        #run(host=FitnessServer.geneticServerIP, port=FitnessServer.geneticServerPort, quiet=True)

    def launchCallbackServer(self, path):
        route(path, "POST", self.computeFitness)

    def computeFitness(self):
        params = request.json
        genomeId = params["genomeId"]
        fitnessVect = []
        for [genomeNr, result, rounds] in params["gameResults"]:
            intResult = int(result == "win")
            fitnessVect.append(0.5 + ((-1) ** (intResult+1))*(1/(1+numpy.log(rounds)))*0.5)
        self.genomeFitnessDictionary[genomeId] = numpy.median(fitnessVect)
        self.resultsArrived = self.resultsArrived + 1

        self.callbackFunction(genomeId, self.genomeFitnessDictionary[genomeId])
        
        print(fitnessVect, " median: ", self.genomeFitnessDictionary[genomeId])
        return "ACK"

    def evaluateGenome(self, genome, callbackFunction):
        self.callbackFunction = callbackFunction
        genomeId = str(hashBlake2(genome.tostring(), 10))
        self.launchCallbackServer("/genomeperformance/" + genomeId)

        postData = {"genomeId": genomeId,
                    "callbackUrl": FitnessServer.geneticServerUrl + "/genomeperformance/" + genomeId,
                    "runCount": FitnessServer.genomeRunCount,
                    "genome": genome.tolist()}

        requests.post(trainingServerUrl + "/startwithgenome", json=postData)
        return genomeId


    def getAsyncFitnessList(self, individualsList, fitnessListComplete):
        self.fitnessListComplete = fitnessListComplete
        self.asyncGenomeIds = []
        self.individualsList = individualsList
        for specimen in self.individualsList:
            self.asyncGenomeIds.append(self.evaluateGenome(specimen.genome, self.asyncCallback))
        self.resultsArrived = 0

    def asyncCallback(self, genomeId, fitness):
        self.genomeFitnessDictionary[genomeId] = fitness
        if self.resultsArrived >= len(self.asyncGenomeIds):
            for i in range(0, len(self.individualsList)):
                self.individualsList[i].fitness = self.genomeFitnessDictionary[self.asyncGenomeIds[i]]
            
            self.fitnessListComplete()


    def getSyncFitnessList(self, genomeList):
        genomeIds = []
        genomeFitness = []
        self.resultsArrived = 0

        for genome in genomeList:
            genomeIds.append(self.evaluateGenome(genome, self.syncCallback))

        while self.resultsArrived <= len(genomeList):
            pass

        self.resultsArrived = 0
        for genomeId in genomeIds:
            genomeFitness.append(genomeFitnessDictionary[genomeId])
        return genomeFitness

    def syncCallback(self):
        pass


def resultReady(genomeId, medianFitness):
    print("result: ", medianFitness)


# fitServ = fitnessServer() # TODO
# fitServ.evaluateGenome(numpy.random.rand(12, 31), resultReady) # TODO
#
