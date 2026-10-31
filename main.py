import os
import json

# from gestion_datos import lo que toque cuando esté creado todo
# from algoritmo_generico import lo que toque cuando esté creado todo


# Estado de la sesión

def crear_estado():
    #empieza vacío
    return {
        "archivo": None,        # ruta del JSON cargado
        "ejecuciones": [],      # todas las ejecuciones
        "historial": [],        # resultados de las ejecuciones ya hechas
        "config_salida": {},    # sección "salida" del JSON
        "num_nucleos": 1,       # núcleos a usar
    }


# Herramientas

def formatear_tiempo(segundos):
    #convierte a horas, minutos y segundos
    if segundos is None:
        return "N/A"
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    resto = segundos - horas * 3600 - minutos * 60
    return f"{horas}h {minutos}m {resto:.2f}s"


def pedir_texto(mensaje):
    #pide texto
    try:
        return input(mensaje).strip()
    #strip quita los espacios antes y después para que los textos queden uniformes
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def pedir_si_no(mensaje, por_defecto=True):
    #pregunta s/n y repite hasta recibir una respuesta válida
    sufijo = " [S/n]: " if por_defecto else " [s/N]: "
    while True:
        texto = pedir_texto(mensaje + sufijo)
        if texto is None:
            return False
        texto = texto.lower()
        if texto == "":
            return por_defecto
        if texto in ("s", "si", "sí", "y", "yes"):
            return True
        if texto in ("n", "no"):
            return False
        print("Responde con 's' o 'n'.")


def num_nucleos(texto, maximo):
    #vuelve un int entre 1 y máximo o None si la entrada no vale
    try:
        valor = int (texto)
    except(ValueError, TypeError):      #devuelve None si el texto de entrada no puede ser convertido a entero 
        return None
    if 1 <= valor <= maximo:            #el valor de los núcleos tiene que estar entre 1 y máximo
        return valor
    return None