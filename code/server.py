from bottle import post, request, run, BaseRequest
import json
import gameWrapper as gw
import preprocessing as pre
import actor


@post("/")
def index():
    game = request.json
    print(f'round: {game["round"]}, outcome: {game["outcome"]}')
    action = actor.action(game)
    print("action: ", action)
    return action


BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
run(host="0.0.0.0", port=50123, quiet=True)
