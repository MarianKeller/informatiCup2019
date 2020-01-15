import json
from hashlib import blake2s

import numpy
import requests
from bottle import BaseRequest, post, request, route, run

import individual

trainingServerUrl = "http://localhost:50124"


def hashBlake2(val, hSize=32):
    h = blake2s(digest_size=hSize)
    h.update(val)
    return h.hexdigest()


class FitnessServer():
    geneticServerPort = 50122
    geneticServerUrl = "http://localhost:50122"
    geneticServerIP = "0.0.0.0"

    genomeRunCount = 2

    def __init__(self):
        self.__fitnessDict = {}
        self.__callback = None
        self.__pendingCalculations = 0

    def __computedResult(self):
        if self.__pendingCalculations == 0:
            for individual in self.__individuals:
                if self.__fitnessDict.get(individual.ID) != None:
                    individual.fitness = self.__fitnessDict[individual.ID]
            self.__callback()

    def __computeFitness(self):
        params = request.json
        genomeID = params["genomeId"]
        fitnessVec = []
        if self.__fitnessDict.get(genomeID) == None:
            for [genomeNr, result, rounds] in params["gameResults"]:
                win = int(result == "win")
                def phi(x): return 1/(1+numpy.log(x))
                fitness = 0.5 * (1 + (-1) ** (win + 1) * phi(rounds))
                fitnessVec.append(fitness)
            self.__fitnessDict[genomeID] = numpy.median(fitnessVec)
        self.__pendingCalculations -= 1
        self.__computedResult()
        return "ACK"

    def __launchCallbackServer(self, path):
        route(path, "POST", self.__computeFitness)

    def __evaluateGenome(self, genome):
        genomeID = str(hashBlake2(genome.tostring(), 10))
        self.__launchCallbackServer("/genomeperformance/" + genomeID)
        postData = {"genomeId": genomeID,
                    "callbackUrl": FitnessServer.geneticServerUrl + "/genomeperformance/" + genomeID,
                    "runCount": FitnessServer.genomeRunCount,
                    "genome": genome.tolist()}
        requests.post(trainingServerUrl + "/startwithgenome", json=postData)
        return genomeID

    def evaluateGenomes(self, individuals, callback):
        self.__callback = callback
        self.__individuals = individuals
        self.__pendingCalculations = len(individuals)
        for individual in self.__individuals:
            individual.ID = self.__evaluateGenome(individual.genome)
