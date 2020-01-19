import collections
import json
import os
import subprocess
import threading
import uuid

import numpy as np
import bottle
from bottle import BaseRequest, post, request, route, run

import postprocessor as actor
import preprocessor as pre
from gameWrapper import GameWrapper

if os.name == 'posix':
    gameFilePath = "ic20/ic20_linux"
    nullFile = "/dev/null"
elif os.name == 'nt':
    gameFilePath = "ic20/ic20_windows"
    nullFile = "./nul"

playerServerUrl = "http://localhost:50122"

class PlayerServer:
    def __init__(self, id="game1", trainer=None, genome=None):
        self.hasTrainer = (trainer is not None)
        self.myTrainer = trainer
        self.genomeId = id
        self.genome = genome
        self.proc = None
        self.uuid = str(uuid.uuid4())

    def launchGame(self):
        path = "/" + self.genomeId + self.uuid
        self.proc = subprocess.Popen(
                    [gameFilePath, "-u", playerServerUrl + path, "-t", "1000", "-o", nullFile])
        route(path, "POST", self.gamePlayer)
        return self.proc
        

    def gamePlayer(self):
        gameDict = request.json
        game = GameWrapper(gameDict)
        if not self.hasTrainer:
            print(f'round: {game.getRound()}, outcome: {game.getOutcome()}')
        if game.getOutcome() == 'pending':
            action = actor.action(
                game, self.genome, doManualOptimizations=(not self.hasTrainer))
            return action
        elif self.hasTrainer:
            self.myTrainer.collectGameResult(
                self, self.genomeId, game.getOutcome(), game.getRound(), self.proc)
        return ""