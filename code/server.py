import collections
import json
import os
import subprocess

import numpy as np
import requests
from bottle import BaseRequest, post, request, route, run

import postprocessor as actor
import preprocessor as pre
from gameWrapper import GameWrapper

trainingMode = True
consoleOutput = False

if os.name == 'posix':
    gameFilePath = "ic20/ic20_linux"
elif os.name == 'nt':
    gameFilePath = "ic20/ic20_windows"


class playerServer(object):
    def __init__(self, id="game1", count=1, trainer=None, genome=None):
        self.hasTrainer = (trainer is not None)
        self.myTrainer = trainer
        self.genomeId = id
        self.genomeCount = count
        self.genome = genome

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
                print(self.genomeId, str(self.genomeCount),
                      " action:", action, "\n")
            return action
        else:
            if self.hasTrainer:
                if consoleOutput:
                    print(self.genomeId, str(self.genomeCount), " from trainer: ",
                          game.getOutcome(), " round: ", game.getRound())
                self.myTrainer.collectGameResult(
                    self.genomeCount, self.genomeId, game.getOutcome(), game.getRound())
            else:
                if consoleOutput:
                    print(game.getOutcome(), " round: ", game.getRound())
        return ""


class trainingServer(object):
    def __init__(self):
        self.gameResults = {}
        self.pendingRuns = {}
        self.maxRuns = {}
        self.callbackURL = {}
        self.genome = {}

    def startPlayerServer(self, genomeId, genome):
        pendingRuns = self.pendingRuns[genomeId]
        maxRuns = self.maxRuns[genomeId]
        nthRun = maxRuns - pendingRuns + 1
        ps = playerServer(genomeId, nthRun, self, genome)
        path = "/" + genomeId + str(nthRun)
        route(path, "POST", ps.gamePlayer)
        # subprocess.Popen([gameFilePath, "-u", trainingServerUrl + path,
        #                   "-o", "logs/log_" + genomeId, str(i) + ".txt"])
        nullFile = "./nul" if os.name == "nt" else "/dev/null"
        subprocess.Popen(
            [gameFilePath, "-u", trainingServerUrl + path, "-o", nullFile, "-t", "0"])
        # subprocess.Popen([gameFilePath, "-u", trainingServerUrl + path])
        if consoleOutput:
            print(genomeId, " playing at: ", path)

    def startGameWithGenome(self):
        params = request.json

        # parse request
        genomeId = params["genomeId"]
        callbackUrl = params["callbackUrl"]
        runCount = params["runCount"]
        genome = np.array(params["genome"])

        if consoleOutput:
            print(genomeId, callbackUrl, runCount)

        self.gameResults[genomeId] = []
        self.pendingRuns[genomeId] = runCount
        self.maxRuns[genomeId] = runCount
        self.callbackURL[genomeId] = callbackUrl
        self.genome[genomeId] = genome

        self.startPlayerServer(genomeId, genome)

        return {"id": genomeId, "state": "started"}

    def collectGameResult(self, genomeNr, genomeId, result, rounds):
        print("evaluated " + str(genomeId) + "_" + str(genomeNr))
        self.gameResults[genomeId].append([genomeNr, result, rounds])
        self.pendingRuns[genomeId] -= 1
        if self.pendingRuns[genomeId] == 0:
            self.returnGameResults(genomeId)
        else:
            self.startPlayerServer(genomeId, self.genome[genomeId])

    def returnGameResults(self, genomeId):
        jsonGameResults = {"genomeId": genomeId,
                           "gameResults": self.gameResults[genomeId]}
        requests.post(self.callbackURL[genomeId], json=jsonGameResults)


trainingServerPort = 50124
trainingServerUrl = "http://localhost:50124"
trainingServerIP = "0.0.0.0"


def launchTrainingServer():
    ts = trainingServer()
    route("/startwithgenome", "POST", ts.startGameWithGenome)
    BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
    run(host=trainingServerIP, port=trainingServerPort, quiet=True)


gameServerPort = 50123
gameServerUrl = "http://localhost:50123"
gameServerIP = "0.0.0.0"


def launchGameServer():
    gs = playerServer(genome=np.random.rand(
        actor.numPossibleActions, pre.inputVectorSize))
    route("/", "POST", gs.gamePlayer)
    BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
    run(host=gameServerIP, port=gameServerPort, quiet=True, server='tornado')


if trainingMode:
    launchTrainingServer()
else:
    launchGameServer()
