import json
from bottle import BaseRequest, post, request, run, route

geneticServerPort = 50124
geneticServerUrl = "http://localhost:50124"
geneticServerIP = "0.0.0.0"
def launchGeneticServer():
    gs = gameServer()
    route("/", "POST", ts.startGameWithGenome)
    BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
    run(host=gameServerIP, port=gameServerPort, quiet=True)

launchTrainingServer()