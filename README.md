Programa visualizador de A* hecho en python

Requerimientos: 

python 3.12.5
pygame 2.6.0

Contenido:

El siguiente programa fue realizado usando de base otro proyecto extraido del github: https://github.com/cb3ndev/Visualizador-Algoritmo-A-Estrella


que se encuentre en el video de: https://youtu.be/hQa9JTtq4Ok?si=KXAXJ-awcLujDxwf
el cual explica el funcionamiento practico de A* y ademas ejemplifica muy bien como se usa, por lo que la mayoria del funcionamiento del programa
esta hecho usando su material como base.

El programa inicia corriendo el archivo inicio.py desde la terminal, ya ahí carga un menu con 3 opciones, la primera siendo una pelea de turnos
del jugador contra la computadora que usa A* para perseguirlo mientras que el jugador debe llegar a un punto destino, el segundo es el modo original
que venia para visualizar como funciona el algoritmo en encontrar rutas, ligeramente modificado, y el tercero es una version que compara el comportamiento de Dijkstra y A*
en la busqueda de rutas.

Estos funcionan por medio de:

hola.py : comparativa entre Dijkstra y A*
original.py : modo original de comportamiento con A*
pelea.py : modo de jugador contra computadora que usa A*
inicio.py : menu principal