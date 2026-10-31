import os

from gestion_datos import (
    cargar_archivo,
    config_sin_matriz,
    ejecutar_todo,
    exportar_resultados,
)


# --------------
# Estado
# --------------

def crear_estado():
    # define el estado inicial
    return {
        "archivo": None,
        "ejecuciones": [],
        "historial": [],
        "config_salida": {},
        "num_nucleos": 1,
        "tiempo_total": None,
    }


# --------------
# Herramientas
# --------------

def pedir_texto(mensaje):
    # recibe texto, si se cancela la operación devuelve None
    try:
        return input(mensaje).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def pedir_si_no(mensaje, por_defecto=True):
    # pregunta s/n convirtiendo a minúscula y aceptando una serie de símiles
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


def llamar_seguro(funcion, *args):
    #Ejecuta la función de gestion_datos 
    try:
        funcion(*args)
        return True
    except ValueError as e:        # errores "esperados" con mensaje legible
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nOperación interrumpida por el usuario.")
    except OSError as e:
        print(f"Error de archivo: {e}")
    except Exception as e:         # evita que el menú se caiga por un fallo
        print(f"Error inesperado: {e}")
    return False


def formatear_tiempo(tiempo):
    # pasa {'horas', 'minutos', 'segundos'} a 'Xh Ym Z.ZZs', si no hay dato devuelve un guion
    if tiempo is None:
        return "—"
    return f"{tiempo['horas']}h {tiempo['minutos']}m {tiempo['segundos']:.2f}s"


def resumir_lista(lista, maximo=30):
    #pasa un breve resumen de la lista si supera el largo de 30
    if len(lista) <= maximo:
        return str(lista)
    return f"{lista[:maximo]} ... ({len(lista)} elementos)"


def parsear_nucleos(texto, maximo):
    # devuelve un entero entre 1 y maximo, o None si la entrada no vale
    try:
        valor = int(texto)
    except (ValueError, TypeError):
        return None
    return valor if 1 <= valor <= maximo else None


def describir_parametros(ejecucion):
    # resumen de una línea de los parámetros de la ejecución (config_sin_matriz quita la matriz)
    partes = []
    for clave, valor in config_sin_matriz(ejecucion).items():
        if clave == "tipo":
            continue
        if clave == "ciudades":
            partes.append(f"ciudades={len(valor)}")
        else:
            partes.append(f"{clave}={valor}")
    return ", ".join(partes)


# --------------
# Menú
# --------------

def opcion_cargar(estado):
    # 1. Carga el archivo
    ruta = pedir_texto("Ruta del archivo JSON (p.ej. problemas/ejemplo.json): ")
    if not ruta:
        print("Operación cancelada.")
        return

    # cargar_archivo valida todo antes de tocar el estado: si falla, se conserva lo anterior
    if llamar_seguro(cargar_archivo, estado, ruta):
        print(f"Archivo cargado: {len(estado['ejecuciones'])} ejecuciones listas. "
              f"Núcleos configurados: {estado['num_nucleos']}.")


def opcion_ajustar(estado):
    # 2. Ajusta los núcleos (entero entre 1 y los núcleos reales de la máquina)
    maximo = os.cpu_count() or 1
    print(f"Núcleos actuales: {estado['num_nucleos']} (máximo disponible: {maximo})")

    while True:
        texto = pedir_texto(f"Nuevo número de núcleos [1-{maximo}] (Enter para mantener): ")
        if not texto:    # None (cancelado) o cadena vacía
            print("Se mantiene el valor anterior.")
            return
        valor = parsear_nucleos(texto, maximo)
        if valor is None:
            print(f"Valor no válido. Introduce un entero entre 1 y {maximo}.")
            continue
        estado["num_nucleos"] = valor
        print(f"Núcleos establecidos a {valor}.")
        return


def opcion_ejecutar(estado):
    #3. Ejecutar en paralelo todas las ejecuciones
    if not estado["ejecuciones"]:
        print("No hay nada cargado. Usa primero la opción 1.")
        return

    # ejecutar_todo sustituye el historial: avisamos antes de perderlo
    if estado["historial"] and not pedir_si_no(
            "Ya hay resultados; se sustituirán por los nuevos. ¿Volver a ejecutar?",
            por_defecto=False):
        print("Operación cancelada.")
        return

    print(f"Ejecutando {len(estado['ejecuciones'])} ejecuciones "
          f"con {estado['num_nucleos']} núcleo(s)...")
    if llamar_seguro(ejecutar_todo, estado):
        print(f"Terminado: {len(estado['historial'])} ejecuciones en "
              f"{formatear_tiempo(estado['tiempo_total'])}.")


def mostrar_resultado(resultado):
    #Imprime los datos de un resultado del historial
    if resultado["tipo"] == "tsp":
        print(f"      mejor distancia: {resultado['mejor_distancia']:.2f} "
              f"(fitness {resultado['mejor_fitness']:.6f})")
    else:
        print(f"      mejor fitness: {resultado['mejor_fitness']}")
    print(f"      mejor individuo: {resumir_lista(resultado['mejor_individuo'])}")
    print(f"      tiempo: {formatear_tiempo(resultado['tiempo'])} | "
          f"hasta óptimo: {formatear_tiempo(resultado['tiempo_hasta_optimo'])}")


def opcion_estado(estado):
    #4. Consultar estado (todo lo guardado)
    total = len(estado["ejecuciones"])
    hechas = len(estado["historial"])

    print("\n=== ESTADO DE LA SESIÓN ===")
    print(f"Archivo cargado : {estado['archivo'] or '(ninguno)'}")
    print(f"Núcleos en uso  : {estado['num_nucleos']} (máquina: {os.cpu_count() or 1})")
    print(f"Salida          : {estado['config_salida'] or '(no configurada)'}")
    print(f"Ejecuciones     : {total} cargadas, {hechas} hechas, {total - hechas} pendientes")

    if total:
        print("\n--- Ejecuciones ---")
        for numero, ejecucion in enumerate(estado["ejecuciones"], start=1):
            print(f" #{numero} [{ejecucion['tipo']}] {describir_parametros(ejecucion)}")
            # El historial conserva el orden de las ejecuciones
            if numero <= hechas:
                mostrar_resultado(estado["historial"][numero - 1])
            else:
                print("      (pendiente)")

    if hechas:
        print(f"\nTiempo total del conjunto: {formatear_tiempo(estado['tiempo_total'])}")
    print()


def opcion_exportar(estado):
    #5. Exportar resultados al archivo/gráfico
    if not estado["historial"]:
        print("No hay resultados que exportar. Ejecuta primero la opción 3.")
        return

    estado_exportar = dict(estado)
    estado_exportar["config_salida"] = dict(estado["config_salida"])

    if estado_exportar["config_salida"].get("grafico_rendimiento"):
        estado_exportar["config_salida"]["grafico_rendimiento"] = pedir_si_no(
            "El archivo pide gráfico de rendimiento. ¿Generarlo ahora?"
        )

    # exportar_resultados imprime que ha guardado
    llamar_seguro(exportar_resultados, estado_exportar)


# --------------
# Bucle
# --------------

def mostrar_menu():
    print("\n===== SOLUCIONADOR POR ALGORITMO GENÉTICO =====")
    print(" 1. Cargar archivo de problemas")
    print(" 2. Ajustar parámetros de ejecución")
    print(" 3. Ejecutar todo")
    print(" 4. Consultar estado")
    print(" 5. Exportar resultados")
    print(" 6. Salir")


def ejecutar_menu(estado):
    # bucle del menú
    acciones = {
        "1": opcion_cargar,
        "2": opcion_ajustar,
        "3": opcion_ejecutar,
        "4": opcion_estado,
        "5": opcion_exportar,
    }
    while True:
        mostrar_menu()
        eleccion = pedir_texto("Elige una opción: ")
        if eleccion is None or eleccion == "6":
            print("¡Chau nen!")
            return
        accion = acciones.get(eleccion)
        if accion is None:
            print("Opción no válida. Elige un número del 1 al 6.")
            continue
        accion(estado)


def main():
    estado = crear_estado()
    ejecutar_menu(estado)


if __name__ == "__main__":
    main()