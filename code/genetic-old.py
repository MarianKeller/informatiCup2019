import math
import threading
import time
from collections import namedtuple
from copy import deepcopy
from typing import Callable, Dict, List, Tuple

import numpy as np

from fitnessServer import FitnessServer
from bottle import BaseRequest, post, request, route, run

from preprocessor import inputVectorSize
from postprocessor import numPossibleActions


class Population:
    @staticmethod
    def __createIndividual(lowerLimit, upperLimit, shape):
        return np.random.uniform(low=lowerLimit, high=upperLimit, size=shape)

    @staticmethod
    def __createPopulation(populationSize, lowerLimit, upperLimit, shape: Tuple[int, ...]):
        return [Population.__createIndividual(lowerLimit, upperLimit, shape) for i in range(populationSize)]

    @staticmethod
    def __rate(fitnessFunction, generation):
        # TODO make class; directly call fitness function that rates whole generation at once by updating the RatedIndividual class if fitness == None
        RatedIndividual = namedtuple(
            'RatedIndividual', ['fitness', 'genes'])
        fitnesses = fitnessFunction(generation)
        return [RatedIndividual(individual[0], individual[1]) for individual in zip(fitnesses, generation)]

    @staticmethod
    def __unrate(ratedGeneration):
        return [individual.genes for individual in ratedGeneration]

    @staticmethod
    def __rouletteSelect(ratedGeneration, cumulativeFitness):
        pick = np.random.uniform(0, cumulativeFitness)
        current = 0
        for individual in ratedGeneration:
            current += individual.fitness
            if current > pick:
                return individual

    @staticmethod
    def __cumulativeFitness(ratedGeneration):
        return sum(individual.fitness for individual in ratedGeneration)

    @staticmethod
    def __select(ratedGeneration, numSurvivors, elitism):
        """using roulette wheel selection"""
        cumulativeFitness = Population.__cumulativeFitness(ratedGeneration)
        survivors = [Population.__rouletteSelect(
            ratedGeneration, cumulativeFitness) for i in range(numSurvivors)]
        survivors.sort(key=lambda x: x.fitness, reverse=True)
        if elitism:
            elit = ratedGeneration[0]
            if survivors[0].fitness != elit.fitness:
                low = 0
                high = len(survivors)-1
                rnd = 0 if low == high else np.random.randint(
                    low=low, high=high)
                survivors[rnd] = elit
                # TODO do not sort again, just remove survivors[rnd] and insert elit at beginning of list
                survivors.sort(key=lambda x: x.fitness, reverse=True)
        return survivors

    @staticmethod
    def __pair(ratedGeneration, numBabies):
        """using roulette wheel selection"""
        # TODO use tournament selection; introduce self.tournamentSize member
        cumulativeFitness = Population.__cumulativeFitness(ratedGeneration)
        return [(Population.__rouletteSelect(ratedGeneration, cumulativeFitness), Population.__rouletteSelect(ratedGeneration, cumulativeFitness)) for i in range(numBabies)]

    @staticmethod
    def __mate(parentList):
        babies = []
        for father, mother in parentList:
            baby = np.empty(father.genes.shaprintpe)
            for i in range(baby.shape[0]):
                choice = np.random.choice([False, True])
                baby[i] = father.genes[i] if choice else mother.genes[i]
            babies.append(baby)
        return babies

    @staticmethod
    def __mutate(generation, lowerLimit, upperLimit, mutationRate, elitism):
        mutatedGeneration = deepcopy(generation)
        start = 0 if not elitism else 1
        for i in range(start, len(mutatedGeneration)):
            genes = mutatedGeneration[i]
            for j in range(genes.shape[0]):
                if np.random.choice([True, False], p=[mutationRate, 1-mutationRate]):
                    genes[j] = np.random.uniform(
                        low=lowerLimit, high=upperLimit, size=genes[j].shape)
        return mutatedGeneration

    def __init__(self, fitnessFunction: Callable, populationSize, lowerLimit, upperLimit, shape,
                 selectionPressure=0.5, mutationRate=0.01, elitism=True, activePopulation=None, graveyard: List = []):
        # note: selection mechanism requires fitness >= 0
        self.fitnessFunction = fitnessFunction
        self.populationSize = populationSize
        self.lowerLimit = lowerLimit
        self.upperLimit = upperLimit
        self.shape = shape
        self.selectionPressure = selectionPressure
        self.mutationRate = mutationRate
        self.elitism = elitism
        self.generation = 0
        self.activePopulation = activePopulation
        # TODO stream graveyard to a file and make lastGeneration field
        self.graveyard = graveyard
        self.__evolve = True

    def nextGeneration(self):
        self.generation += 1
        finalPopulationSize = len(self.activePopulation)
        numSurvivors = math.ceil(
            (1 - self.selectionPressure) * len(self.activePopulation))
        numBabies = finalPopulationSize - numSurvivors

        ratedGeneration = Population.__rate(
            self.fitnessFunction, self.activePopulation)
        ratedGeneration.sort(key=lambda x: x.fitness, reverse=True)
        oldGeneration = deepcopy(ratedGeneration)
        self.graveyard.append(oldGeneration)

        ratedGeneration = Population.__select(
            ratedGeneration, numSurvivors, self.elitism)
        parentList = Population.__pair(ratedGeneration, numBabies)
        babies = Population.__mate(parentList)
        newGeneration = Population.__unrate(ratedGeneration)
        newGeneration.extend(babies)
        newGeneration = Population.__mutate(
            newGeneration, self.lowerLimit, self.upperLimit, self.mutationRate, self.elitism)

        self.activePopulation = newGeneration

    def __startEvolution(self):
        if self.activePopulation is None:
            self.activePopulation = Population.__createPopulation(
                self.populationSize, self.lowerLimit, self.upperLimit, self.shape)
        while(self.__evolve):
            self.nextGeneration()

    def startEvolution(self):
        self.__evolve = True
        thread = threading.Thread(target=self.__startEvolution)
        thread.start()

    def haltEvolution(self):
        self.__evolve = False

fs = FitnessServer()

BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
run(host=FitnessServer.geneticServerIP,
    port=FitnessServer.geneticServerPort, quiet=True)

p = Population(fitnessFunction=lambda x: fs.getSyncFitnessList(x), populationSize=100,
               lowerLimit=-1, upperLimit=1, shape=(numPossibleActions, inputVectorSize), elitism=True, mutationRate=0.01, selectionPressure=0.5)
p.startEvolution()
# TODO
# while(len(p.graveyard) < 1000):
#     time.sleep(1)
# p.haltEvolution()
# print(p.graveyard[-1][0].fitness)
