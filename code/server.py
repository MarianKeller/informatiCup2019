import json

from bottle import BaseRequest, post, request, run

import postprocessor as actor
from gameWrapper import GameWrapper
import preprocessor as pre
import numpy as np


@post("/")
def index():
    gameDict = request.json
    game = GameWrapper(gameDict)
    print(f'round: {game.getRound()}, outcome: {game.getOutcome()}')
    action = actor.action(game, np.random.rand(actor.numPossibleActions, pre.inputVectorSize), np.random.rand(
        actor.numActionsWithRoundParameter, pre.inputVectorSize), doManualOptimizations=True)
    print("action:", action, "\n")
    return action


BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
run(host="0.0.0.0", port=50123, quiet=True)
