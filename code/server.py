import json

from bottle import BaseRequest, post, request, run

import actor
import gameWrapper as gw
import preprocessing as pre


@post("/")
def index():
    game = request.json
    print(f'round: {game["round"]}, outcome: {game["outcome"]}')
    action = gw.doEndRound()
    return action


BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
run(host="0.0.0.0", port=50123, quiet=True)
