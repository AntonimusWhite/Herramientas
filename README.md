# Algoritmos genéticos

Aplicación de consola para resolver problemas **OneMax** y el **problema del
viajante (TSP)** mediante un algoritmo genético. Permite ejecutar varias
configuraciones de cada problema, en paralelo, y exportar los resultados.

## Requisitos y ejecución

Se necesita Python y la biblioteca `matplotlib` para generar gráficos:

```bash
python -m pip install matplotlib
python main.py
```

En el menú:

1. Carga un archivo JSON, por ejemplo `ejemplos/problema.json`.
2. Si lo necesitas, ajusta el número de procesos.
3. Ejecuta las configuraciones cargadas.
4. Consulta el estado y los resultados.
5. Exporta el historial y, si está configurado, genera el gráfico.
6. Sal. El menú avisa si hay resultados todavía sin exportar.

Las rutas del JSON se interpretan desde el directorio desde el que se inicia
`main.py`.

## Formato de entrada

El archivo debe ser un objeto JSON. Puede incluir problemas OneMax,
problemas TSP o ambos:

```json
{
  "problemas_onemax": [
    {
      "tamano_poblacion": [50, 100],
      "num_generaciones": 200,
      "tasa_mutacion": [0.01, 0.05],
      "longitud_gen": 40,
      "optimo_conocido": 40,
      "max_generaciones_sin_mejora": 50
    }
  ],
  "problemas_tsp": [
    {
      "tamano_poblacion": 50,
      "num_generaciones": 200,
      "tasa_mutacion": 0.1,
      "ciudades": [[0, 0], [10, 0], [10, 10], [0, 10]],
      "optimo_conocido": 40
    }
  ],
  "num_nucleos": 2,
  "salida": {
    "guardar_en": "resultados.json",
    "grafico_rendimiento": true
  }
}
```

`tamano_poblacion`, `num_generaciones` y `tasa_mutacion` aceptan un valor o
una lista. Las listas generan una ejecución por cada combinación de valores.
La población debe ser par y mayor o igual que 2; las generaciones, positivas;
y la tasa de mutación, un número entre 0 y 1. OneMax requiere
`longitud_gen` de al menos 4. TSP requiere al menos 4 ciudades, cada una
representada por coordenadas `[x, y]`.

`optimo_conocido` es opcional: representa el fitness objetivo en OneMax y la
distancia mínima conocida en TSP. `max_generaciones_sin_mejora` también es
opcional y detiene la búsqueda tras ese número consecutivo de generaciones sin
mejorar. `num_nucleos` es opcional (por defecto, 1) y no puede superar los
núcleos disponibles.

También se admite un único problema en la raíz, indicando `"tipo": "onemax"`
o `"tipo": "tsp"` y sus parámetros directamente. Los archivos de
[ejemplos](./ejemplos/) muestran configuraciones completas.

## Estructura del proyecto

- [main.py](./main.py) inicia el menú interactivo y mantiene el estado de la
  sesión: archivo cargado, ejecuciones, resultados y configuración de salida.
- [gestion_datos.py](./gestion_datos.py) lee y valida el JSON, expande las
  combinaciones de parámetros, prepara las distancias TSP, ejecuta las tareas
  en paralelo y exporta los resultados.
- [algoritmo_generico.py](./algoritmo_generico.py) contiene los operadores
  genéticos y el motor compartido por los dos tipos de problema.

## Algoritmos

El motor común de [algoritmo_generico.py](./algoritmo_generico.py) genera una
población inicial y repite selección, cruce, mutación y evaluación hasta
alcanzar el máximo de generaciones, encontrar el óptimo conocido o detenerse
por estancamiento. Conserva el mejor individuo global y el mejor de cada
generación (elitismo), y mide el tiempo total y, si corresponde, el tiempo
hasta el óptimo.

- **OneMax:** cada individuo es una cadena de bits. Su fitness es la suma de
  los bits (se maximiza el número de unos). El cruce intercambia las colas de
  dos padres en un punto de corte; la mutación invierte cada bit según la tasa
  configurada.
- **TSP:** cada individuo es una permutación de ciudades. Se mide la longitud
  del recorrido cerrado, incluida la vuelta a la primera ciudad, usando
  distancias euclídeas. El fitness es el inverso de esa distancia, por lo que
  maximizarlo equivale a minimizar el recorrido. El cruce conserva el prefijo
  de cada padre y completa el hijo con las ciudades restantes en el orden del
  otro padre; la mutación intercambia dos ciudades.
- **Selección:** se comparan individuos por parejas y pasa el de mayor fitness
  a la bolsa de apareamiento. El mejor individuo de la población se conserva
  sin mutación.

El cruce selecciona un punto entre las posiciones 2 y `longitud - 2`; por eso
ambos tipos de problema requieren al menos 4 genes o ciudades. La ejecución
de las distintas configuraciones se distribuye entre procesos con
`multiprocessing`.

## Resultados

La opción de exportación guarda, si se indicó `salida.guardar_en`, un JSON con
el tiempo total del conjunto y el historial de ejecuciones. Cada resultado
incluye la configuración, el mejor individuo, su fitness y el tiempo empleado;
los TSP incluyen además la mejor distancia. Si se alcanzó `optimo_conocido`,
se incluye también el tiempo hasta alcanzarlo.

Si `salida.grafico_rendimiento` está activado, se ofrece generar
`grafico_rendimiento.png`. El gráfico compara el tamaño del problema con el
tiempo hasta el óptimo y solo se crea cuando hay resultados con óptimo
alcanzado para al menos dos tamaños distintos del mismo tipo.
