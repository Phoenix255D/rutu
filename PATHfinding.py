import pygame # type: ignore
import sys
import heapq
import random
import subprocess
import os

# Inicializar Pygame
pygame.init()

# Dimensiones de la ventana
width, height = 1400, 780
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pathfinding A*")

heuristic_weigth=1

# Colores
black = (0, 0, 0)
white = (255, 255, 255)
gray = (169, 169, 169)
green = (0, 255, 0)
red = (255, 0, 0)
rod = (205, 30, 30)
yellow = (255, 255, 0)  # Lista abierta
light_blue = (173, 216, 230)  # Lista cerrada
purple = (209, 125, 212)  # Camino más corto
gray = (150, 150, 150)
text_color = black  # Color del texto

# Dimensiones de cada celda
cell_size = 45

# Número de filas y columnas
cols = width // cell_size
rows = height // cell_size

# Estados de las celdas
FREE = 0
OBSTRUCTED = 1
START = 2
END = 3
OPEN = 6
CLOSED = 7
PATH = 8  # Estado de la celda para el camino más corto
PLAYER = 9

# Inicializar la cuadrícula con todas las celdas libres
grid = [[FREE for _ in range(rows)] for _ in range(cols)]
g_score = {}  # Diccionario para almacenar el costo g de cada celda
h_score = {}  # Diccionario para almacenar el costo h de cada celda

# Posiciones de inicio y final
start_pos = (0, 0)
end_pos = (cols - 1, rows - 1)

# Asignar la celda de inicio y final
grid[start_pos[0]][start_pos[1]] = START
grid[end_pos[0]][end_pos[1]] = END

dragging_start = False
dragging_end = False

# Variables para el modo paso a paso
step_by_step = False
open_set = []
came_from = {}
current = None
next_step = False
previous_steps = []
opened_in_step = []  # Lista de celdas abiertas en cada paso
path_found = False  # Ruta encontrada
path = []  # Ruta más corta

# Crear fuente para los botones y texto
font = pygame.font.SysFont(None, 36)
text_font = pygame.font.SysFont(None, int(cell_size/2.7))  # Fuente para el texto del costo
text_font_big = pygame.font.SysFont(None, int(cell_size/1.94))  # Fuente para el texto del costo
# Cargar imagen del obstáculo
# Cargar varias imágenes de obstáculos y ajustarlas al tamaño de celda
obstacle_images = []
for i in range(1, 6):  # si tus archivos son h1.png, h2.png, h3.png, h4.png, h5.png
    img = pygame.image.load(f"h{i}.png").convert_alpha()
    img = pygame.transform.scale(img, (cell_size, cell_size))
    obstacle_images.append(img)

# Inicializar la cuadrícula con todas las celdas libres
grid = [[FREE for _ in range(rows)] for _ in range(cols)]
g_score = {}  # Diccionario para almacenar el costo g de cada celda
h_score = {}  # Diccionario para almacenar el costo h de cada celda

# Diccionario para guardar qué imagen tiene cada obstáculo
grid_image_map = {}

# Función para dibujar la cuadrícula
def draw_grid(show_weights=True, show_path=False):
    for x in range(cols):
        for y in range(rows):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            if grid[x][y] == FREE:
                pygame.draw.rect(win, white, rect)
            elif grid[x][y] == OBSTRUCTED:
                if (x, y) in grid_image_map:
                    win.blit(grid_image_map[(x, y)], rect.topleft)
                else:
                    # Si no hay imagen registrada (por seguridad), asigna una aleatoria
                    img = random.choice(obstacle_images)
                    grid_image_map[(x, y)] = img
                    win.blit(img, rect.topleft)
            elif grid[x][y] == START:
                pygame.draw.rect(win, green, rect)
            elif grid[x][y] == END:
                pygame.draw.rect(win, red, rect)
            #elif grid[x][y] == OPEN:
                #pygame.draw.rect(win, yellow, rect)
            #elif grid[x][y] == CLOSED:
                #pygame.draw.rect(win, light_blue, rect)
            elif grid[x][y] == PATH:
                pygame.draw.rect(win, purple, rect)

            if show_weights and (grid[x][y] in [OPEN, CLOSED, END, PATH]):
                if (x, y) in g_score and (x, y) in h_score:
                    g_text = text_font.render(str(g_score[(x, y)]), True, text_color)
                    h_text = text_font.render(str(h_score[(x, y)]), True, text_color)
                    f_text = text_font_big.render(str(g_score[(x, y)] + h_score[(x, y)]), True, text_color)
                    g_rect = g_text.get_rect(topleft=(x * cell_size + 5, y * cell_size + 5))
                    h_rect = h_text.get_rect(topright=(x * cell_size + cell_size - 5, y * cell_size + 5))
                    f_rect = f_text.get_rect(midbottom=(x * cell_size + cell_size // 2, y * cell_size + cell_size - 5))
                    #win.blit(g_text, g_rect)
                    #win.blit(h_text, h_rect)
                    #win.blit(f_text, f_rect)

            pygame.draw.rect(win, gray, rect, 1)
        
        rectP = pygame.Rect(playerX * cell_size, playerY * cell_size, cell_size, cell_size)
        pygame.draw.rect(win, gray, rectP)
        rectE = pygame.Rect(start_pos[0] * cell_size, start_pos[1] * cell_size, cell_size, cell_size)
        pygame.draw.rect(win, rod, rectE)

# Función para calcular la heurística diagonal
def heuristic(a, b):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    D1 = 10  # Costo de moverse horizontal o verticalmente
    D2 = 14  # Costo de moverse en diagonal
    return D1 * (dx + dy) + (D2 - 2 * D1) * min(dx, dy)

# Función para encontrar los vecinos de una celda con sus costos
def get_neighbors(node):
    neighbors = []
    x, y = node
    for dx, dy, cost in [(-1, 0, 10), (1, 0, 10), (0, -1, 10), (0, 1, 10),
                         (-1, -1, 14), (-1, 1, 14), (1, -1, 14), (1, 1, 14)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < cols and 0 <= ny < rows and grid[nx][ny] != OBSTRUCTED:
            neighbors.append(((nx, ny), cost))
    return neighbors

# Función para realizar el algoritmo A* de forma paso a paso
def a_star_step():
    global current, next_step, path_found, path, step_by_step

    if current is None:
        if not open_set:
            return []
        _, current = heapq.heappop(open_set)
        previous_steps.append(current)
        opened_in_step.append([])

    if current == end_pos:
        path = reconstruct_path(came_from, current)
        path_found = True
        step_by_step = False
        return path

    for neighbor, move_cost in get_neighbors(current):
        tentative_g_score = g_score[current] + move_cost
        tentative_h_score = heuristic(neighbor, end_pos)

        if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
            came_from[neighbor] = current
            g_score[neighbor] = tentative_g_score
            h_score[neighbor] = tentative_h_score
            
            f_score = tentative_g_score + heuristic_weigth * (tentative_h_score + 0.001 * tentative_h_score)

            heapq.heappush(open_set, (f_score, neighbor))
            print(f"Nodo {neighbor} -> f_score: {f_score}, g_score: {tentative_g_score}, h_score: {tentative_h_score}")

            if grid[neighbor[0]][neighbor[1]] not in [START, END]:
                grid[neighbor[0]][neighbor[1]] = OPEN
                if opened_in_step:
                    opened_in_step[-1].append(neighbor)

    if grid[current[0]][current[1]] not in [START, END]:
        grid[current[0]][current[1]] = CLOSED

    current = None
    #next_step = False
    draw_grid()
    pygame.display.flip()

    return []


# Función para inicializar el algoritmo A*
def init_a_star():
    global open_set, came_from, g_score, h_score, current, previous_steps, opened_in_step, path_found, path
    open_set = []
    heapq.heappush(open_set, (0, start_pos))
    came_from = {}
    g_score[start_pos] = 0
    h_score[start_pos] = heuristic(start_pos, end_pos)
    current = None
    previous_steps = []
    opened_in_step = []
    path_found = False
    path = []

# Función para reconstruir el camino encontrado
def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]

    path.reverse()
    return path

# Función para reiniciar la cuadrícula sin cambiar los obstáculos, inicio y meta
def reset_grid():
    global g_score, h_score, step_by_step, path_found, path, current, open_set, came_from, previous_steps, opened_in_step

    # Limpiar las celdas que no sean obstáculos, inicio, ni meta
    for x in range(cols):
        for y in range(rows):
            if grid[x][y] not in [OBSTRUCTED, START, END]:
                grid[x][y] = FREE

    g_score = {}
    h_score = {}
    step_by_step = False
    path_found = False
    path = []
    current = None
    open_set = []
    came_from = {}
    previous_steps = []
    opened_in_step = []

    draw_grid()
    pygame.display.flip()

# Función para reiniciar completamente la cuadrícula (incluyendo obstáculos, inicio y meta)
def reset_all_grid():
    global grid, start_pos, end_pos
    grid = [[FREE for _ in range(rows)] for _ in range(cols)]
    start_pos = (0, 0)
    end_pos = (cols - 1, rows - 1)
    grid[start_pos[0]][start_pos[1]] = START
    grid[end_pos[0]][end_pos[1]] = END
    reset_grid()
    
def open_other_file():
    pygame.quit()
    # Cambia 'otro_archivo.py' por el nombre de tu archivo
    subprocess.Popen([sys.executable, 'hola.py'])
    sys.exit()
    
# Función para dibujar los botones
def draw_buttons():
    reset_all_button = pygame.Rect(50, height - 50, 120, 40)
    pygame.draw.rect(win, gray, reset_all_button)
    win.blit(font.render("Reset_all", True, black), (60, height - 45))

    reset_button = pygame.Rect(200, height - 50, 150, 40)
    pygame.draw.rect(win, gray, reset_button)
    win.blit(font.render("Reset", True, black), (210, height - 45))

    # NUEVO BOTÓN
    open_file_button = pygame.Rect(width - 200, height - 50, 150, 40)
    pygame.draw.rect(win, gray, open_file_button)
    win.blit(font.render("Modo VS", True, black), (width - 190, height - 45))

    if path_found:
        path_button = pygame.Rect(400, height - 50, 195, 40)
        pygame.draw.rect(win, gray, path_button)
        win.blit(font.render("Ruta más corta", True, black), (410, height - 45))
        return reset_button, reset_all_button, path_button, open_file_button
    else:
        step_button = pygame.Rect(400, height - 50, 150, 40)
        pygame.draw.rect(win, gray, step_button)
        win.blit(font.render("Siguiente", True, black), (410, height - 45))
        return reset_button, reset_all_button, step_button, open_file_button

playerX = 10 
playerY = 10
while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
               pygame.quit()
               sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if(playerY > 0 and grid[playerX][playerY-1] != OBSTRUCTED):
                    playerY -= 1

            if event.key == pygame.K_DOWN:
                if(playerY < 16 and grid[playerX][playerY+1] != OBSTRUCTED):
                    playerY +=1

            if event.key == pygame.K_RIGHT:
                if(playerX < 30 and grid[playerX+1][playerY] != OBSTRUCTED):
                    playerX +=1
                
            if event.key == pygame.K_LEFT:
                if(playerX > 0 and grid[playerX-1][playerY] != OBSTRUCTED):
                    playerX -=1
            for a in range(-1,2):
                for b in range(-1,2):
                    print(start_pos[0]+a,start_pos[1]+b)
                    if(grid[start_pos[0]+a][start_pos[1]+b] == PATH):
                        start_pos = (start_pos[0]+a,start_pos[1]+b)
                        
                        break

            end_pos = (playerX, playerY)

            reset_grid()

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            grid_x = x // cell_size
            grid_y = y // cell_size

            reset_button, reset_all_button, action_button, open_file_button = draw_buttons()

            if reset_button.collidepoint(event.pos):
                reset_grid()
            elif reset_all_button.collidepoint(event.pos):
                reset_all_grid()
            elif open_file_button.collidepoint(event.pos):  # NUEVA CONDICIÓN
                open_other_file()
            elif path_found and action_button.collidepoint(event.pos):
                for pos in path:
                    if pos != end_pos:
                        grid[pos[0]][pos[1]] = PATH
                draw_grid(show_weights=False, show_path=True)
            elif not path_found and action_button.collidepoint(event.pos):
                if not step_by_step:
                    init_a_star()
                    step_by_step = True
                next_step = True
            elif (grid_x, grid_y) == start_pos:
                dragging_start = True
            elif (grid_x, grid_y) == end_pos:
                dragging_end = True
            else:
                # haber pues el uno es para el click normal
                if event.button == 1:  # Click izquierdo: obstáculos
                    if grid[grid_x][grid_y] == FREE:
                        grid[grid_x][grid_y] = OBSTRUCTED
                        grid_image_map[(grid_x, grid_y)] = random.choice(obstacle_images)
                    elif grid[grid_x][grid_y] == OBSTRUCTED:
                        grid[grid_x][grid_y] = FREE
                        if (grid_x, grid_y) in grid_image_map:
                            del grid_image_map[(grid_x, grid_y)]
                # el dos es para el click de la rueda del raton
                elif event.button == 2:
                    if grid[grid_x][grid_y] == START:
                        grid[grid_x][grid_y] = FREE
                    elif (grid_x, grid_y) != end_pos:
                        grid[start_pos[0]][start_pos[1]] = FREE
                        start_pos = (grid_x, grid_y)
                        grid[grid_x][grid_y] = START

                # el tres es para el click derecho
                elif event.button == 3:
                    if grid[grid_x][grid_y] == END:
                        grid[grid_x][grid_y] = FREE
                    elif (grid_x, grid_y) != start_pos:
                        grid[end_pos[0]][end_pos[1]] = FREE
                        end_pos = (grid_x, grid_y)
                        grid[grid_x][grid_y] = END

        if event.type == pygame.MOUSEBUTTONUP:
            dragging_start = False
            dragging_end = False

        if event.type == pygame.MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            grid_x = x // cell_size
            grid_y = y // cell_size

            if dragging_start:
                if (grid_x, grid_y) != end_pos:
                    grid[start_pos[0]][start_pos[1]] = FREE
                    start_pos = (grid_x, grid_y)
                    grid[start_pos[0]][start_pos[1]] = START

            if dragging_end:
                if (grid_x, grid_y) != start_pos:
                    grid[end_pos[0]][end_pos[1]] = FREE
                    end_pos = (grid_x, grid_y)
                    grid[end_pos[0]][end_pos[1]] = END



    win.fill(white)

    if path_found:
        for pos in path:
            if pos != end_pos:
                grid[pos[0]][pos[1]] = PATH
        draw_grid(show_weights=False, show_path=False)
    elif not path_found:
        if not step_by_step:
            init_a_star()
            step_by_step = True
        next_step = True
    #draw_grid()
    draw_buttons()
    path = a_star_step()
    #if step_by_step and next_step:
    pygame.display.flip()
