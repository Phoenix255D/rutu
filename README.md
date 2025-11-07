Visualizador del Algoritmo A* en Python

Este programa es una aplicación visual interactiva que muestra el funcionamiento del algoritmo de búsqueda A*.

Requerimientos

Python 3.12.5

Pygame 2.6.0

Para instalar las dependencias necesarias, ejecutar:

pip install pygame

Ejecución

Para iniciar el programa, se debe ejecutar en una terminal, por ejemplo powershell en caso de windows:

python inicio.py


Esto abrirá un menú principal con tres modos de funcionamiento:

Pelea de turnos (jugador vs computadora):
El jugador debe alcanzar un punto objetivo (cuadro con un png de una mina) mientras la computadora, utilizando el algoritmo A*, intenta alcanzarlo.

Modo original:
Basado en el proyecto original, muestra cómo A* encuentra la ruta óptima paso a paso.
Se realizaron ligeras modificaciones que se aplicaron en los otros 2, como movimiento de los puntos inicio y destino.

Comparativa A* vs Dijkstra:
Muestra como ambos algoritmos buscan rutas en el mismo plano para comparar su funcionameinto.

Archivos principales

inicio.py - Menú principal del programa
pelea.py - Modo jugador contra computadora que usa A*
original.py - Modo visualizador original del algoritmo
hola.py - Comparativa entre Dijkstra y A*

Créditos

Proyecto adaptado y extendido a partir del repositorio:
https://github.com/cb3ndev/Visualizador-Algoritmo-A-Estrella

El cual se obtuvo viendo en el video sobre el algoritmo A*:
https://youtu.be/hQa9JTtq4Ok?si=KXAXJ-awcLujDxwf
