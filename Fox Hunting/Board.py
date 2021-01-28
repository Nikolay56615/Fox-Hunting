from Проверка import load_image, NUM_COLORS
from Fox_Hunting_2.0 import COUNTER_OF_FOXES, COUNTER_OF_HODS
import pygame
import random


# класс отвечающий за отрисовку поля
# и основнй игровой процесс
class Board:
    def __init__(self):
        self.width = 10
        self.height = 10
        self.board = [[0] * 10 for _ in range(10)]
        self.left = 30
        self.top = 60
        self.cell_size = 26
        self.n_foxes = 8
        self.image = load_image("fox.png")
        self.image1 = pygame.transform.scale(self.image, (24, 24))
        self._reset_add_foxes()

    # рисует изначальное пустое поле на экране
    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen, pygame.Color(0, 0, 0), (
                    x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,
                    self.cell_size), 1)

    # отрисовка всех значений при нажатии на
    # пустую клетку
    def on_click(self, cell, screen):
        global COUNTER_OF_FOXES, COUNTER_OF_HODS
        x = cell[0] * self.cell_size + self.left
        y = cell[1] * self.cell_size + self.top

        if self.board[cell[0]][cell[1]] != 55:

            if COUNTER_OF_FOXES > 0:
                COUNTER_OF_HODS += 1

            if self.board[cell[0]][cell[1]] == 9:
                screen.blit(self.image1, (x + 1, y + 1))
                self.board[cell[0]][cell[1]] = 55
                COUNTER_OF_FOXES -= 1
                pygame.draw.rect(screen, pygame.Color('white'),
                                 (155, 15, 70, 25))
                font = pygame.font.Font(None, 30)
                text = font.render(str(COUNTER_OF_FOXES), True, (0, 0, 0))
                text_x = 160
                text_y = 20
                screen.blit(text, (text_x, text_y))

            elif self.board[cell[0]][cell[1]] >= 0 and \
                    self.board[cell[0]][cell[1]] != 9:
                font = pygame.font.Font(None, 28)
                digit = self.board[cell[0]][cell[1]]
                text = font.render(str(digit), True, NUM_COLORS[digit])
                screen.blit(text, (x + 8, y + 5))
                self.board[cell[0]][cell[1]] = 55

    # возвращает координату значения клетки в
    # self.board
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
            return True
        return False

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

    # открытие всего поля
    def reveal_map(self, screen):
        for x in range(0, self.width):
            for y in range(0, self.width):
                self.on_click((x, y), screen)