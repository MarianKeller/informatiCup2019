import json
from bottle import BaseRequest, post, request, run, route
import requests

geneticServerPort = 50124
geneticServerUrl = "http://localhost:50124"
geneticServerIP = "0.0.0.0"


class geneticServer(object):
    def launchCallbackServer(self, path):
        route(path, "POST", ts.startGameWithGenome)


    def evaluateGenome(self, genome, genomeId):
        pass

    def newTrainingCampaign(self):
        pass

BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
run(host=gameServerIP, port=gameServerPort, quiet=True)