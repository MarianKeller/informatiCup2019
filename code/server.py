import json
from bottle import BaseRequest, post, request, run, route
import numpy as np
import requests
import subprocess
import postprocessor as actor
from gameWrapper import GameWrapper
import preprocessor as pre
import os

trainingMode = True
consoleOutput = False

if os.name == 'posix':
    gameFilePath = "ic20/ic20_linux"
elif os.name == 'nt':
    gameFilePath = "ic20/ic20_windows"


class playerServer(object):
    def __init__(self, id="game1", count=1, trainer=None, genome=None):
        self.hasTrainer = (trainer != None)
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
                print(self.genomeId, str(self.genomeCount), " action:", action, "\n")
            return action
        else:
            if self.hasTrainer:
                if consoleOutput:
                    print(self.genomeId, str(self.genomeCount), " from trainer: ",
                      game.getOutcome(), " round: ", game.getRound())
                self.myTrainer.collectGameResult(
                    self.genomeCount, game.getOutcome(), game.getRound())
            else:
                if consoleOutput:
                    print(game.getOutcome(), " round: ", game.getRound())
        return ""


class trainingServer(object):
    def parseRequest(self, params):
        self.genomeId = params["genomeId"]
        self.callbackUrl = params["callbackUrl"]
        self.runCount = params["runCount"]
        self.genome = np.array(params["genome"])

    def startGameWithGenome(self):
        params = request.json
        if consoleOutput:
            print(params)
        self.parseRequest(params)

        self.gameResults = []

        for i in range(0, self.runCount):
            ps = playerServer(self.genomeId, i, self, self.genome)
            path = "/" + self.genomeId + str(i)
            route(path, "POST", ps.gamePlayer)
            subprocess.Popen([gameFilePath, "-u", trainingServerUrl + path,
                              "-o", "logs/log_" + self.genomeId, str(i) + ".txt"])
            if consoleOutput:
                print(self.genomeId, " playing at: ", path)

        return {"id": self.genomeId, "state": "started"}

    def collectGameResult(self, genomeNr, result, rounds):
        self.gameResults.append([genomeNr, result, rounds])
        if len(self.gameResults) >= self.runCount:
            self.returnGameResults()

    def returnGameResults(self):
        jsonGameResults = {"genomeId": self.genomeId,
                           "gameResults": self.gameResults}
        requests.post(self.callbackUrl, json=jsonGameResults)


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
    run(host=gameServerIP, port=gameServerPort, quiet=True)

if trainingMode:
    launchTrainingServer()
else:
    launchGameServer()
