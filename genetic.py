import threading
import time
from collections import namedtuple
from copy import deepcopy
from typing import Callable, Dict, List, Tuple
import math

import numpy as np


class Population:
    @staticmethod
    def __createIndividual(lowerLimit, upperLimit, shape):
        return np.random.uniform(low=lowerLimit, high=upperLimit, size=shape)

    @staticmethod
    def __createPopulation(populationSize, lowerLimit, upperLimit, shape: Tuple[int, ...]):
        return [Population.__createIndividual(lowerLimit, upperLimit, shape) for i in range(populationSize)]

    @staticmethod
    def __rate(fitnessFunction, generation):
        RatedIndividual = namedtuple(
            'RatedIndividual', ['fitness', 'genes'])
        return [RatedIndividual(fitnessFunction(individual), individual) for individual in generation]

    @staticmethod
    def __unrate(ratedGeneration):
        return [individual.genes for individual in ratedGeneration]

    @staticmethod
    def __array_in(arr, list_of_arr):
        for elem in list_of_arr:
            if np.array_equal(arr, elem):
                return True
        return False

    @staticmethod
    def __select(ratedGeneration, numSurvivors, elitism):
        """using roulette wheel selection"""
        cumulativeFitness = sum(
            individual.fitness for individual in ratedGeneration)
        wheel = [individual.fitness /
                 cumulativeFitness for individual in ratedGeneration]

        survivorIndices = np.random.choice(
            len(ratedGeneration), size=numSurvivors, p=wheel)
        survivors = [ratedGeneration[i] for i in survivorIndices]

        if elitism:
            elit = ratedGeneration[0]
            if not Population.__array_in(elit, survivors):
                low = 0
                high = len(survivors)-1
                rnd = 0 if low == high else np.random.randint(
                    low=low, high=high)
                survivors[rnd] = elit
        survivors.sort(key=lambda x: x.fitness, reverse=True)
        return list(survivors)

    @staticmethod
    def __pair(ratedGeneration, numBabies):
        """using roulette wheel selection"""
        cumulativeFitness = sum(
            individual.fitness for individual in ratedGeneration)
        wheel = [individual.fitness /
                 cumulativeFitness for individual in ratedGeneration]
        fatherIndices = np.random.choice(
            len(ratedGeneration), size=numBabies, p=wheel)
        motherIndices = np.random.choice(
            len(ratedGeneration), size=numBabies, p=wheel)
        return [(ratedGeneration[fatherIndices[i]], ratedGeneration[motherIndices[i]]) for i in range(numBabies)]

    @staticmethod
    def __mate(parentList):
        babies = []
        for father, mother in parentList:
            baby = np.empty(father.genes.shape)
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
                 selectionPressure=0.5, mutationRate=0.01, elitism=True, curGeneration=None, graveyard: List = []):
        # note: selection mechanism requires fitness >= 0
        self.fitnessFunction = fitnessFunction
        self.populationSize = populationSize
        self.lowerLimit = lowerLimit
        self.upperLimit = upperLimit
        self.shape = shape
        self.selectionPressure = selectionPressure
        self.mutationRate = mutationRate
        self.elitism = elitism
        self.curGeneration = curGeneration
        self.graveyard = graveyard
        self.__evolve = True

    def nextGeneration(self):
        finalPopulationSize = len(self.curGeneration)
        numSurvivors = math.ceil(
            (1 - self.selectionPressure) * len(self.curGeneration))
        numBabies = finalPopulationSize - numSurvivors

        ratedGeneration = Population.__rate(
            self.fitnessFunction, self.curGeneration)
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

        self.curGeneration = newGeneration

    def __startEvolution(self):
        if self.curGeneration == None:
            self.curGeneration = Population.__createPopulation(
                self.populationSize, self.lowerLimit, self.upperLimit, self.shape)
        while(self.__evolve):
            self.nextGeneration()

    def startEvolution(self):
        self.__evolve = True
        thread = threading.Thread(target=self.__startEvolution)
        thread.start()

    def haltEvolution(self):
        self.__evolve = False


p = Population(fitnessFunction=lambda x: sum(map(sum, x)), populationSize=100,
               lowerLimit=0, upperLimit=1000, shape=(10,10), elitism=True, selectionPressure=0.5, mutationRate=0.01)
p.startEvolution()
time.sleep(60)
p.haltEvolution()
print(p.graveyard[0][0])
print(p.graveyard[-1][0])
