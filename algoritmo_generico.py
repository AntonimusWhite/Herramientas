###############
# EJERCICIO 6 #
###############
def distancias_coordenadas(coordenadas):
    distancias = []
    for i in range(len(coordenadas)):
        fila = []
        for j in range(len(coordenadas)):
            x1, y1 = coordenadas[i]
            x2, y2 = coordenadas[j]
            distancia = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            fila.append(distancia)
        distancias.append(fila)

    return distancias

###############
# EJERCICIO 1 #
###############
import math
import random
import time

def generate_individual_bitstring(size):
    individual= []
    while size > 0:
        n_aleatorio = random.randint(0,1)
        individual.append(n_aleatorio)
        size -= 1
    return individual

def generate_individual_permutation(size):
    lista_pos = [i for i in range(size)]
    random.shuffle(lista_pos)
    return lista_pos

def generate_population(population_size, individual_generator_size, size):
    poblacion = []
    for _ in range(population_size):
        individual = individual_generator_size(size)
        poblacion.append(individual)
    return poblacion

###############
# EJERCICIO 2 #
###############
def tsp_distance(route, distances):
    suma_total = 0
    for i in range(len(route)):
        suma_total = distances[route[i]][route[(i+1)%len(route)]] + suma_total

    return suma_total

def fitness_tsp(route,distances):
    suma_total = tsp_distance(route,distances)

    return 1/suma_total

###############
# EJERCICIO 3 #
###############
def generate_cut_point(gene_length):
    aleatorio = random.randint(2, gene_length-2)
    return aleatorio

def fill_remaining_in_order(fixed_segment, source_parent):
    lista_nueva = []
    i=0
    while (len(fixed_segment)<len(source_parent)) and i<len(source_parent):
        if source_parent[i] not in fixed_segment:
            lista_nueva.append(source_parent[i])
            i+=1
        else: 
            i+=1
    return lista_nueva

def crossover_bitstring(parent1, parent2):
    cruce = generate_cut_point(len(parent1))
    child1 = parent1[:cruce] + parent2[cruce:]
    child2 = parent2[:cruce] + parent1[cruce:]
    return child1,child2


def crossover_permutation(parent1, parent2):
    cruce = generate_cut_point(len(parent1))
    l1= fill_remaining_in_order(parent1[:cruce], parent2)
    l2= fill_remaining_in_order(parent2[:cruce], parent1)
    child1 = parent1[:cruce] + l1
    child2  = parent2[:cruce] + l2
    return child1, child2

###############
# EJERCICIO 4 #
###############
def mutate_bitstring(individual, mutation_rate):
    for i in range(len(individual)):
        if random.random() < mutation_rate:
            if individual[i]==0:
                individual[i]=1
            else:
                individual[i]=0
    return individual


def swap_mutation(individual, mutation_rate): 
    x = random.random()
    if x < mutation_rate:
        pos1 = random.randint(0,len(individual)-1)
        pos2 = random.randint(0,len(individual)-1)
        while pos2==pos1:
            pos2 = random.randint(0,len(individual)-1)
        individual[pos1],individual[pos2] = individual[pos2],individual[pos1]
    return individual

###############
# EJERCICIO 5 #
###############
def fitness_onemax(individuo,distances):
    contador=0
    for i in individuo:
        if i==1:
            contador+=1
    return contador

def obtener_fitnesses(poblacion):
    fitnesses = []
    for indiv in poblacion:
        fitness= fitness_onemax(indiv,None)
        fitnesses.append(fitness)
    return fitnesses

def mating_pool_poblacion(poblacion, fitnesses):
    mating_pool = []
    for _ in range(2):
        lista_vacia = []
        for i in range(len(poblacion)):
            lista_vacia.append(i)
        random.shuffle(lista_vacia)
        for i in range(0,len(lista_vacia)-1,2):
            pos1 = lista_vacia[i]
            pos2 = lista_vacia[i+1]
            if fitnesses[pos1] > fitnesses[pos2]:
                mating_pool.append(poblacion[pos1])
            else:
                mating_pool.append(poblacion[pos2])
    return mating_pool

def run_genetic_algorithm(population_size, individual_size, num_generations, mutation_rate, individual_generator, fitness_function, crossover_function, mutation_function):
    poblacion = generate_population(population_size, individual_generator, individual_size)
    distances = distancias_coordenadas(poblacion)
    j = 0
    while j < num_generations:
        fitnesses = [fitness_function(individual,distances) for individual in poblacion]
        mating_pool_nueva = mating_pool_poblacion(poblacion, fitnesses)
        new_population = []
        for i in range(0,len(mating_pool_nueva)-1,2):
            cross1, cross2 = crossover_function(mating_pool_nueva[i],mating_pool_nueva[i+1])
            new_population.append(cross1)
            new_population.append(cross2)
        new_population = [mutation_function(individual,mutation_rate) for individual in new_population]
        poblacion = new_population
        j += 1

    fitnesses = [fitness_function(individual,distances) for individual in poblacion]
    best_index = fitnesses.index(max(fitnesses))
    best_individual = poblacion[best_index]
    best_fitness = fitnesses[best_index]

    return best_individual, best_fitness