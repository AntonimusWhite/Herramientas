import math
import random


# 1. generacion indivisuos
def generate_individual_bitstring(size): #onemax
    individuo = []
    for i in range(size):
        gen = random.randint(0, 1)
        individuo.append(gen)
    return individuo

def generate_individual_permutation(size): #tsp
    individuo = list(range(size))
    random.shuffle(individuo)
    return individuo

#Generacion poblaciones
def generate_population(population_size, individual_generator, size):
    poblacion = []
    for i in range(population_size):
        individuo = individual_generator(size)
        poblacion.append(individuo)
    return poblacion

# 2. funciones fitness
# Calculamos el FITNESS ONEMAX de cada individuo, maximizar los unos
def fitness_onemax(individual):
    fitness = 0
    for genes in individual: #para cada gen en individual
        fitness = fitness + genes #sumo cada gen al fitness.
    return fitness

# fitness tsp
#distances ya no es una variable global por lo que hay que llamarla
def tsp_distance(route, distances):
    suma_total = 0
    for i in range(len(route)):
        suma_total = distances[route[i]][route[(i+1)%len(route)]] + suma_total
    return suma_total

def fitness_tsp(route, distances):
    suma_total = tsp_distance(route, distances)
    return 1/suma_total

# 3. cruce
# punto donde se cruzan dos individuos
def generate_cut_point(gene_length):
    return random.randint(2, gene_length-2)

# Cruce de un punto para individuos OneMax
def crossover_bitstring(parent1, parent2):
    gene_length = len(parent1)
    puntocruce = generate_cut_point(gene_length)
    child1 = parent1[:puntocruce] + parent2[puntocruce:]
    child2 = parent2[:puntocruce] + parent1[puntocruce:]
    return child1, child2

# Obtiene las ciudades que faltan sin repetir las del segmento fijo
def fill_remaining_in_order(fixed_segment, source_parent):
    lista = []
    for i in range(len(source_parent)):
        if source_parent[i] not in fixed_segment:
            lista.append(source_parent[i])
    return lista

# Cruce de permutaciones para TSP
def crossover_permutation(parent1, parent2):
    gene_length = len(parent1)
    punto = generate_cut_point(gene_length)

    # Conservamos una parte de cada padre y completamos con las ciudades restantes
    child1 = parent1[:punto] + fill_remaining_in_order(parent1[:punto], parent2)
    child2 = parent2[:punto] + fill_remaining_in_order(parent2[:punto], parent1)
    return child1, child2

# 4. mutaciones
# OneMax cambiar de 0 a 1 o viceversa
def mutate_bitstring(individual, mutation_rate):
    for gen in range(len(individual)):
        if random.random() < mutation_rate:
            if individual[gen] == 0:
                individual[gen] = 1
            else:
                individual[gen] = 0
    return individual

# TSP intercambia dos ciudades de la ruta
def swap_mutation(individual, mutation_rate):
    #posiciones de individual
    if random.random() < mutation_rate:
        posicion1 = random.randint(0, len(individual)-1)
        posicion2 = random.randint(0, len(individual)-1)
        while posicion1 == posicion2:
            posicion2 = random.randint(0, len(individual)-1)
        individual[posicion1], individual[posicion2] = individual[posicion2], individual[posicion1]
    return individual

# 5. seleccion mejor individuo
def crearmatingpool(population, fitnesses):
    mating_pool = []
    repeticion =0
    while repeticion <2: #repetir dos veces
        #creo lista desde 0 hasta population size -1
        lista = list(range(len(population)))
        random.shuffle(lista) #barajar 
        #recorrer la lista en pares
        for i in range(0, len(lista), 2):
            posicion = lista[i] #me guardo la posicion del primer individuo
            posicion2 = lista[i+1] #posicion del segundo individuo
            #comparo los fitnesses de cada pareja
            if fitnesses[posicion] >= fitnesses[posicion2]:
                mating_pool.append(population[posicion]) #population tiene a los individuos
            else:
                mating_pool.append(population[posicion2])
        repeticion = repeticion +1
    return mating_pool

# Obtiene el mejor individuo de una población y su fitness
def mejor_individuo(population, fitnesses):
    mejor_fitness = max(fitnesses)
    posicion = fitnesses.index(mejor_fitness)
    mejor_individual = population[posicion]
    return mejor_individual, mejor_fitness

