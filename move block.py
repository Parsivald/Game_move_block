#!/usr/bin/env python
# coding: utf-8

# In[35]:


import pygame
import sys
from copy import deepcopy
from pygame.locals import *

pygame.init()

# Ustawienia ekranu
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 10, 10
TILE_SIZE = WIDTH // COLS
FPS = 60

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

# Inicjalizacja
screen = pygame.display.set_mode((WIDTH, HEIGHT + 50))
pygame.display.set_caption("Gra logiczna")
clock = pygame.time.Clock()

# Poziomy planszy
levels = [
    [
        list("##########"),
        list("#........#"),
        list("#..1.....#"),
        list("#........#"),
        list("#....@...#"),
        list("#....#...#"),
        list("#........#"),
        list("#....2...#"),
        list("#..g1..g2#"),
        list("##########"),
    ],
    [
        list("##########"),
        list("#.......g2#"),
        list("#..1..####"),
        list("#....#...#"),
        list("#...#....#"),
        list("#....2...#"),
        list("#........#"),
        list("#....@...#"),
        list("#..g1....#"),
        list("##########"),
    ],
    [
        list("##########"),
        list("#........#"),
        list("#@.....2.#"),
        list("#.####.#.#"),
        list("#........#"),
        list("#.1......#"),
        list("#........#"),
        list("#..##....#"),
        list("#........#"),
        list("#..g1..g2#"),
        list("##########"),
    ],
]

# Globalne zmienne
level_index = 0
undo_stack = []
move_count = 0
level_data = []  # dodano, by istniała globalnie
walls, boxes, goals, player = set(), {}, {}, (0, 0)  # placeholdery


def parse_level(level_data):
    walls, boxes, goals, player = set(), {}, {}, None
    for r, row in enumerate(level_data):
        c = 0
        while c < len(row):
            char = row[c]
            pos = (r, c)
            if char == '#':
                walls.add(pos)
            elif char == '@':
                player = pos
            elif char in '123456789':
                boxes[pos] = char
            elif char == 'g' and c + 1 < len(row) and row[c + 1] in '123456789':
                goals[pos] = row[c + 1]
                c += 1
            c += 1
    return walls, boxes, goals, player


def draw(walls, boxes, goals, player):
    screen.fill(GRAY)
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

    for r, c in walls:
        pygame.draw.rect(screen, BLACK, (c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    for (r, c), digit in goals.items():
        pygame.draw.rect(screen, GREEN, (c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        render_text(digit, c, r)

    for (r, c), digit in boxes.items():
        pygame.draw.rect(screen, RED, (c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        render_text(digit, c, r)

    pr, pc = player
    pygame.draw.rect(screen, BLUE, (pc * TILE_SIZE, pr * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    pygame.draw.rect(screen, GRAY, (50, HEIGHT + 5, 100, 40))
    pygame.draw.rect(screen, BLACK, (50, HEIGHT + 5, 100, 40), 2)
    screen.blit(pygame.font.SysFont(None, 24).render("Reset", True, BLACK), (75, HEIGHT + 15))

    pygame.draw.rect(screen, GRAY, (200, HEIGHT + 5, 100, 40))
    pygame.draw.rect(screen, BLACK, (200, HEIGHT + 5, 100, 40), 2)
    screen.blit(pygame.font.SysFont(None, 24).render("Cofnij", True, BLACK), (225, HEIGHT + 15))

    font = pygame.font.SysFont(None, 24)
    moves_text = font.render(f"Ruchy: {move_count}", True, BLACK)
    screen.blit(moves_text, (400, HEIGHT + 15))

    pygame.display.flip()


def render_text(text, col, row):
    font = pygame.font.SysFont(None, 24)
    text_surf = font.render(text, True, BLACK)
    rect = text_surf.get_rect(center=(col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2))
    screen.blit(text_surf, rect)


def move(dx, dy, walls, boxes, goals, player):
    global undo_stack, move_count
    pr, pc = player
    nr, nc = pr + dy, pc + dx
    if (nr, nc) in walls:
        return player
    if (nr, nc) in boxes:
        br, bc = nr + dy, nc + dx
        if (br, bc) in walls or (br, bc) in boxes:
            return player
        undo_stack.append((deepcopy(boxes), player))
        boxes[(br, bc)] = boxes.pop((nr, nc))
        move_count += 1
        return (nr, nc)
    else:
        undo_stack.append((deepcopy(boxes), player))
        move_count += 1
        return (nr, nc)


def check_win(boxes, goals):
    return all(pos in goals and boxes[pos] == goals[pos] for pos in boxes) and len(boxes) == len(goals)


def show_win_screen():
    win_font = pygame.font.SysFont(None, 48)
    win_text = win_font.render("Poziom ukończony!", True, GREEN)
    rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(win_text, rect)

    pygame.draw.rect(screen, GRAY, (150, HEIGHT // 2 + 50, 100, 40))
    pygame.draw.rect(screen, BLACK, (150, HEIGHT // 2 + 50, 100, 40), 2)
    screen.blit(pygame.font.SysFont(None, 24).render("Koniec", True, BLACK), (180, HEIGHT // 2 + 60))

    pygame.draw.rect(screen, GRAY, (350, HEIGHT // 2 + 50, 100, 40))
    pygame.draw.rect(screen, BLACK, (350, HEIGHT // 2 + 50, 100, 40), 2)
    screen.blit(pygame.font.SysFont(None, 24).render("Dalej", True, BLACK), (380, HEIGHT // 2 + 60))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                if 150 <= x <= 250 and HEIGHT // 2 + 50 <= y <= HEIGHT // 2 + 90:
                    pygame.quit()
                    sys.exit()
                if 350 <= x <= 450 and HEIGHT // 2 + 50 <= y <= HEIGHT // 2 + 90:
                    return


# Główna pętla gry
while True:

    def reset_level():
        global walls, boxes, goals, player, undo_stack, move_count, level_data
        level_data = deepcopy(levels[level_index])
        walls, boxes, goals, player = parse_level(deepcopy(level_data))
        undo_stack.clear()
        move_count = 0

    reset_level()

    while True:
        clock.tick(FPS)
        draw(walls, boxes, goals, player)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    player = move(-1, 0, walls, boxes, goals, player)
                elif event.key == K_RIGHT:
                    player = move(1, 0, walls, boxes, goals, player)
                elif event.key == K_UP:
                    player = move(0, -1, walls, boxes, goals, player)
                elif event.key == K_DOWN:
                    player = move(0, 1, walls, boxes, goals, player)
            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                if 50 <= x <= 150 and HEIGHT + 5 <= y <= HEIGHT + 45:
                    reset_level()
                if 200 <= x <= 300 and HEIGHT + 5 <= y <= HEIGHT + 45:
                    if undo_stack:
                        boxes, player = undo_stack.pop()
                        move_count = max(0, move_count - 1)

        if check_win(boxes, goals):
            draw(walls, boxes, goals, player)
            pygame.display.flip()
            pygame.time.delay(200)
            show_win_screen()
            level_index += 1
            if level_index >= len(levels):
                pygame.quit()
                sys.exit()
            break


# In[ ]:




