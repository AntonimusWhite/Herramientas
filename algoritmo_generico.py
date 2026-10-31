import math
import random


# generacion indivisuos
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

# Calculamos el FITNESS ONEMAX de cada individuo, maximizar los unos
def fitness_onemax(individual):
    fitness = 0
    for genes in individual: #para cada gen en individual
        fitness = fitness + genes #sumo cada gen al fitness.
    return fitness

#FITNESS TSP
# matriz de distancias a partir de las coordenadas
def calcular_matriz_distancias(coordinates):
    distances = []
    for ciudad1 in coordinates: #recorre ciudades
        fila = []
        for ciudad2 in coordinates: #comparar las ciidades entre ellas
            x1, y1 = ciudad1
            x2, y2 = ciudad2
            distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2) #calcular distancia entre ciudades
            fila.append(distancia)
        distances.append(fila)
    return distances

#distances ya no es una variable global por lo que hay que llamarla
def tsp_distance(route, distances):
    suma_total = 0
    for i in range(len(route)):
        suma_total = distances[route[i]][route[(i+1)%len(route)]] + suma_total
    return suma_total

def fitness_tsp(route, distances):
    suma_total = tsp_distance(route, distances)
    return 1/suma_total