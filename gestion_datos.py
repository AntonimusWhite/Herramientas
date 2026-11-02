import json
import math
import multiprocessing
import os
import time
import matplotlib
import matplotlib.pyplot as plt

from algoritmo_generico import (
    crossover_bitstring,
    crossover_permutation,
    fitness_onemax,
    fitness_tsp,
    generate_individual_bitstring,
    generate_individual_permutation,
    mutate_bitstring,
    run_genetic_algorithm,
    swap_mutation,
)


##########
# PASO 1 #
##########
# El diccionario "estado" lo crea main (crear_estado). Estas funciones lo reciben
# por argumento y usan sus claves: archivo, ejecuciones, historial, config_salida,
# num_nucleos y tiempo_total.
def segundos_a_hms(segundos):
    # Convierte segundos a horas, minutos y segundos.
    horas, resto = divmod(segundos, 3600)
    minutos, seg = divmod(resto, 60)
    return {"horas": int(horas), "minutos": int(minutos), "segundos": seg}

def config_sin_matriz(ejecucion):
    # Copia de la ejecución sin la matriz de distancias (es enorme y no hace falta guardarla).
    copia = ejecucion.copy()
    copia.pop("matriz_distancias", None)   # la quita si existe (solo en TSP)
    return copia


###################
# LECTURA JSON    #
###################
def cargar_json(ruta):
    # Lee un archivo JSON. Si no existe o está mal formado, lanza ValueError.
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except FileNotFoundError:
        raise ValueError(f"No se encuentra el archivo '{ruta}'.")
    except json.JSONDecodeError as error:
        raise ValueError(f"El archivo no es un JSON válido: {error}.")
    except OSError as error:
        raise ValueError(f"No se pudo leer el archivo '{ruta}': {error}.")
    return datos

def normalizar_problemas(problemas):
    #Devuelve siempre una lista de problemas (dict -> [dict], None -> []).
    if problemas is None:
        return []
    if isinstance(problemas, dict):
        problemas = [problemas]
    if not isinstance(problemas, list) or not all(isinstance(p, dict) for p in problemas):
        raise ValueError("Los problemas deben ser un objeto JSON o una lista de objetos JSON.")
    return problemas


def agrupar_problemas(datos):
    """Devuelve los problemas del archivo como una lista de pares (tipo, problema).
    Admite problemas_onemax / problemas_tsp (objeto o lista) y también un problema
    suelto en la raíz con "tipo": "onemax" o "tsp", que se añade a la misma lista."""

    if not isinstance(datos, dict):
        raise ValueError("El archivo debe contener un objeto JSON en la raíz.")

    problemas = [("onemax", p) for p in normalizar_problemas(datos.get("problemas_onemax"))]
    problemas += [("tsp", p) for p in normalizar_problemas(datos.get("problemas_tsp"))]

    if "tipo" in datos:
        tipo = datos["tipo"]
        if tipo not in ("onemax", "tsp"):
            raise ValueError(f"Tipo de problema desconocido: {tipo!r} (debe ser 'onemax' o 'tsp').")

        # El problema suelto son las claves de la raíz que no son de configuración general
        generales = ("tipo", "problemas_onemax", "problemas_tsp", "salida", "output", "num_nucleos")
        suelto = {clave: valor for clave, valor in datos.items() if clave not in generales}
        problemas.append((tipo, suelto))

    elif "tamano_poblacion" in datos or "longitud_gen" in datos or "ciudades" in datos:
        raise ValueError("El archivo parece describir un problema suelto, pero falta el campo 'tipo' ('onemax' o 'tsp').")

    if not problemas:
        raise ValueError("El archivo no contiene ningún problema: falta 'problemas_onemax', 'problemas_tsp' o un problema con 'tipo'")

    return problemas

###################
# VALIDACIÓN      #
###################
def es_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)

def como_lista(valor):
    # Si el valor no es una lista, lo mete en una lista de un elemento (20 -> [20]).
    if isinstance(valor, list):
        return valor
    return [valor]

def validar_problema(problema, tipo, nombre):
    # Comprueba lo imprescindible para que el motor no falle.
    for clave in ("tamano_poblacion", "num_generaciones", "tasa_mutacion"):
        if clave not in problema:
            raise ValueError(f"{nombre}: falta '{clave}'.")

    # Cada hiperparámetro puede ser un valor o una lista de valores (rejilla)
    for poblacion in como_lista(problema["tamano_poblacion"]):
        if not isinstance(poblacion, int) or poblacion < 2 or poblacion % 2 != 0:
            raise ValueError(f"{nombre}: 'tamano_poblacion' debe ser un entero par (mayor o igual que 2).")

    for generaciones in como_lista(problema["num_generaciones"]):
        if not isinstance(generaciones, int) or generaciones < 1:
            raise ValueError(f"{nombre}: 'num_generaciones' debe ser un entero positivo.")

    for tasa in como_lista(problema["tasa_mutacion"]):
        if not es_numero(tasa):
            raise ValueError(f"{nombre}: 'tasa_mutacion' debe ser un número.")

    # El cruce del motor necesita al menos 4 genes (o ciudades) para elegir el punto de corte
    if tipo == "onemax":
        longitud = problema.get("longitud_gen")
        if not es_numero(longitud) or not isinstance(longitud, int) or longitud < 4:
            raise ValueError(f"{nombre}: 'longitud_gen' debe ser un entero mayor o igual que 4.")
    else:
        ciudades = problema.get("ciudades")
        if not isinstance(ciudades, list) or len(ciudades) < 4:
            raise ValueError(f"{nombre}: 'ciudades' debe ser una lista de al menos 4 ciudades.")
        for ciudad in ciudades:
            if not isinstance(ciudad, list) or len(ciudad) != 2 or not all(es_numero(c) for c in ciudad):
                raise ValueError(f"{nombre}: cada ciudad debe ser un par de números [x, y] "
                                 f"(ciudad recibida: {ciudad!r}).")

    optimo = problema.get("optimo_conocido")
    if optimo is not None and not es_numero(optimo):
        raise ValueError(f"{nombre}: 'optimo_conocido' debe ser un número.")

###################
# EXPANSIÓN       #
###################
def expandir_hiperparametros(problema):
    # Una ejecución por cada combinación de la rejilla de hiperparámetros.
    poblaciones = como_lista(problema["tamano_poblacion"])
    generaciones = como_lista(problema["num_generaciones"])
    mutaciones = como_lista(problema["tasa_mutacion"])

    ejecuciones = []
    for poblacion in poblaciones:
        for generacion in generaciones:
            for mutacion in mutaciones:
                # Copia del problema con un único valor en cada hiperparámetro
                ejecucion = problema.copy()
                ejecucion["tamano_poblacion"] = poblacion
                ejecucion["num_generaciones"] = generacion
                ejecucion["tasa_mutacion"] = mutacion
                ejecuciones.append(ejecucion)

    return ejecuciones


def distancias_coordenadas(ciudades):
    # Matriz de distancias euclídeas entre cada par de ciudades.
    distancias = []
    for i in range(len(ciudades)):
        fila = []
        for j in range(len(ciudades)):
            x1, y1 = ciudades[i]
            x2, y2 = ciudades[j]
            distancia = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            fila.append(distancia)
        distancias.append(fila)

    return distancias


def preparar_ejecuciones(problemas):
    """Convierte la lista de pares (tipo, problema) en la lista de ejecuciones individuales:
    una por cada combinación de la rejilla de hiperparámetros de cada problema."""
    ejecuciones = []

    for tipo, problema in problemas:
        # Tamaño N del problema y, en TSP, matriz de distancias (se calcula una vez por problema)
        if tipo == "tsp":
            matriz = distancias_coordenadas(problema["ciudades"])
            tamano = len(problema["ciudades"])
        else:
            tamano = problema["longitud_gen"]

        for ejecucion in expandir_hiperparametros(problema):
            ejecucion["tipo"] = tipo
            ejecucion["tamano_problema"] = tamano   
            if tipo == "tsp":
                ejecucion["matriz_distancias"] = matriz
            ejecuciones.append(ejecucion)

    return ejecuciones


def procesar_instancia(ruta):
    """Lee, valida y expande un archivo sin tocar ningún estado. Si algo falla lanza
    ValueError. Devuelve un dict con ejecuciones, num_nucleos y salida."""
    datos = cargar_json(ruta)
    problemas = agrupar_problemas(datos)

    for numero, (tipo, problema) in enumerate(problemas, start=1):
        validar_problema(problema, tipo, f"Problema {numero} ({tipo})")

    maximo = os.cpu_count() or 1
    num_nucleos = datos.get("num_nucleos", 1)
    if (not isinstance(num_nucleos, int) or isinstance(num_nucleos, bool)
            or not 1 <= num_nucleos <= maximo):
        raise ValueError(f"'num_nucleos' debe ser un entero entre 1 y {maximo} (núcleos disponibles); valor recibido: {num_nucleos!r}.")

    salida = datos.get("salida") or datos.get("output") or {}
    if not isinstance(salida, dict):
        raise ValueError("'salida' debe ser un objeto JSON.")

    return {"ejecuciones": preparar_ejecuciones(problemas), "num_nucleos": num_nucleos, "salida": salida,}


def cargar_archivo(estado, ruta):
    instancia = procesar_instancia(ruta)

    estado["archivo"] = ruta
    estado["ejecuciones"] = instancia["ejecuciones"]
    estado["num_nucleos"] = instancia["num_nucleos"]
    estado["config_salida"] = instancia["salida"]
    estado["historial"] = []
    estado["tiempo_total"] = None


###################
# EJECUCIÓN       #
###################
def crear_argumentos_ejecucion(ejecuciones):
    """Argumentos posicionales de run_genetic_algorithm para cada ejecución.
    Orden del motor: ..., mutation_function, optimo_conocido, tipo, *args
    (en TSP, *args lleva la matriz de distancias)."""
    argumentos = []

    for ejecucion in ejecuciones:
        if ejecucion["tipo"] == "onemax":
            argumentos.append((
                ejecucion["tamano_poblacion"],
                ejecucion["longitud_gen"],
                ejecucion["num_generaciones"],
                ejecucion["tasa_mutacion"],
                generate_individual_bitstring,
                fitness_onemax,
                crossover_bitstring,
                mutate_bitstring,
                ejecucion.get("optimo_conocido"),
                "onemax",
            ))
        else:
            argumentos.append((
                ejecucion["tamano_poblacion"],
                len(ejecucion["ciudades"]),
                ejecucion["num_generaciones"],
                ejecucion["tasa_mutacion"],
                generate_individual_permutation,
                fitness_tsp,
                crossover_permutation,
                swap_mutation,
                ejecucion.get("optimo_conocido"),
                "tsp",
                ejecucion["matriz_distancias"],
            ))

    return argumentos


def construir_resultado(ejecucion, salida_motor):
    # Convierte lo que devuelve el motor en una entrada del historial.
    mejor_individuo, mejor_fitness, tiempo_total, tiempo_optimo = salida_motor
    resultado = {
        "tipo": ejecucion["tipo"],
        "configuracion": config_sin_matriz(ejecucion),
        "mejor_individuo": mejor_individuo,
        "mejor_fitness": mejor_fitness,
        "tiempo": segundos_a_hms(tiempo_total),
        "tiempo_segundos": tiempo_total,
        "tiempo_hasta_optimo": None,
        "tiempo_hasta_optimo_segundos": None,
    }
    if ejecucion["tipo"] == "tsp":
        resultado["mejor_distancia"] = 1 / mejor_fitness
    if tiempo_optimo is not None:
        resultado["tiempo_hasta_optimo"] = segundos_a_hms(tiempo_optimo)
        resultado["tiempo_hasta_optimo_segundos"] = tiempo_optimo
    return resultado


def ejecutar_instancias(ejecuciones, num_nucleos):
    # Ejecuta todas las ejecuciones en paralelo y devuelve la lista de resultados.
    argumentos = crear_argumentos_ejecucion(ejecuciones)

    with multiprocessing.Pool(processes=num_nucleos) as pool:
        salidas = pool.starmap(run_genetic_algorithm, argumentos)

    return [construir_resultado(ejecucion, salida) for ejecucion, salida in zip(ejecuciones, salidas)]


def ejecutar_todo(estado):
    """Opción 3 del menú. Ejecuta todas las ejecuciones cargadas, sustituye el historial
    y guarda el tiempo del conjunto completo. Devuelve el número de ejecuciones hechas."""
    
    if not estado["ejecuciones"]:
        raise ValueError("No hay ejecuciones cargadas. Carga primero un archivo de problemas.")
    inicio = time.perf_counter()
    estado["historial"] = ejecutar_instancias(estado["ejecuciones"], estado["num_nucleos"])
    estado["tiempo_total"] = segundos_a_hms(time.perf_counter() - inicio)


###################
# EXPORTACIÓN     #
###################
def guardar_resultados(estado, ruta):
    # Escribe en un único JSON el tiempo total y el historial completo.
    contenido = {"tiempo_total": estado.get("tiempo_total"), "resultados": estado["historial"]}
    try:
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(contenido, archivo, indent=2, ensure_ascii=False)
    except OSError as error:
        raise ValueError(f"No se pudo escribir '{ruta}': {error}.")


def generar_grafico(historial, ruta_imagen):
    """Un punto por ejecución: tamaño N frente a tiempo hasta el óptimo, con una gráfica
    por tipo de problema. Solo cuentan las ejecuciones que alcanzaron su óptimo conocido,
    y hacen falta al menos 2 tamaños distintos del mismo tipo."""
    puntos = {}
    for resultado in historial:
        tiempo = resultado["tiempo_hasta_optimo_segundos"]
        if tiempo is not None:
            tamano = resultado["configuracion"]["tamano_problema"]
            puntos.setdefault(resultado["tipo"], []).append((tamano, tiempo))

    puntos = {tipo: p for tipo, p in puntos.items() if len({n for n, _ in p}) >= 2}
    if not puntos:
        print("No se generó el gráfico: hacen falta ejecuciones que alcancen su "
              "'optimo_conocido' en al menos 2 tamaños distintos del mismo tipo.")
        return

    matplotlib.use("Agg")   # dibuja directamente a un archivo, sin abrir ninguna ventana
    
    figura, ejes = plt.subplots(1, len(puntos), figsize=(5.5 * len(puntos), 4), squeeze=False)
    for eje, (tipo, lista) in zip(ejes[0], sorted(puntos.items())):
        eje.scatter([n for n, _ in lista], [t for _, t in lista], color="#2a6fdb")
        eje.set_title(tipo.upper())
        eje.set_xlabel("Tamaño del problema N")
        eje.set_ylabel("Tiempo hasta el óptimo (s)")
        eje.grid(axis="y", color="#dddddd")

    figura.tight_layout()
    figura.savefig(ruta_imagen, dpi=150)
    plt.close(figura)
    print(f"Gráfico de rendimiento guardado en '{ruta_imagen}'.")


def exportar_resultados(estado):
    """Opción 5 del menú. Escribe el historial en 'guardar_en' y genera el gráfico si el
    JSON lo pide. Si no hay resultados, lanza ValueError."""
    if not estado["historial"]:
        raise ValueError("No hay resultados que exportar. Ejecuta primero los problemas.")

    guardar_en = estado["config_salida"].get("guardar_en")
    grafico = estado["config_salida"].get("grafico_rendimiento")

    if guardar_en:
        guardar_resultados(estado, guardar_en)
        print(f"Resultados guardados en '{guardar_en}'.")

    if grafico:
        generar_grafico(estado["historial"], "grafico_rendimiento.png")

    if not guardar_en and not grafico:
        print("El archivo cargado no configura ninguna salida; no se ha escrito nada.")