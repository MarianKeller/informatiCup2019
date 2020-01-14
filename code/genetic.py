# This file contains code from the DEAP examples written by De Rainville et al.
import random
import numpy

import fitnessServer

from bottle import BaseRequest, post, request, route, run

from deap import base
from deap import creator
from deap import tools


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", numpy.ndarray, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# Attribute generator
#                      define 'attr_bool' to be an attribute ('gene')
#                      which corresponds to floats sampled uniformly
#                      from the range [0,1] 
toolbox.register("attr_float", random.rand, 0, 1)
#numpy.random.rand(12, 31),

# Structure initializers
#                         define 'individual' to be an individual
#                         consisting of random n x m array
toolbox.register("individual", numpy.random.rand, 12, 31) # TODO: change matrix dimensions to correct ones


# define the population to be a list of individuals
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


# the goal ('fitness') function to be maximized
def evalOneMax(population):
    fs = fitnessServer()
    return fs.getSyncFitnessList(population)


# ----------
# Operator registration
# ----------
# register the goal / fitness function
toolbox.register("evaluate", evalOneMax)


# register the crossover operator
toolbox.register("mate", tools.cxTwoPoint)


# register a mutation operator with a probability to
# flip each attribute/gene of 0.05
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)


# operator for selecting individuals for breeding the next
# generation: each individual of the current generation
# is replaced by the 'fittest' (best) of three individuals
# drawn randomly from the current generation.
toolbox.register("select", tools.selTournament, tournsize=3)


# ----------
def main():
    BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
    run(host=fitnessServer.geneticServerIP, port=fitnessServer.geneticServerPort, quiet=True)
    #random.seed()

    # create an initial population of 100 individuals (where
    # each individual is a list of nparrays)
    pop = toolbox.population(n=100)

    # CXPB  is the probability with which two individuals
    #       are crossed
    #
    # MUTPB is the probability for mutating an individual

    CXPB, MUTPB = 0.5, 0.2

    print("Start of evolution")

    # Evaluate the entire population
    fitnesses = evalOneMax(pop)
    #fitnesses = list(map(toolbox.evaluate, pop))

    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    print("  Evaluated %i individuals" % len(pop))

    # Extracting all the fitnesses of

    fits = [ind.fitness.values[0] for ind in pop]

    # Variable keeping track of the number of generations

    g = 0

    # Begin the evolution
    while max(fits) < 100 and g < 1000:

        # A new generation
        g = g + 1
        print("-- Generation %i --" % g)
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))
        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            # cross two individuals with probability CXPB
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                # fitness values of the children
                # must be recalculated later
                del child1.fitness.values
                del child2.fitness.values
        for mutant in offspring:

            # mutate an individual with probability MUTPB

            if random.random() < MUTPB:

                toolbox.mutate(mutant)

                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]

        fitnesses = map(toolbox.evaluate, invalid_ind)

        for ind, fit in zip(invalid_ind, fitnesses):

            ind.fitness.values = fit

        print("  Evaluated %i individuals" % len(invalid_ind))

        # The population is entirely replaced by the offspring

        pop[:] = offspring

        # Gather all the fitnesses in one list and print the stats

        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)

        mean = sum(fits) / length

        sum2 = sum(x*x for x in fits)

        std = abs(sum2 / length - mean**2)**0.5

        print("  Min %s" % min(fits))

        print("  Max %s" % max(fits))

        print("  Avg %s" % mean)

        print("  Std %s" % std)

    print("-- End of (successful) evolution --")

    best_ind = tools.selBest(pop, 1)[0]

    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))


main()
