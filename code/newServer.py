import collections
import json
import os
import subprocess
import threading

import numpy as np
import requests
import bottle
from bottle import BaseRequest, post, request, route, run

import postprocessor as actor
import preprocessor as pre
from gameWrapper import GameWrapper

trainingMode = True
consoleOutput = True

maxPlayerServerCount = 20

trainingServerPort = 50124
trainingServerIp = "0.0.0.0"
trainingServerUrl = "http://localhost:" + str(trainingServerPort)

if os.name == 'posix':
    gameFilePath = "ic20/ic20_linux"
elif os.name == 'nt':
    gameFilePath = "ic20/ic20_windows"


class Job(object):
    def __init__(self, genomeId, genome, pendingRuns, callbackURL):
        self.genomeId = genomeId
        self.genome = genome
        self.pendingRuns = pendingRuns
        self.callbackURL = callbackURL
        self.results = []


class PlayerServer(object):
    def __init__(self, id="game1", trainer=None, genome=None, job=None):
        self.hasTrainer = (trainer is not None)
        self.myTrainer = trainer
        self.myJob = job
        self.genomeId = id
        self.genome = genome

    def assignJob(self, job):
        self.myJob = job
        self.genomeId = job.genomeId
        self.genome = job.genome

    def gamePlayer(self):
        gameDict = request.json
        game = GameWrapper(gameDict)
        if consoleOutput:
            print(f'round: {game.getRound()}, outcome: {game.getOutcome()}')
        if(game.getOutcome() == 'pending'):
            action = actor.action(
                game, self.genome, doManualOptimizations=(not self.hasTrainer))
            if consoleOutput:
                print("numPossibleActions: ", actor.numPossibleActions,
                      "inputVectorSize: ", pre.inputVectorSize)
                print(self.genomeId, str(self.myJob.pendingRuns),
                      " action:", action, "\n")
            return action
        else:
            if self.hasTrainer:
                if consoleOutput:
                    print(self.genomeId, " from trainer: ",
                          game.getOutcome(), " round: ", game.getRound())
                self.myTrainer.collectGameResult(
                    self, self.myJob, game.getOutcome(), game.getRound())
            else:
                if consoleOutput:
                    print(game.getOutcome(), " round: ", game.getRound())
        return ""


class trainingServer(object):
    def __init__(self, bottleInstance):
        self.bottleInstance = bottleInstance
        self.jobList = []
        self.availablePlayerServers = []
        self.busyPlayerServers = []

        for i in range(0, maxPlayerServerCount):
            self.availablePlayerServers.append(PlayerServer(trainer=self))

    def newJob(self):
        params = request.json
        
        # parse request
        genomeId = params["genomeId"]
        callbackUrl = params["callbackUrl"]
        runCount = params["runCount"]
        genome = np.array(params["genome"])

        self.jobList.append(Job(genomeId, genome, runCount, callbackUrl))
        self.__manager()

    def __manager(self):
        while len(self.jobList) <= 0 and len(self.availablePlayerServers) <= 0:
            job = self.jobList[0]
            player = self.availablePlayerServers.pop()
            self.busyPlayerServers.append(player)

            player.assignJob(job)

            path = "/" + job.genomeId + str(job.pendingRuns)
            self.bottleInstance.route(path, "POST", player.gamePlayer)

            subprocess.Popen(
                [gameFilePath, "-u", trainingServerUrl + path, "-t", "1000"])

            job.pendingRuns = job.pendingRuns - 1

    def collectGameResult(self, player, job, result, rounds):
        self.availablePlayerServers.append(player)
        self.busyPlayerServers.remove(player)

        job.results.append([result, rounds])

        if job.pendingRuns <= 0:
            thread = threading.Thread(target=self.__returnJobResults, args=(
                job.genomeId, job.gameResults, job.callbackUrl))
            del job

        self.__manager()

    def __returnJobResults(self, genomeId, gameResults, callbackUrl):
        jsonGameResults = {"genomeId": genomeId,
                           "gameResults": gameResults}
        requests.post(callbackURL, json=jsonGameResults)

    def test(self):
        return "Hi! This is test!"


def launchTrainingServer(serverIp, serverPort):
    trainingApp = bottle.Bottle()
    
    ts = trainingServer(trainingApp)
    trainingApp.route("/newjob", "POST", ts.newJob)
    trainingApp.route("/test", "POST",ts.test)
    trainingApp.run(host=serverIp, port=serverPort, quiet=True)


launchTrainingServer(trainingServerIp, trainingServerPort)
