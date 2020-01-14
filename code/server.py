import json
from bottle import BaseRequest, post, request, run, route
import numpy as np
import requests
import subprocess
import postprocessor as actor
from gameWrapper import GameWrapper
import preprocessor as pre

gameFilePath = "ic20_windows"

class playerServer(object):
    def __init__(self, id="game1", count=1, trainer=None, genome=None):
        self.hasTrainer = (trainer != None)
        self.myTrainer = trainer
        self.genomeId = id
        self.genomeCount = count
        self.genome = genome #TODO: specify genome format, pass from request and actually use the passed genome


    def gamePlayer(self):
        gameDict = request.json
        game = GameWrapper(gameDict)
        print(f'round: {game.getRound()}, outcome: {game.getOutcome()}')
        if(game.getOutcome() == 'pending'):
            action = actor.action(game, self.genome, doManualOptimizations=(not self.hasTrainer))
            #action = GameWrapper.doEndRound() # TODO: remove this line
            print("numPossibleActions: ", actor.numPossibleActions, "inputVectorSize: ", pre.inputVectorSize)
            print(self.genomeId, str(self.genomeCount), " action:", action, "\n")
            return action
        else:
            if self.hasTrainer:
                print(self.genomeId, str(self.genomeCount), " from trainer: ", game.getOutcome(), " round: ", game.getRound())
                self.myTrainer.collectGameResult(self.genomeCount, game.getOutcome(), game.getRound())
            else:
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
        print(params)
        self.parseRequest(params)

        self.gameResults = []

        for i in range(0,self.runCount):
            ps = playerServer(self.genomeId, i, self, self.genome)
            path = "/" + self.genomeId + str(i)
            route(path, "POST", ps.gamePlayer)
            subprocess.Popen([gameFilePath, "-u", trainingServerUrl + path, 
                "-o", "logs/log_", self.genomeId, str(i), ".txt"])
            print(self.genomeId, " playing at: ", path)

        return {"id" : self.genomeId, "state" : "started"}


    def collectGameResult(self, genomeNr, result, rounds):
        self.gameResults.append([genomeNr, result, rounds])
        if len(self.gameResults) >= self.runCount:
            self.returnGameResults()


    def returnGameResults(self):
        jsonGameResults = {"genomeId" : self.genomeId, "gameResults" : self.gameResults}
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
    gs = playerServer(genome=np.random.rand(actor.numPossibleActions, pre.inputVectorSize))
    route("/", "POST", gs.gamePlayer)
    BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
    run(host=gameServerIP, port=gameServerPort, quiet=True)

#launchTrainingServer()
launchGameServer()