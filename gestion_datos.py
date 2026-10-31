import math

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
