from gestion_datos import cargar_archivo, ejecutar_todo, exportar_resultados


def crear_estado():
    # el mismo que en main
    return {
        "archivo": None,
        "ejecuciones": [],
        "historial": [],
        "config_salida": {},
        "num_nucleos": 1,
    }


if __name__ == "__main__":   # obligatorio con multiprocessing
    estado = crear_estado()
    try:
        cargar_archivo(estado, "problema.json")
        print("Ejecuciones cargadas:", len(estado["ejecuciones"]))
        print("Núcleos:", estado["num_nucleos"])

        ejecutar_todo(estado)

        for resultado in estado["historial"]:
            config = resultado["configuracion"]
            print(resultado["tipo"], "N =", config["tamano_problema"],
                  "pob =", config["tamano_poblacion"],
                  "mut =", config["tasa_mutacion"],
                  "| mejor fitness:", resultado["mejor_fitness"],
                  "| tiempo:", resultado["tiempo"],
                  "| hasta óptimo:", resultado["tiempo_hasta_optimo"])
        print("Tiempo total:", estado["tiempo_total"])

        exportar_resultados(estado)
    except ValueError as error:
        print("Error:", error)