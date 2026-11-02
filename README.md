# Herramientas

## Carga de problemas

`gestion_datos.procesar_instancia(ruta)` carga un archivo JSON y devuelve dos
listas: las ejecuciones OneMax y las ejecuciones TSP, expandidas por cada
combinación de hiperparámetros. Cada ejecución TSP incluye
`matriz_distancias`, calculada a partir de `ciudades`.

Los problemas se declaran en las secciones `problemas_onemax` y
`problemas_tsp`; cada sección acepta un problema o una lista. Los tres
hiperparámetros del solucionador aceptan un valor o una lista de valores.

`gestion_datos.ejecutar_instancias(ejecuciones_onemax, ejecuciones_tsp,
num_nucleos)` ejecuta las configuraciones en paralelo con
`multiprocessing.Pool.starmap` y devuelve el resultado, la configuración y el
tiempo de cada ejecución, desglosado en horas, minutos y segundos. Para TSP,
la matriz de distancias se pasa a la función de fitness mediante `*args`; para
OneMax no se pasa ningún argumento adicional.

## Historial, exportación y gráficos

`SesionEjecucion` mantiene en memoria la configuración cargada y el historial
de resultados de la sesión. Al cargar otro archivo, reemplaza la configuración
y reinicia el historial. `ejecutar()` procesa las ejecuciones pendientes y
añade sus resultados al historial. `exportar_resultados()` guarda el archivo
JSON configurado con la configuración completa y el historial.

Cada resultado incluye el mejor individuo y su fitness, el tiempo total y,
cuando hay `optimo_conocido` y se alcanza, el tiempo hasta encontrarlo por
primera vez. El gráfico usa este último tiempo, no el tiempo total. Los
gráficos se generan por separado para OneMax y TSP, junto al JSON, con nombres
como `resultados_rendimiento_onemax.png`. Si varias ejecuciones del mismo tipo
tienen el mismo tamaño N, se representa la media de sus tiempos hasta el
óptimo. Solo se crea un gráfico cuando hay datos de al menos dos tamaños
distintos para ese tipo.

Instala las dependencias con `pip install -r requirements.txt`.
