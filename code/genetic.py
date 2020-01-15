import json
import math
import os
import threading
import time
from collections import namedtuple
from copy import deepcopy
from threading import Thread
from time import sleep
from typing import Callable, Dict, List, Tuple

import numpy as np
from bottle import BaseRequest, post, request, route, run

import jsonlines
from fitnessServer import FitnessServer
from individual import Individual
from postprocessor import numPossibleActions
from preprocessor import inputVectorSize

genPath = "gens/"


class Population:
    @staticmethod
    def __createIndividual(lowerLimit, upperLimit, shape):
        return Individual(np.random.uniform(low=lowerLimit, high=upperLimit, size=shape))

    @staticmethod
    def __createPopulation(populationSize, lowerLimit, upperLimit, shape: Tuple[int, ...]):
        return [Population.__createIndividual(lowerLimit, upperLimit, shape) for i in range(populationSize)]

    @staticmethod
    def __rouletteSelect(population, cumulativeFitness):
        pick = np.random.uniform(0, cumulativeFitness)
        current = 0
        for individual in population:
            current += individual.fitness
            if current > pick:
                return individual

    @staticmethod
    def __tournamentSelect(population, tournamentSize, numSelect):
        competitorIndices = np.random.choice(len(population), tournamentSize)
        competitors = [population[i] for i in competitorIndices]
        competitors.sort(key=lambda x: x.fitness, reverse=True)
        winners = [competitors[i] for i in range(numSelect)]
        return winners

    @staticmethod
    def __cumulativeFitness(population):
        return sum(individual.fitness for individual in population)

    @staticmethod
    def __select(population, numSurvivors, elitism):
        """using roulette wheel selection"""
        elit = max(population, key=lambda x: x.fitness)
        cumulativeFitness = Population.__cumulativeFitness(population)
        survivors = [Population.__rouletteSelect(
            population, cumulativeFitness) for i in range(numSurvivors)]
        if elitism:
            bestSurvivor = max(survivors, key=lambda x: x.fitness)
            if bestSurvivor.fitness < elit.fitness:
                low = 0
                high = len(survivors) - 1
                rnd = 0 if low == high else np.random.randint(
                    low=low, high=high)
                del survivors[rnd]
                survivors.insert(0, elit)
        return survivors

    @staticmethod
    def __pair(population, numBabies, tournamentSize):
        """using tournament selection"""
        return [(Population.__tournamentSelect(population, tournamentSize, 2)) for i in range(numBabies)]

    @staticmethod
    def __mate(parentList):
        babies = []
        for father, mother in parentList:
            baby = Individual(np.empty(father.genome.shape))
            for i in range(baby.genome.shape[0]):
                choice = np.random.choice([False, True])
                baby.genome[i] = father.genome[i] if choice else mother.genome[i]
            babies.append(baby)
        return babies

    @staticmethod
    def __mutate(generation, lowerLimit, upperLimit, mutationRate, elitism):
        mutatedGeneration = deepcopy(generation)
        start = 0 if not elitism else 1
        for i in range(start, len(mutatedGeneration)):
            genome = mutatedGeneration[i].genome
            for j in range(genome.shape[0]):
                if np.random.choice([True, False], p=[mutationRate, 1-mutationRate]):
                    genome[j] = np.random.uniform(
                        low=lowerLimit, high=upperLimit, size=genome[j].shape)
        return mutatedGeneration

    def __init__(self, fitnessFunction: Callable, populationSize, lowerLimit, upperLimit, shape, tournamentSize,
                 selectionPressure=0.5, mutationRate=0.01, elitism=True, activePopulation=None, graveyard: List = []):
        # note: selection mechanism requires fitness >= 0
        self.fitnessFunction = fitnessFunction
        self.populationSize = populationSize
        self.lowerLimit = lowerLimit
        self.upperLimit = upperLimit
        self.shape = shape
        self.selectionPressure = selectionPressure
        self.tournamentSize = tournamentSize
        self.mutationRate = mutationRate
        self.elitism = elitism
        self.generation = 0
        self.activePopulation = activePopulation
        self.lastGeneration = None
        self.canEvolve = True

    def __cleanup(self):
        self.lastGeneration = deepcopy(self.activePopulation)
        self.lastGeneration.sort(key=lambda x: x.fitness, reverse=True)
        self.generation += 1
        self.canEvolve = True

    def __evaluateGeneration(self, callback):
        self.canEvolve = False
        self.fitnessFunction(self.activePopulation, callback)

    def __applyGeneticOperators(self):
        finalPopulationSize = len(self.activePopulation)
        numSurvivors = math.ceil(
            (1 - self.selectionPressure) * len(self.activePopulation))
        numBabies = finalPopulationSize - numSurvivors

        population = Population.__select(
            self.activePopulation, numSurvivors, self.elitism)
        parentList = Population.__pair(
            population, numBabies, self.tournamentSize)
        babies = Population.__mate(parentList)
        newGeneration = population
        newGeneration.extend(babies)
        newGeneration = Population.__mutate(
            newGeneration, self.lowerLimit, self.upperLimit, self.mutationRate, self.elitism)

        self.activePopulation = newGeneration

    def evolve(self):
        while not self.canEvolve:
            sleep(0.5)
        if self.activePopulation is None:
            self.activePopulation = Population.__createPopulation(
                self.populationSize, self.lowerLimit, self.upperLimit, self.shape)
        else:
            self.__applyGeneticOperators()
        self.__evaluateGeneration(callback=self.__cleanup)


def startEvolution():
    fs = FitnessServer()
    p = Population(fitnessFunction=lambda pop, callb: fs.evaluateGenomes(pop, callb), populationSize=10,
                   lowerLimit=-1, upperLimit=1, shape=(numPossibleActions, inputVectorSize), tournamentSize=7,
                   elitism=True, mutationRate=0.01, selectionPressure=0.5)

    for i in range(10):
        while not p.canEvolve:
            sleep(0.5)
        p.evolve()
        if p.lastGeneration:
            gen = p.generation
            fitnesses = [individual.fitness for individual in p.lastGeneration]
            minFitness = min(fitnesses)
            maxFitness = max(fitnesses)
            avgFitness = np.average(fitnesses)
            stdFitness = np.std(fitnesses)
            lastGenList = [
                {"genome": individual.genome.tolist(),
                 "fitness": individual.fitness}
                for individual in p.lastGeneration
            ]
            if not os.path.exists(genPath):
                os.makedirs(genPath)
            with jsonlines.open(genPath + "gen" + str(gen) + ".jsonl", mode="w") as writer:
                for individual in lastGenList:
                    writer.write(individual)
            print('gen:', str(gen) + ',', 'min:', str(minFitness) + ',', 'max:', str(maxFitness) + ',',
                  'average:', str(avgFitness) + ',', 'standard deviation:', str(stdFitness))


@post("/main")
def main():
    thread = Thread(target=startEvolution)
    thread.start()
    return "main"


BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
run(host=FitnessServer.geneticServerIP,
    port=FitnessServer.geneticServerPort, quiet=True)
