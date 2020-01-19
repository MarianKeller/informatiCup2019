import json
from hashlib import blake2s

import numpy
import requests
from bottle import BaseRequest, post, request, route, run

import time
import schedule
import threading

from playerServer import PlayerServer

def hashBlake2(val, hSize=32):
    h = blake2s(digest_size=hSize)
    h.update(val)
    return h.hexdigest()

class FitnessServer():
    genomeRunCount = 1 # how many times one genome should be run
    maxPlayerCount = 20 # how many players should run in parallel at a time

    playerServerIp = "0.0.0.0"
    playerServerPort = 50122

    def __init__(self):
        self.__individuals = []
        self.__fitnessDict = {}
        self.__jobQueue = []
        self.__callback = None
        self.__currPlayerCount = 0

        schedule.every(5).seconds.do(self.__queueManager)
        schedule.every(30).seconds.do(self.__watchdog)
        self.__schedulerThread = None
        self.__schedulerAbortEvent = threading.Event()

    def __cleanup(self):
        callback = self.__callback

        self.__schedulerAbortEvent.set() # abort thread
        self.__individuals = []
        self.__fitnessDict = {}
        self.__jobQueue = []
        self.__currPlayerCount = 0
        self.__callback = None
        callback()

    def __scheduler(self):
        while not self.__schedulerAbortEvent.is_set():
            schedule.run_pending()
            time.sleep(1)

    watchdogTriggerCount = 15
    def __watchdog(self):
        try:
            for genomeId in self.__fitnessDict:
                for pid in self.__fitnessDict[genomeId]["processList"]:
                    timerCount = self.__fitnessDict[genomeId]["processList"][pid]["watchDogCount"]
                    if (timerCount >= FitnessServer.watchdogTriggerCount):
                        print("Watchdog reset one Player for Genome:", str(genomeId))
                        self.__currPlayerCount -= 1

                        player = self.__fitnessDict[genomeId]["processList"][pid]["player"]
                        self.__currPlayerCount -= 1
                        del player
                        self.__fitnessDict[genomeId]["processList"].pop(pid, None)

                        pid.kill()
                        self.__addJob(genomeId)

                        break
                    else:
                        self.__fitnessDict[genomeId]["processList"][pid]["watchDogCount"] += 1

        except Exception as e:
            print("Error in __watchdog")
            print(str(e))

    def __computedResult(self):
        incompleteCounter = 0
        for individual in self.__individuals:
                if self.__fitnessDict[individual.ID]["medianFitness"] >= 0:
                    individual.fitness = self.__fitnessDict[individual.ID]["medianFitness"]
                else:
                    incompleteCounter += 1
        if incompleteCounter == 0:
            self.__cleanup()
            
    def collectGameResult(self, playerServer, genomeId, result, rounds, pid):
        if genomeId in self.__fitnessDict:
            win = int(result == "win")
            def phi(x): return 1/(1+numpy.log(x))
            fitness = 0.5 * (1 + (-1) ** (win + 1) * phi(rounds))
            self.__fitnessDict[genomeId]["results"].append(fitness)
            print("result collected: ", genomeId, ": fitness = ", str(fitness))
            self.__currPlayerCount -= 1
            
            if len(self.__fitnessDict[genomeId]["results"]) >= self.__fitnessDict[genomeId]["runCount"]:
                self.__fitnessDict[genomeId]["medianFitness"] = numpy.median(self.__fitnessDict[genomeId]["results"])
                self.__computedResult()
            pid.kill()
            del playerServer

    def __evaluateGenome(self, genome):
        genomeId = str(hashBlake2(genome.tostring(), 10))
        self.__fitnessDict[genomeId] = {"genome": genome,
                                      "runCount": FitnessServer.genomeRunCount,
                                      "medianFitness": -1,
                                      "results": [],
                                      "processList": {}}
        for i in range(0, FitnessServer.genomeRunCount):
            self.__addJob(genomeId)

        return genomeId

    def __addJob(self, genomeId):
        self.__jobQueue.append(genomeId)

    def __queueManager(self):
        if FitnessServer.maxPlayerCount > self.__currPlayerCount and len(self.__jobQueue) > 0:
            print("__queueManager starts jobs:")
            while len(self.__jobQueue) > 0:
                if FitnessServer.maxPlayerCount > self.__currPlayerCount and len(self.__jobQueue) > 0:
                    job = self.__jobQueue.pop()
                    player = PlayerServer(id=job, genome=self.__fitnessDict[job]["genome"], trainer=self)
                    pid = player.launchGame()
                    self.__currPlayerCount += 1
                    self.__fitnessDict[job]["processList"][pid] = {}
                    self.__fitnessDict[job]["processList"][pid]["watchDogCount"] = 0
                    self.__fitnessDict[job]["processList"][pid]["player"] = player
                else:
                    break


    def evaluateGenomes(self, individuals, callback):
        self.__schedulerAbortEvent = threading.Event()
        self.__schedulerThread = threading.Thread(target=self.__scheduler)
        self.__schedulerThread.start()

        self.__callback = callback
        self.__individuals = [
            individual for individual in individuals if individual.fitness is None or numpy.random.rand() <= 0.1]
        self.__pendingCalculations = len(self.__individuals)
        if self.__pendingCalculations == 0:
            self.__cleanup()
        for i in range(len(self.__individuals)):
            individual = self.__individuals[i]
            individual.ID = self.__evaluateGenome(individual.genome)
