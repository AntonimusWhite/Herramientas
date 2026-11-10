## Ejecución de problemas

`gestion_datos.procesar_instancia(ruta)` carga y valida un archivo JSON, y
expande las combinaciones de hiperparámetros en una lista de ejecuciones.
Para cada problema TSP, calcula la matriz de distancias una sola vez y la
asocia a sus ejecuciones.

`gestion_datos.ejecutar_instancias(ejecuciones, num_nucleos)` ejecuta las
configuraciones en paralelo mediante `multiprocessing.Pool.starmap` y devuelve
los resultados en el mismo orden que las ejecuciones recibidas. El número de
procesos se configura con `num_nucleos`.

El menú mantiene la configuración y el historial en un diccionario de estado.
Al cargar otro archivo, se reinicia el historial. Los resultados incluyen el
mejor individuo, su fitness y el tiempo de ejecución. Si se configura
`optimo_conocido` y se alcanza, también se registra el tiempo hasta encontrarlo.

## Cruce de permutaciones TSP

`crossover_permutation` conserva un segmento de un padre y completa el hijo
con las ciudades restantes en el orden en que aparecen en el otro padre.
`fill_remaining_in_order` realiza esa selección.