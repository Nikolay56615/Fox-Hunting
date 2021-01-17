import pygame
from operator import itemgetter
from datetime import datetime
import random
import time
import sys
import csv

NUM_COLORS = {
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
    STATUS_READY: "./images/plus.png",
    STATUS_PLAYING: "./images/smiley.png",
    STATUS_FAILED: "./images/cross.png",
    STATUS_SUCCESS: "./images/smiley-lol.png",
}

COUNTER_OF_FOXES = 0
COUNTER_OF_HODS = 0
LAST_COUNTER_OF_HODS = COUNTER_OF_HODS
LAST_COUNTER_OF_FOXES = 0
LAST_HOD = 0
N_SECS = 0


class Board:
    def __init__(self):
        self.width = 10
        self.height = 10
        self.board = [[0] * 10 for _ in range(10)]
        self.left = 10
        self.top = 10
        self.cell_size = 20
        self.set_view(left, top, cell_size)

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen, pygame.Color(255, 255, 255), (
                    x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,
                    self.cell_size), 1)

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def on_click(self, cell):
        print(cell)

    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if cell_x < 0 or cell_x >= self.width or cell_y < 0 or cell_y >= self.height:
            return None
        return cell_x, cell_y

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)
        else:
            print(cell)
