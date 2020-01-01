import json

from bottle import BaseRequest, post, request, run

import postprocessor as actor
import gameWrapper as gw
import preprocessor as pre
import numpy as np


@post("/")
def index():
    game = request.json
    print(f'round: {game["round"]}, outcome: {game["outcome"]}')
    action = actor.action(game, np.random.rand(actor.numPossibleActions, pre.inputVectorSize), np.random.rand(actor.numActionsWithRoundParameter, pre.inputVectorSize))
    print("\n", action, "\n")
    return action


BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
run(host="0.0.0.0", port=50123, quiet=True)
