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
consoleOutput = False

maxPlayerServerCount = 20

trainingServerPort = 50124
trainingServerIp = "0.0.0.0"
trainingServerUrl = "http://localhost:" + str(trainingServerPort)

if os.name == 'posix':
    gameFilePath = "ic20/ic20_linux"
    nullFile = "/dev/null"
elif os.name == 'nt':
    gameFilePath = "ic20/ic20_windows"
    nullFile = "./nul"


class Job:
    def __init__(self, genomeId, genome, runsMax, callbackUrl):
        self.genomeId = genomeId
        self.genome = genome
        self.runsMax = runsMax
        self.runsStarted = 0
        self.runsFinished = 0
        self.callbackUrl = callbackUrl
        self.results = []


class PlayerServer:
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
        if self.hasTrainer:
            print(f'round: {game.getRound()}, outcome: {game.getOutcome()}')
        if game.getOutcome() == 'pending':
            action = actor.action(
                game, self.genome, doManualOptimizations=(not self.hasTrainer))
            return action
        elif self.hasTrainer:
            self.myTrainer.collectGameResult(
                self, self.myJob, game.getOutcome(), game.getRound())
        return ""


class trainingServer:
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

        print("Job created: ", genomeId, " ", str(
            runCount))  # TODO: remove debug output

        self.jobList.append(Job(genomeId, genome, runCount, callbackUrl))
        self.__manager()

    def __manager(self):
        while self.jobList and len(self.availablePlayerServers) > 0:
            player = self.availablePlayerServers.pop()
            self.busyPlayerServers.append(player)

            job = self.jobList.pop()
            player.assignJob(job)

            for _ in range(job.runsMax):
                print("__manager assignment: ", "job: ", job.genomeId, "run number: ", str(
                    job.runsStarted + 1), "server: ", player.genomeId)
                path = "/" + job.genomeId + str(job.runsStarted)
                self.bottleInstance.route(path, "POST", player.gamePlayer)
                subprocess.Popen(
                    [gameFilePath, "-u", trainingServerUrl + path, "-t", "0", "-o", nullFile])
                job.runsStarted += 1

    def collectGameResult(self, player, job, result, rounds):
        job.runsFinished += 1
        job.results.append((result, rounds))
        if job.runsFinished == job.runsMax:
            self.busyPlayerServers.remove(player)
            self.availablePlayerServers.append(player)
            thread = threading.Thread(target=self.__returnJobResults, args=(
                job.genomeId, job.results, job.callbackUrl))
            thread.start()

        self.__manager()

    def __returnJobResults(self, genomeId, gameResults, callbackUrl):
        jsonGameResults = {"genomeId": genomeId,
                           "gameResults": gameResults}
        requests.post(callbackUrl, json=jsonGameResults)


def launchTrainingServer(serverIp, serverPort):
    trainingApp = bottle.Bottle()

    ts = trainingServer(trainingApp)
    trainingApp.route("/newjob", "POST", ts.newJob)
    BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
    trainingApp.run(host=serverIp, port=serverPort,
                    quiet=True, server='tornado')


launchTrainingServer(trainingServerIp, trainingServerPort)
