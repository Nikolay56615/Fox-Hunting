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
VALID_CHARACTERS = 'qwertyuiopasdfghjklzxcvbnm'
VALID_CHARACTERS += '[]-_()1234567890!@$&*+=/~.'
VALID_CHARACTERS += 'QWERTYUIOPASDFGHJKLZXCVBNM'
VALID_CHARACTERS += 'ёйцукенгшщзхъфывапролджэячсмитьбю'
VALID_CHARACTERS += 'ЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ'


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


def loadTable(table_name):
    with open(table_name, encoding="utf8") as csvfile:
        reader = csv.reader(csvfile,
                            delimiter=';', quotechar='"')
        title = next(reader)
        list_of_lines = []
        for i, row in enumerate(reader):
            row[1] = int(row[1])
            row[2] = int(row[2])
            list_of_lines.append(row)
        s = sorted(list_of_lines, key=itemgetter(2))  # сортируем по вторичному ключу
        s = sorted(s, key=itemgetter(1))
        s.insert(0, title)
    return s


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
                font = pygame.font.Font(None, 28)
                digit = self.board[cell[0]][cell[1]]
                text = font.render(str(digit), True, NUM_COLORS[digit])
                screen.blit(text, (x + 8, y + 5))
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
size = width, height = 320, 330
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Fox Hunting")
screen.fill(pygame.Color('white'))

if __name__ == '__main__':
    in_game = True
    start_screen = True
    score_screen = False
    button_x = 0
    button_y = 0
    button_x1 = 0
    button_y1 = 0
    # Основной игровой цикл
    while in_game:
        # Начальный экран
        while start_screen:
            screen.fill((255, 255, 255))

            font = pygame.font.Font(None, 50)
            text = font.render("Начать игру", True, (255, 128, 0))
            text_x = width // 2 - text.get_width() // 2
            text_y = height // 2 - 2 * text.get_height()
            text_w = text.get_width()
            text_h = text.get_height()
            screen.blit(text, (text_x, text_y))
            pygame.draw.rect(screen, (0, 0, 0), (text_x - 10, text_y - 10,
                                                 text_w + 20, text_h + 20), 1)

            font = pygame.font.Font(None, 50)
            text = font.render("Таблица лидеров", True, (255, 128, 0))
            text_x1 = width // 2 - text.get_width() // 2
            text_y1 = height // 2
            text_w1 = text.get_width()
            text_h1 = text.get_height()
            screen.blit(text, (text_x1, text_y1))
            pygame.draw.rect(screen, (0, 0, 0), (text_x1 - 10, text_y1 - 10,
                                                 text_w1 + 20, text_h1 + 20), 1)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    in_game = False
                    start_screen = False
                    running = False

                if event.type == pygame.MOUSEBUTTONUP:
                    x, y = event.pos
                    if text_x1 <= x <= text_x1 + text_w1 and text_y1 <= y <= text_y1 + text_h1:
                        start_screen = False
                        score_screen = True
                    if text_x <= x <= text_x + text_w and text_y <= y <= text_y + text_h:
                        start_screen = False
                        stage0 = True

            pygame.display.flip()
        try:
            screen.fill((255, 255, 255))
        except Exception:
            exit(1)

        # Экран Таблицы очков
        while score_screen:

            font = pygame.font.Font(None, 50)
            text = font.render("Начать игру", True, (255, 128, 0))
            text_x1 = width // 2 - text.get_width() // 2
            text_y1 = height // 1.25
            text_w1 = text.get_width()
            text_h1 = text.get_height()
            screen.blit(text, (text_x1, text_y1))
            pygame.draw.rect(screen, (0, 255, 0), (text_x1 - 10, text_y1 - 10,
                                                   text_w1 + 20, text_h1 + 20), 1)

            table = loadTable('HighScoreTable.csv')

            for i in range(min(6, len(table))):
                string = str(table[i][0]) + ' - ' + str((table[i][1])) + ' - '
                string += str(table[i][2]) + ' - ' + str((table[i][3]))
                font = pygame.font.Font(None, 30)
                text = font.render(string, True, (255, 128, 0))
                text_x = width // 2 - text.get_width() // 2
                text_y = height // 8 * (i + 1) - 40
                screen.blit(text, (text_x, text_y))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    in_game = False
                    score_screen = False
                    running = False

                if event.type == pygame.MOUSEBUTTONUP:
                    x, y = event.pos
                    if text_x1 <= x <= text_x1 + text_w1 and text_y1 <= y <= text_y1 + text_h1:
                        start_screen = False
                        score_screen = False
                        stage0 = True

            pygame.display.flip()

        stage2 = False
        board = Board()
        running = True
        player_name = ''

        clock = pygame.time.Clock()
        if in_game:
            # Стадия до начала игры: ввод имени игрока
            while stage0:
                fps = 180
                if not running:
                    pygame.quit()
                    break
                try:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.unicode in VALID_CHARACTERS:
                                player_name += event.unicode
                            elif event.key == 8:
                                player_name = player_name[:-1]
                            if event.key == 13:
                                stage0 = False
                                stage1 = True
                                break
                except Exception:
                    exit(1)
                screen.fill((0, 0, 0))
                if len(player_name) > 7:
                    player_name = player_name[:7]
                font = pygame.font.Font(None, 36)
                text = font.render("Введи своё имя: {}".format(player_name), True, (100, 255, 100))
                text_x = width // 2 - text.get_width() // 2
                text_y = height // 2 - text.get_height() // 2
                text_w = text.get_width()
                text_h = text.get_height()
                screen.blit(text, (text_x, text_y))

                pygame.display.flip()
                clock.tick(fps)


    pygame.quit()
