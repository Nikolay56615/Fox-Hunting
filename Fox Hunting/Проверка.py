import pygame
from operator import itemgetter
from datetime import datetime
import os
import random
import time
import sys
import csv

NUM_COLORS = {
    0: pygame.Color(0, 0, 0),
    1: pygame.Color(244, 67, 54),
    2: pygame.Color(156, 39, 176),
    3: pygame.Color(63, 81, 181),
    4: pygame.Color(3, 169, 244),
    5: pygame.Color(0, 188, 212),
    6: pygame.Color(76, 175, 80),
    7: pygame.Color(233, 30, 99),
    8: pygame.Color(255, 152, 0)
}

STATUS_READY = 0
STATUS_PLAYING = 1
STATUS_FAILED = 2
STATUS_SUCCESS = 3

STATUS_ICONS = {
    STATUS_READY: "plus.png",
    STATUS_PLAYING: "smiley.png",
    STATUS_FAILED: "cross.png",
    STATUS_SUCCESS: "smiley-lol.png",
}

COUNTER_OF_FOXES = 0
COUNTER_OF_HODS = 0
LAST_COUNTER_OF_HODS = COUNTER_OF_HODS
LAST_COUNTER_OF_FOXES = 0
LAST_HOD = 0
N_SECS = 0


def load_image(name, colorkey=None):
    fullname = os.path.join('images', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Board:
    def __init__(self):
        self.width = 10
        self.height = 10
        self.board = [[0] * 10 for _ in range(10)]
        self.left = 10
        self.top = 10
        self.cell_size = 20
        self.n_foxes = 8
        self.image = load_image("fox.png")
        self.image1 = pygame.transform.scale(self.image, (18, 18))
        self._reset_add_foxes()

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen, pygame.Color(0, 0, 0), (
                    x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,
                    self.cell_size), 1)

    def on_click(self, cell, screen):
        x = cell[0] * self.cell_size + self.left
        y = cell[1] * self.cell_size + self.top

        if self.board[cell[0]][cell[1]] != 55:

            if self.board[cell[0]][cell[1]] == 9:
                screen.blit(self.image1, (x + 1, y + 1))
                self.board[cell[0]][cell[1]] = 55

            elif self.board[cell[0]][cell[1]] >= 0 and \
                    self.board[cell[0]][cell[1]] != 9:
                font = pygame.font.Font(None, 21)
                digit = self.board[cell[0]][cell[1]]
                text = font.render(str(digit), True, NUM_COLORS[digit])
                screen.blit(text, (x + 5, y + 5))
                self.board[cell[0]][cell[1]] = 55

    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if cell_x < 0 or cell_x >= self.width or cell_y < 0 or cell_y >= self.height:
            return None
        return cell_x, cell_y

    def get_click(self, mouse_pos, screen):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell, screen)

    # Добавляем позиции лис. И определяем значения клеток без лис
    def _reset_add_foxes(self):
        positions = []
        while len(positions) < self.n_foxes:
            x, y = random.randint(0, self.height - 1), random.randint(0, self.height - 1)
            if (x, y) not in positions:
                positions.append((x, y))
                # обрабатываем список списков с цифрами
                for i in range(10):
                    for j in range(10):
                        if i == x and j == y:
                            self.board[i][j] = 9
                        elif i != x and j == y and self.board[i][j] != 9:
                            self.board[i][j] += 1
                        elif i == x and j != y and self.board[i][j] != 9:
                            self.board[i][j] += 1
                        elif abs(i - x) == abs(j - y) and self.board[i][j] != 9:
                            self.board[i][j] += 1


pygame.init()
screen = pygame.display.set_mode((300, 300))
pygame.display.set_caption("Fox Hunting")
screen.fill(pygame.Color('white'))

board = Board()
board.render(screen)
pygame.display.flip()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            board.get_click(event.pos, screen)
    pygame.display.flip()
pygame.quit()
