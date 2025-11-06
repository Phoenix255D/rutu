import pygame
import sys
import heapq
import random
import subprocess
import os

# Inicializar Pygame
pygame.init()

# Dimensiones, colores y  tamaños
width, height = 1350, 700
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("A* vs Dijkstra")
heuristic_weight = 1
black = (0, 0, 0)
white = (255, 255, 255)
gray = (169, 169, 169)
green = (0, 255, 0)
red = (255, 0, 0)
yellow = (255, 255, 0)
light_blue = (173, 216, 230)
purple = (209, 125, 212)
text_color = black
cell_size = 70
grid_width = width // 2
cols = grid_width // cell_size
rows = height // cell_size
FREE = 0
OBSTRUCTED = 1
START = 2
END = 3
OPEN = 6
CLOSED = 7
PATH = 8

# Inicializar las cuadrículas
grid_astar = [[FREE for _ in range(rows)] for _ in range(cols)]
grid_dijkstra = [[FREE for _ in range(rows)] for _ in range(cols)]

# costos
g_score_astar = {}
h_score_astar = {}
f_score_astar = {}
g_score_dijkstra = {}

# Posiciones de inicio y final
start_pos = (0, 0)
end_pos = (cols - 1, rows - 1)

# Asignar celdas de inicio y final en ambos grids
grid_astar[start_pos[0]][start_pos[1]] = START
grid_astar[end_pos[0]][end_pos[1]] = END
grid_dijkstra[start_pos[0]][start_pos[1]] = START
grid_dijkstra[end_pos[0]][end_pos[1]] = END

dragging_start = False
dragging_end = False

# Variables para A* y Dijkstra
step_by_step_astar = False
open_set_astar = []
came_from_astar = {}
current_astar = None
path_found_astar = False
path_astar = []
step_by_step_dijkstra = False
open_set_dijkstra = []
came_from_dijkstra = {}
current_dijkstra = None
path_found_dijkstra = False
path_dijkstra = []

#  fuente para los botones y texto
font = pygame.font.SysFont(None, 36)
font_title = pygame.font.SysFont(None, 48)
text_font = pygame.font.SysFont(None, int(cell_size/2.7))
text_font_big = pygame.font.SysFont(None, int(cell_size/1.94))

# Función para dibujar una cuadrícula específica
def draw_grid(grid, g_score, h_score, offset_x=0, show_weights=True):
    for x in range(cols):
        for y in range(rows):
            rect = pygame.Rect(offset_x + x * cell_size, y * cell_size, cell_size, cell_size)
            if grid[x][y] == FREE:
                pygame.draw.rect(win, white, rect)
            elif grid[x][y] == OBSTRUCTED:
                pygame.draw.rect(win, black, rect)
            elif grid[x][y] == START:
                pygame.draw.rect(win, green, rect)
            elif grid[x][y] == END:
                pygame.draw.rect(win, red, rect)
            elif grid[x][y] == OPEN:
                pygame.draw.rect(win, yellow, rect)
            elif grid[x][y] == CLOSED:
                pygame.draw.rect(win, light_blue, rect)
            elif grid[x][y] == PATH:
                pygame.draw.rect(win, purple, rect)

            if show_weights and (grid[x][y] in [OPEN, CLOSED, END, PATH]):
                if (x, y) in g_score:
                    g_text = text_font.render(str(g_score[(x, y)]), True, text_color)
                    g_rect = g_text.get_rect(topleft=(offset_x + x * cell_size + 5, y * cell_size + 5))
                    win.blit(g_text, g_rect)
                    
                    if (x, y) in h_score:
                        h_text = text_font.render(str(h_score[(x, y)]), True, text_color)
                        h_rect = h_text.get_rect(topright=(offset_x + x * cell_size + cell_size - 5, y * cell_size + 5))
                        win.blit(h_text, h_rect)
                        
                        f_text = text_font_big.render(str(g_score[(x, y)] + h_score[(x, y)]), True, text_color)
                        f_rect = f_text.get_rect(midbottom=(offset_x + x * cell_size + cell_size // 2, y * cell_size + cell_size - 5))
                        win.blit(f_text, f_rect)

            pygame.draw.rect(win, gray, rect, 1)

# Función para calcular la heurística diagonal
def heuristic(a, b):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    D1 = 10
    D2 = 14
    return D1 * (dx + dy) + (D2 - 2 * D1) * min(dx, dy)

# Función para encontrar los vecinos de una celda
def get_neighbors(node, grid):
    neighbors = []
    x, y = node
    for dx, dy, cost in [(-1, 0, 10), (1, 0, 10), (0, -1, 10), (0, 1, 10),
                         (-1, -1, 14), (-1, 1, 14), (1, -1, 14), (1, 1, 14)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < cols and 0 <= ny < rows and grid[nx][ny] != OBSTRUCTED:
            neighbors.append(((nx, ny), cost))
    return neighbors

# Función para realizar un paso de A*
def a_star_step():
    global current_astar, path_found_astar, path_astar, step_by_step_astar

    if current_astar is None:
        if not open_set_astar:
            return []
        _, current_astar = heapq.heappop(open_set_astar)

    if current_astar == end_pos:
        path_astar = reconstruct_path(came_from_astar, current_astar)
        path_found_astar = True
        return path_astar

    for neighbor, move_cost in get_neighbors(current_astar, grid_astar):
        tentative_g_score = g_score_astar[current_astar] + move_cost
        tentative_h_score = heuristic(neighbor, end_pos)

        if neighbor not in g_score_astar or tentative_g_score < g_score_astar[neighbor]:
            came_from_astar[neighbor] = current_astar
            g_score_astar[neighbor] = tentative_g_score
            h_score_astar[neighbor] = tentative_h_score
            
            f_score = tentative_g_score + heuristic_weight * (tentative_h_score + 0.001 * tentative_h_score)

            heapq.heappush(open_set_astar, (f_score, neighbor))

            if grid_astar[neighbor[0]][neighbor[1]] not in [START, END]:
                grid_astar[neighbor[0]][neighbor[1]] = OPEN

    if grid_astar[current_astar[0]][current_astar[1]] not in [START, END]:
        grid_astar[current_astar[0]][current_astar[1]] = CLOSED

    current_astar = None
    return []

# Aqui esta el flujo de un paso de Dijkstra
def dijkstra_step():
    global current_dijkstra, path_found_dijkstra, path_dijkstra, step_by_step_dijkstra

    if current_dijkstra is None:
        if not open_set_dijkstra:
            return []
        _, current_dijkstra = heapq.heappop(open_set_dijkstra)

    if current_dijkstra == end_pos:
        path_dijkstra = reconstruct_path(came_from_dijkstra, current_dijkstra)
        path_found_dijkstra = True
        return path_dijkstra

    for neighbor, move_cost in get_neighbors(current_dijkstra, grid_dijkstra):
        tentative_g_score = g_score_dijkstra[current_dijkstra] + move_cost

        if neighbor not in g_score_dijkstra or tentative_g_score < g_score_dijkstra[neighbor]:
            came_from_dijkstra[neighbor] = current_dijkstra
            g_score_dijkstra[neighbor] = tentative_g_score
           
            heapq.heappush(open_set_dijkstra, (tentative_g_score, neighbor))

            if grid_dijkstra[neighbor[0]][neighbor[1]] not in [START, END]:
                grid_dijkstra[neighbor[0]][neighbor[1]] = OPEN

    if grid_dijkstra[current_dijkstra[0]][current_dijkstra[1]] not in [START, END]:
        grid_dijkstra[current_dijkstra[0]][current_dijkstra[1]] = CLOSED

    current_dijkstra = None
    return []

# Función para inicializar A*
def init_a_star():
    global open_set_astar, came_from_astar, g_score_astar, h_score_astar, current_astar, path_found_astar, path_astar
    open_set_astar = []
    heapq.heappush(open_set_astar, (0, start_pos))
    came_from_astar = {}
    g_score_astar = {start_pos: 0}
    h_score_astar = {start_pos: heuristic(start_pos, end_pos)}
    current_astar = None
    path_found_astar = False
    path_astar = []

# aca se inicializa el dijkstra, todo lo de dijkstra se hizo basandose en codigo ya hecho de internet
# una de las paginas consultadas: https://docs.python.org/3/library/heapq.html
def init_dijkstra():
    global open_set_dijkstra, came_from_dijkstra, g_score_dijkstra, current_dijkstra, path_found_dijkstra, path_dijkstra
    open_set_dijkstra = []
    heapq.heappush(open_set_dijkstra, (0, start_pos))
    came_from_dijkstra = {}
    g_score_dijkstra = {start_pos: 0}
    current_dijkstra = None
    path_found_dijkstra = False
    path_dijkstra = []

# Función para reconstruir el camino
def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

# aca se reinician ambas cuadrículas (odio que python deja de funcionar si esta mal identado, perdi mucho tiempo acomodando lineas)
def reset_grids():
    global grid_astar, grid_dijkstra, g_score_astar, h_score_astar, g_score_dijkstra
    global step_by_step_astar, step_by_step_dijkstra, path_found_astar, path_found_dijkstra
    global path_astar, path_dijkstra, current_astar, current_dijkstra
    global open_set_astar, open_set_dijkstra, came_from_astar, came_from_dijkstra

    for x in range(cols):
        for y in range(rows):
            if grid_astar[x][y] not in [OBSTRUCTED, START, END]:
                grid_astar[x][y] = FREE
            if grid_dijkstra[x][y] not in [OBSTRUCTED, START, END]:
                grid_dijkstra[x][y] = FREE

    g_score_astar = {}
    h_score_astar = {}
    g_score_dijkstra = {}
    step_by_step_astar = False
    step_by_step_dijkstra = False
    path_found_astar = False
    path_found_dijkstra = False
    path_astar = []
    path_dijkstra = []
    current_astar = None
    current_dijkstra = None
    open_set_astar = []
    open_set_dijkstra = []
    came_from_astar = {}
    came_from_dijkstra = {}

# Función para reiniciar completamente (incluyendo obstáculos)
def reset_all_grids():
    global grid_astar, grid_dijkstra, start_pos, end_pos
    grid_astar = [[FREE for _ in range(rows)] for _ in range(cols)]
    grid_dijkstra = [[FREE for _ in range(rows)] for _ in range(cols)]
    start_pos = (0, 0)
    end_pos = (cols - 1, rows - 1)
    grid_astar[start_pos[0]][start_pos[1]] = START
    grid_astar[end_pos[0]][end_pos[1]] = END
    grid_dijkstra[start_pos[0]][start_pos[1]] = START
    grid_dijkstra[end_pos[0]][end_pos[1]] = END
    reset_grids()

# Función para salirse al menu del inicio
def salirse():
    pygame.quit()
    subprocess.Popen([sys.executable, 'inicio.py'])
    sys.exit()

# aca se dibujan los botones
def botones():
    reset_all_button = pygame.Rect(50, height - 50, 120, 40)
    pygame.draw.rect(win, gray, reset_all_button)
    win.blit(font.render("Reset_all", True, black), (60, height - 45))

    reset_button = pygame.Rect(200, height - 50, 150, 40)
    pygame.draw.rect(win, gray, reset_button)
    win.blit(font.render("Reset", True, black), (210, height - 45))

    step_button = pygame.Rect(400, height - 50, 150, 40)
    pygame.draw.rect(win, gray, step_button)
    win.blit(font.render("Siguiente", True, black), (410, height - 45))

    boton_salir = pygame.Rect(width - 200, height - 50, 150, 40)
    pygame.draw.rect(win, gray, boton_salir)
    win.blit(font.render("Volver", True, black), (width - 190, height - 45))

    return reset_button, reset_all_button, step_button, boton_salir

# Función para dibujar los títulos
def titulos():
    astar_title = font_title.render("A*", True, black)
    dijkstra_title = font_title.render("Dijkstra", True, black)
    
    astar_rect = astar_title.get_rect(center=(grid_width // 2, 20))
    dijkstra_rect = dijkstra_title.get_rect(center=(grid_width + grid_width // 2, 20))
    
    win.blit(astar_title, astar_rect)
    win.blit(dijkstra_title, dijkstra_rect)

# Bucle principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            grid_x = x // cell_size
            grid_y = y // cell_size

            reset_button, reset_all_button, step_button, boton_salir = botones()

            if reset_button.collidepoint(event.pos):
                reset_grids()
            elif reset_all_button.collidepoint(event.pos):
                reset_all_grids()
            elif boton_salir.collidepoint(event.pos):
                salirse()
            elif step_button.collidepoint(event.pos):
                if not step_by_step_astar:
                    init_a_star()
                    init_dijkstra()
                    step_by_step_astar = True
                    step_by_step_dijkstra = True
                
                # Ejecutar un paso de cada algoritmo
                if not path_found_astar:
                    a_star_step()
                if not path_found_dijkstra:
                    dijkstra_step()
            else:
                # Determinar en qué grid se hizo clic
                if x < grid_width:
                    # Click en grid A* (izquierda)
                    if grid_x < cols and grid_y < rows:
                        if (grid_x, grid_y) == start_pos:
                            dragging_start = True
                        elif (grid_x, grid_y) == end_pos:
                            dragging_end = True
                        else:
                            # haber pues el uno es para el click normal
                            if event.button == 1:
                                if grid_astar[grid_x][grid_y] == FREE:
                                    grid_astar[grid_x][grid_y] = OBSTRUCTED
                                    grid_dijkstra[grid_x][grid_y] = OBSTRUCTED
                                elif grid_astar[grid_x][grid_y] == OBSTRUCTED:
                                    grid_astar[grid_x][grid_y] = FREE
                                    grid_dijkstra[grid_x][grid_y] = FREE
                            
                            # el dos es para el click de la rueda del raton
                            elif event.button == 2:
                                if grid_astar[grid_x][grid_y] == START:
                                    grid_astar[grid_x][grid_y] = FREE
                                    grid_dijkstra[grid_x][grid_y] = FREE
                                elif (grid_x, grid_y) != end_pos:
                                    grid_astar[start_pos[0]][start_pos[1]] = FREE
                                    grid_dijkstra[start_pos[0]][start_pos[1]] = FREE
                                    start_pos = (grid_x, grid_y)
                                    grid_astar[grid_x][grid_y] = START
                                    grid_dijkstra[grid_x][grid_y] = START
                            
                            # el tres es para el click derecho
                            elif event.button == 3:
                                if grid_astar[grid_x][grid_y] == END:
                                    grid_astar[grid_x][grid_y] = FREE
                                    grid_dijkstra[grid_x][grid_y] = FREE
                                elif (grid_x, grid_y) != start_pos:
                                    grid_astar[end_pos[0]][end_pos[1]] = FREE
                                    grid_dijkstra[end_pos[0]][end_pos[1]] = FREE
                                    end_pos = (grid_x, grid_y)
                                    grid_astar[grid_x][grid_y] = END
                                    grid_dijkstra[grid_x][grid_y] = END

        if event.type == pygame.MOUSEBUTTONUP:
            dragging_start = False
            dragging_end = False

        if event.type == pygame.MOUSEMOTION:
            if dragging_start or dragging_end:
                x, y = pygame.mouse.get_pos()
                grid_x = x // cell_size
                grid_y = y // cell_size

                if grid_x < cols and grid_y < rows:
                    if dragging_start and (grid_x, grid_y) != end_pos:
                        grid_astar[start_pos[0]][start_pos[1]] = FREE
                        grid_dijkstra[start_pos[0]][start_pos[1]] = FREE
                        start_pos = (grid_x, grid_y)
                        grid_astar[start_pos[0]][start_pos[1]] = START
                        grid_dijkstra[start_pos[0]][start_pos[1]] = START

                    if dragging_end and (grid_x, grid_y) != start_pos:
                        grid_astar[end_pos[0]][end_pos[1]] = FREE
                        grid_dijkstra[end_pos[0]][end_pos[1]] = FREE
                        end_pos = (grid_x, grid_y)
                        grid_astar[end_pos[0]][end_pos[1]] = END
                        grid_dijkstra[end_pos[0]][end_pos[1]] = END

    win.fill(white)
    
    # Dibujado de los elementos
    pygame.draw.line(win, black, (grid_width, 0), (grid_width, height), 3)
    titulos()
    draw_grid(grid_astar, g_score_astar, h_score_astar, offset_x=0)
    draw_grid(grid_dijkstra, g_score_dijkstra, {}, offset_x=grid_width)
    if path_found_astar:
        for pos in path_astar:
            if pos != end_pos:
                grid_astar[pos[0]][pos[1]] = PATH
    
    if path_found_dijkstra:
        for pos in path_dijkstra:
            if pos != end_pos:
                grid_dijkstra[pos[0]][pos[1]] = PATH
    
    botones()
    pygame.display.flip()

pygame.quit()