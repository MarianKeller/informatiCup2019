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
from time import sleep

from individual import Individual


class Population:
    @staticmethod
    def __createIndividual(lowerLimit, upperLimit, shape):
        return Individual(np.random.uniform(low=lowerLimit, high=upperLimit, size=shape))

    @staticmethod
    def __createPopulation(populationSize, lowerLimit, upperLimit, shape: Tuple[int, ...]):
        return [Population.__createIndividual(lowerLimit, upperLimit, shape) for i in range(populationSize)]

    # TODO delete
    # @staticmethod
    def __rate(fitnessFunction, generation):
        pass
        # fitnesses = fitnessFunction(generation)
        # return [RatedIndividual(individual[0], individual[1]) for individual in zip(fitnesses, generation)]

        # TODO delete
        # @staticmethod
        # def __unrate(ratedGeneration):
        #     return [individual.genes for individual in ratedGeneration]

    @staticmethod
    def __rouletteSelect(population, cumulativeFitness):
        pick = np.random.uniform(0, cumulativeFitness)
        current = 0
        for individual in population:
            current += individual.fitness
            if current > pick:
                return individual

    @staticmethod
    def __cumulativeFitness(population):
        return sum(individual.fitness for individual in population)

    @staticmethod
    def __select(population, numSurvivors, elitism):
        """using roulette wheel selection"""
        cumulativeFitness = Population.__cumulativeFitness(population)
        survivors = [Population.__rouletteSelect(
            population, cumulativeFitness) for i in range(numSurvivors)]
        survivors.sort(key=lambda x: x.fitness, reverse=True)
        if elitism:
            elit = population[0]
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
    def __pair(population, numBabies):
        """using roulette wheel selection"""
        # TODO use tournament selection; introduce self.tournamentSize member
        cumulativeFitness = Population.__cumulativeFitness(population)
        return [(Population.__rouletteSelect(population, cumulativeFitness), Population.__rouletteSelect(population, cumulativeFitness)) for i in range(numBabies)]

    @staticmethod
    def __mate(parentList):
        babies = []
        for father, mother in parentList:
            baby = Individual(np.empty(father.genes.shape))
            for i in range(baby.shape[0]):
                choice = np.random.choice([False, True])
                baby.genome[i] = father.genome[i] if choice else mother.genome[i]
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
        self.lastGeneration = None

    def __cleanup(self):
        self.activePopulation.sort(key=lambda x: x.fitness, reverse=True)
        self.generation += 1
        self.lastGeneration = copy.deepcopy(self.activePopulation)

    def __evaluateGeneration(self, callback):
        self.fitnessFunction(self.activePopulation, callback=callback)

    def __applyGeneticOperators(self):
        finalPopulationSize = len(self.activePopulation)
        numSurvivors = math.ceil(
            (1 - self.selectionPressure) * len(self.activePopulation))
        numBabies = finalPopulationSize - numSurvivors

        population = Population.__select(
            self.activePopulation, numSurvivors, self.elitism)
        parentList = Population.__pair(population, numBabies)
        babies = Population.__mate(parentList)
        newGeneration.extend(babies)
        newGeneration = Population.__mutate(
            newGeneration, self.lowerLimit, self.upperLimit, self.mutationRate, self.elitism)

        self.activePopulation = newGeneration

    def evolve(self):
        if self.activePopulation is None:
            self.activePopulation = Population.__createPopulation(
                self.populationSize, self.lowerLimit, self.upperLimit, self.shape)
        else:
            self.__applyGeneticOperators()
        self.__evaluateGeneration(callback=__cleanup)


fs = FitnessServer()

BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
run(host=FitnessServer.geneticServerIP,
    port=FitnessServer.geneticServerPort, quiet=True)

p = Population(fitnessFunction=lambda x: fs.getAsyncFitnessList(x), populationSize=100,
               lowerLimit=-1, upperLimit=1, shape=(numPossibleActions, inputVectorSize), elitism=True, mutationRate=0.01, selectionPressure=0.5)

for i in range(2):
    p.evolve()
