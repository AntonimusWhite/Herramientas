import math
import random
import time

# 1. generacion indivisuos
def generate_individual_bitstring(size): #onemax
    individuo = [random.randint(0, 1) for _ in range(size)]
    return individuo

def generate_individual_permutation(size): #tsp
    individuo = list(range(size))
    random.shuffle(individuo)
    return individuo

#Generacion poblaciones
def generate_population(population_size, individual_generator, size):
    poblacion = [individual_generator(size) for _ in range(population_size)]
    return poblacion

# 2. funciones fitness
# Calculamos el FITNESS ONEMAX de cada individuo, maximizar los unos
def fitness_onemax(individual):
    fitness = sum(individual)
    return fitness

# fitness tsp
#distances ya no es una variable global por lo que hay que llamarla
def tsp_distance(route, distances):
    suma_total = sum(distances[route[i]][route[(i+1)%len(route)]] for i in range(len(route)))
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
    lista = [source_parent[i] for i in range(len(source_parent)) if source_parent[i] not in fixed_segment]
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

# 6.

# Comprueba si se ha alcanzado el óptimo conocido
def optimo_alcanzado(mejor_fitness, optimo_conocido, tipo):
    if optimo_conocido is None:
        return False

    if tipo == "onemax":
        return mejor_fitness >= optimo_conocido
    elif tipo == "tsp":
        # óptimo conocido representa la distancia mínima
        if mejor_fitness == float("inf"):
            distancia = 0
        else:
            distancia = 1 / mejor_fitness
        return distancia <= optimo_conocido
    return False

def run_genetic_algorithm(population_size, individual_size, num_generations, mutation_rate, individual_generator, fitness_function, 
                          crossover_function, mutation_function, optimo_conocido=None, tipo=None, *args):
    
    # Iniciamos el cronómetro
    inicio = time.perf_counter()
    tiempo_optimo = None

    population = generate_population(population_size, individual_generator, individual_size) #fun del ej 1

    fitnesses = [fitness_function(individual, *args) for individual in population] #calcular fitnesses iniciales

    #guardamos el mejor individuo inicial de la poblacion y el fitness
    mejor_individual_global, mejor_fitness_global = mejor_individuo(population, fitnesses)
    mejor_individual_global = mejor_individual_global.copy()

    # Comprobamos si el óptimo está en la población inicial
    if optimo_alcanzado(mejor_fitness_global, optimo_conocido, tipo):
        tiempo_optimo = time.perf_counter() - inicio
        tiempo_total = time.perf_counter() - inicio
        return mejor_individual_global, mejor_fitness_global, tiempo_total, tiempo_optimo

    #Repetir durante num_generations generaciones
    for generacion in range(num_generations):
        #creo padres
        mating_pool = crearmatingpool(population, fitnesses)

        # conservamos el mejor individuo de la poblacion inicial
        elite, fitness_elite = mejor_individuo(population, fitnesses)
        elite = elite.copy()

        #Cruzar padres y generar hijos, ejercicio 3 lab03
        new_population = []
        for i in range(0, len(mating_pool)-1, 2): #gestionar poblacion impar
            parent1 = mating_pool[i]
            parent2 = mating_pool[i+1]
            child1, child2 = crossover_function(parent1, parent2)
            new_population.append(child1)
            new_population.append(child2)

        # Si la población es impar, conservamos un padre sin cruzarlo
        if len(mating_pool) % 2 != 0:
            new_population.append(mating_pool[-1].copy())

        # Mutar hijos
        for individual in new_population:
            mutation_function(individual, mutation_rate)

        #introducimos el mejor individuo sin mutarlo
        new_population[0] = elite

        # Sustituir población anterior por la nueva
        population = new_population

        #Calcular los nuevos fitnesses y actualizar el mejor individuo
        fitnesses = [fitness_function(individual, *args) for individual in population]

        mejor_individual, mejor_fitness = mejor_individuo(population, fitnesses)

        if mejor_fitness > mejor_fitness_global:
            mejor_fitness_global = mejor_fitness
            mejor_individual_global = mejor_individual.copy()

        # Comprobamos si hemos alcanzado el óptimo conocido
        if optimo_alcanzado(mejor_fitness_global, optimo_conocido, tipo):
            tiempo_optimo = time.perf_counter() - inicio
            break

    tiempo_total = time.perf_counter() - inicio #tiempo total d ela ejecucion

    return mejor_individual_global, mejor_fitness_global, tiempo_total, tiempo_optimo