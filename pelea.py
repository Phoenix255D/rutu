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
pygame.display.set_caption("Pelea")

heuristic_weigth=1

# Colores
black = (0, 0, 0)
white = (255, 255, 255)
gray = (169, 169, 169)
green = (0, 255, 0)
red = (255, 0, 0)
rod = (205, 30, 30)
yellow = (255, 255, 0)
light_blue = (173, 216, 230)
purple = (209, 125, 212)
blue = (0, 0, 255)
text_color = black

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
PATH = 8
PLAYER = 9
DESTINATION = 10

# Inicializar la cuadrícula con todas las celdas libres
grid = [[FREE for _ in range(rows)] for _ in range(cols)]
g_score = {}
h_score = {}

# Posiciones iniciales - ENEMIGO Y JUGADOR SEPARADOS
start_pos = (25, 12)  # Enemigo (rojo)
end_pos = (5, 5)  # Objetivo del enemigo (perseguir al jugador)
destination = (26, 15)  # Meta del jugador (verde)

# Asignar celdas
grid[start_pos[0]][start_pos[1]] = START
grid[destination[0]][destination[1]] = DESTINATION



dragging_start = False
dragging_end = False

# Variables para el modo paso a paso
step_by_step = False
open_set = []
came_from = {}
current = None
next_step = False
previous_steps = []
opened_in_step = []
path_found = False
path = []

# VARIABLES DEL JUEGO
playerX = 5
playerY = 5
game_over = False
player_won = False
game_message = ""

# Crear fuente para los botones y texto
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)
text_font = pygame.font.SysFont(None, int(cell_size/2.7))
text_font_big = pygame.font.SysFont(None, int(cell_size/1.94))

# Cargar imagenes de obstaculos
obstacle_images = []
for i in range(1, 6):
    try:
        img = pygame.image.load(f"h{i}.png").convert_alpha()
        img = pygame.transform.scale(img, (cell_size, cell_size))
        obstacle_images.append(img)
    except:
        print(f"No se pudo cargar h{i}.png")  

if not obstacle_images:
    print("ERROR: No se encontraron las imágenes h1.png a h5.png")
    pygame.quit()
    sys.exit()

# Diccionario para guardar qué imagen tiene cada obstáculo
grid_image_map = {}

# Cargar imágenes del jugador, enemigo y destino
try:
    player_img = pygame.image.load("bueno.png").convert_alpha()
    player_img = pygame.transform.scale(player_img, (cell_size, cell_size))
except:
    print("No se pudo cargar bueno.png")
    player_img = None

try:
    enemy_img = pygame.image.load("malo.png").convert_alpha()
    enemy_img = pygame.transform.scale(enemy_img, (cell_size, cell_size))
except:
    print("No se pudo cargar malo.png")
    enemy_img = None

try:
    destination_img = pygame.image.load("mina.png").convert_alpha()
    destination_img = pygame.transform.scale(destination_img, (cell_size, cell_size))
except:
    print("No se pudo cargar mina.png")
    destination_img = None

# obstaculos predefinidos
initial_obstacles = [
    (10, 5), (10, 6), (10, 7), (10, 8), (10, 9),
    (12, 10), (13, 10), (14, 10), (15, 10), (16, 10),
    (20, 5), (20, 6), (20, 7), (20, 8),
    (8, 12), (9, 12), (10, 12), (11, 12),
    (18, 2), (18, 3), (18, 4), (18, 5),
]

for obs in initial_obstacles:
    if 0 <= obs[0] < cols and 0 <= obs[1] < rows:
        grid[obs[0]][obs[1]] = OBSTRUCTED
        grid_image_map[obs] = random.choice(obstacle_images)

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
                    grid_image_map[(x, y)] = random.choice(obstacle_images)
                    win.blit(grid_image_map[(x, y)], rect.topleft)
            elif grid[x][y] == START:
                pygame.draw.rect(win, red, rect)
            elif grid[x][y] == DESTINATION:
                if destination_img:
                    win.blit(destination_img, rect.topleft)
                else:
                    pygame.draw.rect(win, green, rect)
                    pygame.draw.rect(win, black, rect, 3)
            elif grid[x][y] == PATH:
                pygame.draw.rect(win, purple, rect)

            pygame.draw.rect(win, gray, rect, 1)
        
    # Dibujar jugador (azul)
    rectP = pygame.Rect(playerX * cell_size, playerY * cell_size, cell_size, cell_size)
    if player_img:
        win.blit(player_img, rectP.topleft)
    else:
        pygame.draw.rect(win, blue, rectP)
    
    # Dibujar enemigo (rojo oscuro)
    rectE = pygame.Rect(start_pos[0] * cell_size, start_pos[1] * cell_size, cell_size, cell_size)
    if enemy_img:
        win.blit(enemy_img, rectE.topleft)
    else:
        pygame.draw.rect(win, rod, rectE)

# Función para calcular la heurística diagonal
def heuristic(a, b):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    D1 = 10
    D2 = 14
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

            if grid[neighbor[0]][neighbor[1]] not in [START, DESTINATION]:
                grid[neighbor[0]][neighbor[1]] = OPEN
                if opened_in_step:
                    opened_in_step[-1].append(neighbor)

    if grid[current[0]][current[1]] not in [START, DESTINATION]:
        grid[current[0]][current[1]] = CLOSED

    current = None
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

    for x in range(cols):
        for y in range(rows):
            if grid[x][y] not in [OBSTRUCTED, START, DESTINATION]:
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

# Función para reiniciar completamente la cuadrícula
def reset_all_grid():
    global grid, start_pos, end_pos, playerX, playerY, game_over, player_won, game_message, grid_image_map
    
    grid = [[FREE for _ in range(rows)] for _ in range(cols)]
    grid_image_map = {}
    
    # Restablecer posiciones iniciales
    playerX = 5
    playerY = 5
    start_pos = (25, 12)
    end_pos = (playerX, playerY)
    
    grid[start_pos[0]][start_pos[1]] = START
    grid[destination[0]][destination[1]] = DESTINATION
    
    # Restablecer obstáculos
    for obs in initial_obstacles:
        if 0 <= obs[0] < cols and 0 <= obs[1] < rows:
            grid[obs[0]][obs[1]] = OBSTRUCTED
            if obstacle_images:
                grid_image_map[(obs[0], obs[1])] = random.choice(obstacle_images)
    
    game_over = False
    player_won = False
    game_message = ""
    
    reset_grid()
    
def open_other_file():
    pygame.quit()
    subprocess.Popen([sys.executable, 'inicio.py'])
    sys.exit()

# Función para verificar colisiones
def check_collision():
    global game_over, player_won, game_message
    
    # Si el enemigo alcanza al jugador
    if start_pos == (playerX, playerY):
        game_over = True
        player_won = False
        game_message = "perdiste"
        return True
    
    # Si el jugador llega al destino
    if (playerX, playerY) == destination:
        game_over = True
        player_won = True
        game_message = "ganaste"
        return True
    
    return False

# Función para mover al enemigo hacia el jugador
def move_enemy():
    global start_pos
    
    # Buscar el siguiente paso en el camino
    for a in range(-1, 2):
        for b in range(-1, 2):
            check_x = start_pos[0] + a
            check_y = start_pos[1] + b
            
            # Verificar límites
            if 0 <= check_x < cols and 0 <= check_y < rows:
                if grid[check_x][check_y] == PATH:
                    # Limpiar la posición anterior
                    grid[start_pos[0]][start_pos[1]] = FREE
                    # Mover al enemigo
                    start_pos = (check_x, check_y)
                    grid[start_pos[0]][start_pos[1]] = START
                    return

# Función para dibujar mensaje de game over
def draw_game_over():
    overlay = pygame.Surface((width, height))
    overlay.set_alpha(128)
    overlay.fill(black)
    win.blit(overlay, (0, 0))
    
    color = green if player_won else red
    text = big_font.render(game_message, True, color)
    text_rect = text.get_rect(center=(width // 2, height // 2))
    win.blit(text, text_rect)
    
    restart_text = font.render("Presiona REINICIAR para jugar de nuevo", True, white)
    restart_rect = restart_text.get_rect(center=(width // 2, height // 2 + 60))
    win.blit(restart_text, restart_rect)
    
# Función para dibujar los botones
def botones():
    reset_all_button = pygame.Rect(50, height - 50, 120, 40)
    pygame.draw.rect(win, gray, reset_all_button)
    win.blit(font.render("Reiniciar", True, black), (60, height - 45))

    reset_button = pygame.Rect(200, height - 50, 150, 40)
    pygame.draw.rect(win, gray, reset_button)
    win.blit(font.render("Reset", True, black), (210, height - 45))

    salirse = pygame.Rect(width - 200, height - 50, 150, 40)
    pygame.draw.rect(win, gray, salirse)
    win.blit(font.render("volver", True, black), (width - 190, height - 45))

    if path_found:
        path_button = pygame.Rect(400, height - 50, 195, 40)
        pygame.draw.rect(win, gray, path_button)
        win.blit(font.render("Ruta más corta", True, black), (410, height - 45))
        return reset_button, reset_all_button, path_button, salirse
    else:
        step_button = pygame.Rect(400, height - 50, 150, 40)
        pygame.draw.rect(win, gray, step_button)
        win.blit(font.render("Siguiente", True, black), (410, height - 45))
        return reset_button, reset_all_button, step_button, salirse

# Loop principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and not game_over:
            moved = False
            
            if event.key == pygame.K_UP:
                if playerY > 0 and grid[playerX][playerY-1] != OBSTRUCTED:
                    playerY -= 1
                    moved = True

            if event.key == pygame.K_DOWN:
                if playerY < rows - 1 and grid[playerX][playerY+1] != OBSTRUCTED:
                    playerY += 1
                    moved = True

            if event.key == pygame.K_RIGHT:
                if playerX < cols - 1 and grid[playerX+1][playerY] != OBSTRUCTED:
                    playerX += 1
                    moved = True
                
            if event.key == pygame.K_LEFT:
                if playerX > 0 and grid[playerX-1][playerY] != OBSTRUCTED:
                    playerX -= 1
                    moved = True
            
            if moved:
                # Verificar colisión después del movimiento del jugador
                if not check_collision():
                    # Mover al enemigo
                    move_enemy()
                    check_collision()
                
                # Actualizar objetivo del enemigo
                end_pos = (playerX, playerY)
                reset_grid()

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            grid_x = x // cell_size
            grid_y = y // cell_size

            reset_button, reset_all_button, action_button, salirse = botones()

            if reset_button.collidepoint(event.pos):
                reset_grid()
            elif reset_all_button.collidepoint(event.pos):
                reset_all_grid()
            elif salirse.collidepoint(event.pos):
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
            elif (grid_x, grid_y) == destination:
                dragging_end = True
            else:
                if event.button == 1:
                    if grid[grid_x][grid_y] == FREE:
                        grid[grid_x][grid_y] = OBSTRUCTED
                        grid_image_map[(grid_x, grid_y)] = random.choice(obstacle_images)  # Quitar el if obstacle_images:
                    elif grid[grid_x][grid_y] == OBSTRUCTED:
                        grid[grid_x][grid_y] = FREE
                        if (grid_x, grid_y) in grid_image_map:
                            del grid_image_map[(grid_x, grid_y)]
                elif event.button == 2:
                    if grid[grid_x][grid_y] == START:
                        grid[grid_x][grid_y] = FREE
                    elif (grid_x, grid_y) != destination:
                        grid[start_pos[0]][start_pos[1]] = FREE
                        start_pos = (grid_x, grid_y)
                        grid[grid_x][grid_y] = START
                elif event.button == 3:
                    if grid[grid_x][grid_y] == DESTINATION:
                        grid[grid_x][grid_y] = FREE
                    elif (grid_x, grid_y) != start_pos:
                        grid[destination[0]][destination[1]] = FREE
                        destination = (grid_x, grid_y)
                        grid[destination[0]][destination[1]] = DESTINATION

        if event.type == pygame.MOUSEBUTTONUP:
            dragging_start = False
            dragging_end = False

        if event.type == pygame.MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            grid_x = x // cell_size
            grid_y = y // cell_size

            if dragging_start:
                if (grid_x, grid_y) != destination:
                    grid[start_pos[0]][start_pos[1]] = FREE
                    start_pos = (grid_x, grid_y)
                    grid[start_pos[0]][start_pos[1]] = START

            if dragging_end:
                if (grid_x, grid_y) != start_pos:
                    grid[destination[0]][destination[1]] = FREE
                    destination = (grid_x, grid_y)
                    grid[destination[0]][destination[1]] = DESTINATION

    win.fill(white)

    if not game_over:
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
        
        botones()
        path = a_star_step()
    else:
        draw_grid()
        botones()
        draw_game_over()
    
    pygame.display.flip()