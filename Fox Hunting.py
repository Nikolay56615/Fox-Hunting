from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from operator import itemgetter
from datetime import datetime

import random
import time
import sys
import csv

IMG_FOX = QImage("./images/fox.png")
IMG_HODS = QImage("./images/hod.png")
IMG_CLOCK = QImage("./images/clock-select.png")

NUM_COLORS = {
    1: QColor('#f44336'),
    2: QColor('#9C27B0'),
    3: QColor('#3F51B5'),
    4: QColor('#03A9F4'),
    5: QColor('#00BCD4'),
    6: QColor('#4CAF50'),
    7: QColor('#E91E63'),
    8: QColor('#FF9800')
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


# представляет плитку и содержит всю необходимую
# информацию о своей позиции на карте
class Pos(QWidget):
    revealed = pyqtSignal(object)
    clicked = pyqtSignal()
    update_hods = pyqtSignal()
    win = pyqtSignal()

    def __init__(self, x, y, *args, **kwargs):
        super(Pos, self).__init__(*args, **kwargs)

        self.setFixedSize(QSize(20, 20))
        self.x = x
        self.y = y
        self.reset()

    #  сбрасывает все атрибуты объектов
    #  до значения по умолчанию, т.е. нулевые значения.
    def reset(self):
        self.is_start = False
        self.is_fox = False
        self.check_n = 0
        self.is_revealed = False

        self.update()

    # рисование плитки
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        r = event.rect()

        if self.is_revealed:

            if self.is_fox:
                p.drawPixmap(r, QPixmap(IMG_FOX))

            elif self.check_n > 0 and self.check_n != 9:
                pen = QPen(NUM_COLORS[self.check_n])
                p.setPen(pen)
                f = p.font()
                f.setBold(True)
                p.setFont(f)
                p.drawText(r, Qt.AlignHCenter | Qt.AlignVCenter, str(self.check_n))

        else:
            p.fillRect(r, QBrush(Qt.lightGray))
            pen = QPen(Qt.gray)
            pen.setWidth(1)
            p.setPen(pen)
            p.drawRect(r)

    # Подавление сигнала при раскрытии плитки,
    # который приводит к дальнейшему поиску и раскрытии всей карты.
    def reveal(self, emit=True):
        if not self.is_revealed:
            global COUNTER_OF_HODS
            self.is_revealed = True
            COUNTER_OF_HODS += 1
            self.update()

            if emit:
                self.revealed.emit(self)

    # обрабатывает нажатие левой кнопкой мыши,
    # и в свою очередь, приводит к раскрытию квадрата
    def click(self):
        self.reveal()

        self.clicked.emit()

    # Обработка нажатия левой кнопки мыши
    def mouseReleaseEvent(self, e):
        global COUNTER_OF_FOXES, LAST_COUNTER_OF_HODS, LAST_COUNTER_OF_FOXES
        if e.button() == Qt.LeftButton:
            self.click()
            if self.is_fox:
                COUNTER_OF_FOXES += 1
            if LAST_COUNTER_OF_HODS != COUNTER_OF_HODS:
                LAST_COUNTER_OF_HODS = COUNTER_OF_HODS
                self.update_hods.emit()
            if COUNTER_OF_FOXES == 8:
                COUNTER_OF_FOXES = 0
                LAST_COUNTER_OF_FOXES = 8
                self.win.emit()


# Этот класс отвечает за окно с таблицей рекордов
class QHighScoreTable(QWidget):
    def __init__(self):
        super(QHighScoreTable, self).__init__()

        self.setWindowTitle('Таблица рекордов')
        self.setGeometry(500, 300, 700, 600)
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(QRect(10, 50, 680, 280))
        hb1 = QHBoxLayout()
        self.info = QLabel(self)
        self.info.setText('Таблица рекордов')
        f = self.info.font()  # увеличение размера и *жирности* текста
        f.setPointSize(24)
        f.setWeight(75)
        self.info.setFont(f)
        hb1.addWidget(self.info)
        vb = QVBoxLayout()  # выстраивает виджеты по вертикали
        vb.addLayout(hb1)
        self.loadTable('HighScoreTable.csv')

    # записывает значения из csv файла в таблицу
    def loadTable(self, table_name):
        with open(table_name, encoding="utf8") as csvfile:
            reader = csv.reader(csvfile,
                                delimiter=';', quotechar='"')
            title = next(reader)
            self.tableWidget.setColumnCount(len(title))
            self.tableWidget.setHorizontalHeaderLabels(title)
            self.tableWidget.setRowCount(0)
            list_of_lines = []
            for i, row in enumerate(reader):
                row[1] = int(row[1])
                row[2] = int(row[2])
                list_of_lines.append(row)
            s = sorted(list_of_lines, key=itemgetter(2))  # сортируем по вторичному ключу
            s = sorted(s, key=itemgetter(1))
            for i, row in enumerate(s):
                self.tableWidget.setRowCount(
                    self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.tableWidget.setItem(
                        i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()


# Этот класс отвечает за появление окна для ввода
# никнейма в том случае, если игрок победил, и
# условие попадания результата в таблицу рекордов было выполнено.
class QSaveCSV(QWidget):
    hide_q = pyqtSignal()

    def __init__(self):
        super(QSaveCSV, self).__init__()

        self.setGeometry(300, 300, 280, 220)
        self.label_text_hods = QLabel(self)
        self.label_text_hods.move(10, 20)
        self.label_text_hods.setFont(QFont('Arial', 11))
        self.label_text_hods.resize(250, 20)
        QWidget.hide(self.label_text_hods)
        self.label_text_timer = QLabel(self)
        self.label_text_timer.move(10, 40)
        self.label_text_timer.setFont(QFont('Arial', 11))
        self.label_text_timer.resize(250, 20)
        QWidget.hide(self.label_text_timer)
        self.label_text_name = QLabel(self)
        self.label_text_name.move(10, 60)
        self.label_text_name.setFont(QFont('Arial', 11))
        self.label_text_name.resize(250, 20)
        QWidget.hide(self.label_text_name)

        self.name_input = QLineEdit(self)
        self.name_input.resize(185, 20)
        self.name_input.move(10, 85)
        QWidget.hide(self.name_input)

        self.button_save = QPushButton('Сохранить', self)
        self.button_save.resize(65, 22)
        self.button_save.move(205, 84)
        self.button_save.pressed.connect(self.button_save_pressed)
        QWidget.hide(self.button_save)

        congratulation = 'Поздравляю, ваш результат соответствует'
        self.label_text_con1 = QLabel(congratulation, self)
        self.label_text_con1.move(10, 110)
        self.label_text_con1.setFont(QFont('Arial', 9))
        self.label_text_con1.resize(250, 20)
        congratulation = 'критериям попадания в таблицу рекордов!'
        self.label_text_con2 = QLabel(congratulation, self)
        self.label_text_con2.move(10, 130)
        self.label_text_con2.setFont(QFont('Arial', 9))
        self.label_text_con2.resize(250, 20)

        self.button_congratulation = QPushButton('Продолжить', self)
        self.button_congratulation.resize(260, 60)
        self.button_congratulation.move(10, 155)
        self.button_congratulation.pressed.connect(self.update_counter)

    # Этя функция нужна для обновления текста на
    # label с счетчиками. открывает ввод никнейма
    # и label счетчиков
    def update_counter(self):
        QWidget.show(self.label_text_hods)
        QWidget.show(self.label_text_timer)
        QWidget.show(self.label_text_name)
        QWidget.show(self.name_input)
        QWidget.show(self.button_save)
        self.label_text_hods.setText(f'Вы сняли всех лис за {LAST_HOD} ходов.')
        self.label_text_timer.setText(f'На это вы потратили {N_SECS} секунд.')
        self.label_text_name.setText(f'Введите своё имя (никнейм)')
        QWidget.hide(self.button_congratulation)
        QWidget.hide(self.label_text_con1)
        QWidget.hide(self.label_text_con2)

    # открытие поля с помощью show()
    def button_save_pressed(self):
        global LAST_HOD, N_SECS
        name = self.name_input.text()
        QWidget.hide(self.label_text_hods)
        QWidget.hide(self.label_text_timer)
        QWidget.hide(self.label_text_name)
        QWidget.hide(self.name_input)
        QWidget.hide(self.button_save)
        QWidget.show(self.button_congratulation)
        QWidget.show(self.label_text_con1)
        QWidget.show(self.label_text_con2)
        self.save_in_table('HighScoreTable.csv', name)

    # сохраняет в csv файл данные рекорда
    def save_in_table(self, table_name, name):
        global LAST_HOD, N_SECS
        with open(table_name, 'a', newline='', encoding="utf8") as csvfile:
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='"')
            current_datetime = datetime.now().date()
            day = current_datetime.day
            month = current_datetime.month
            year = current_datetime.year
            date = f'{day}.{month}.{year}'
            writer.writerow([name, LAST_HOD, N_SECS, date])
        self.hide_q.emit()


# Класс, что реализует дизайн, функцию победы,
# а также смену состояния игры
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.b_size, self.n_foxes = 10, 8

        w = QWidget()
        hb = QHBoxLayout()  # выстраивает виджеты по горизонтали

        self.setWindowTitle("Foxhunting")  # название игры
        self.setWindowIcon(QIcon("./images/fox.png"))  # Иконка

        self.foxes = QLabel()
        # Выравнивание по центру
        self.foxes.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.clock = QLabel()
        # Выравнивание по центру
        self.clock.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.hods = QLabel()
        # Выравнивание по центру
        self.hods.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        f = self.foxes.font()  # увеличение размера и *жирности* текста
        f.setPointSize(24)
        f.setWeight(75)
        self.foxes.setFont(f)
        self.clock.setFont(f)
        self.hods.setFont(f)

        self._timer = QTimer()  # время
        self._timer.timeout.connect(self.update_timer)
        self._timer.start(1000)

        self.foxes.setText("%03d" % self.n_foxes)
        self.clock.setText("000")
        self.hods.setText("%03d" % COUNTER_OF_HODS)

        self.button = QPushButton()
        self.button.setFixedSize(QSize(32, 32))
        self.button.setIconSize(QSize(32, 32))
        self.button.setIcon(QIcon("./images/smiley.png"))
        self.button.setFlat(True)

        self.button.pressed.connect(self.button_pressed)

        self.l1 = QLabel()
        self.l1.setPixmap(QPixmap.fromImage(IMG_FOX))
        self.l1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        hb.addWidget(self.l1)

        hb.addWidget(self.foxes)
        hb.addWidget(self.button)
        hb.addWidget(self.clock)

        self.l2 = QLabel()
        self.l2.setPixmap(QPixmap.fromImage(IMG_CLOCK))
        self.l2.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        hb.addWidget(self.l2)

        hb.addWidget(self.hods)

        self.l3 = QLabel()
        self.l3.setPixmap(QPixmap.fromImage(IMG_HODS))
        self.l3.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        hb.addWidget(self.l3)

        self.vb = QVBoxLayout()  # выстраивает виджеты по вертикали
        self.vb.addLayout(hb)

        self.grid = QGridLayout()  # сеточный (табличный) макет
        self.grid.setSpacing(5)  # промежуток 5
        self.grid.setSizeConstraint(QLayout.SetFixedSize)  # заполнение размером в 20

        self.vb.addLayout(self.grid)
        w.setLayout(self.vb)
        self.setCentralWidget(w)
        self.positions = [[0] * 10 for _ in range(10)]

        self.high_score_table = QAction(self)
        self.high_score_table.setText('Таблица рекордов')
        self.high_score_table.triggered.connect(self.table)
        self.menuBar().addAction(self.high_score_table)

        self.qtable = QHighScoreTable()

        self.qsavecsv = QSaveCSV()

        self.init_map()
        self.update_status(STATUS_READY)

        self.reset_map()
        self.update_status(STATUS_READY)

        self.show()

    # Инициализируем карту.
    def init_map(self):
        global COUNTER_OF_FOXES, COUNTER_OF_HODS, LAST_COUNTER_OF_HODS, \
            N_SECS, LAST_HOD
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = Pos(x, y)
                self.grid.addWidget(w, x, y)
                self.positions = [[0] * 10 for _ in range(10)]
                COUNTER_OF_FOXES = 0
                COUNTER_OF_HODS = 0
                N_SECS = 0
                LAST_HOD = 0
                LAST_COUNTER_OF_HODS = COUNTER_OF_HODS
                # Подключаем сигнал для обработки начала.
                w.clicked.connect(self.trigger_start)
                w.update_hods.connect(self.update_hods)
                w.win.connect(self.game_won)
                w.revealed.connect(self.on_reveal)

    # Показывает Таблицу Рекордов и обновляет её
    def table(self):
        self.qtable.loadTable('HighScoreTable.csv')
        self.qtable.show()

    # Главная функция reset_map вызывает функции для настройки
    def reset_map(self):
        self._reset_position_data()
        self._reset_add_foxes()
        self._reset_calculate_checked()
        self._reset_add_starting_marker()
        self.update_timer()

    # Очистка всех позиций лис, очистка всех счетчиков
    def _reset_position_data(self):
        global COUNTER_OF_FOXES, COUNTER_OF_HODS, LAST_COUNTER_OF_HODS, \
            N_SECS, LAST_HOD
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = self.grid.itemAtPosition(x, y).widget()
                w.reset()
        COUNTER_OF_FOXES = 0
        COUNTER_OF_HODS = 0
        N_SECS = 0
        LAST_HOD = 0
        LAST_COUNTER_OF_HODS = COUNTER_OF_HODS
        self.positions = [[0] * 10 for _ in range(10)]

    # Добавляем позиции лис.
    def _reset_add_foxes(self):
        positions = []
        while len(positions) < self.n_foxes:
            x, y = random.randint(0, self.b_size - 1), random.randint(0, self.b_size - 1)
            if (x, y) not in positions:
                w = self.grid.itemAtPosition(x, y).widget()
                w.is_fox = True
                positions.append((x, y))
                # обрабатываем список списков с цифрами
                for i in range(10):
                    for j in range(10):
                        if i == x and j == y:
                            self.positions[i][j] = 9
                        elif i != x and j == y and self.positions[i][j] != 9:
                            self.positions[i][j] += 1
                        elif i == x and j != y and self.positions[i][j] != 9:
                            self.positions[i][j] += 1
                        elif abs(i - x) == abs(j - y) and self.positions[i][j] != 9:
                            self.positions[i][j] += 1

    # заполняем клетками карту (с цифрами)
    def _reset_calculate_checked(self):
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = self.grid.itemAtPosition(x, y).widget()
                w.check_n = self.positions[x][y]

    # Размещение стартового маркера.
    def _reset_add_starting_marker(self):

        # Устанавливаем начальный статус (нужно для функции .click)
        self.update_status(STATUS_READY)

    # при нажатии на кнопку self.button статус
    # должен измениться
    def button_pressed(self):
        if self.status == STATUS_PLAYING:
            self.update_status(STATUS_FAILED)
            self.reveal_map()

        elif self.status == STATUS_FAILED:
            self.update_status(STATUS_READY)
            self.reset_map()

        elif self.status == STATUS_SUCCESS:
            self.update_status(STATUS_READY)
            self.reset_map()

    # открытие всего поля
    def reveal_map(self):
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = self.grid.itemAtPosition(x, y).widget()
                w.reveal()

    # инициализация начала
    def trigger_start(self, *args):
        if self.status == STATUS_READY:
            # Первое нажатие.
            self.update_status(STATUS_PLAYING)
            # Запуск таймера.
            self._timer_start_nsecs = int(time.time())

    # обновление статуса игры и иконки
    def update_status(self, status):
        self.status = status
        self.button.setIcon(QIcon(STATUS_ICONS[self.status]))

    # обновление времени
    def update_timer(self):
        global N_SECS
        if self.status == STATUS_PLAYING:
            n_secs = int(time.time()) - self._timer_start_nsecs
            N_SECS = n_secs
            self.clock.setText("%03d" % n_secs)

    # обновление счетчика ходов
    def update_hods(self):
        if self.status == STATUS_PLAYING:
            global COUNTER_OF_HODS
            self.hods.setText("%03d" % COUNTER_OF_HODS)

    # определение победы
    def on_reveal(self, w):
        if COUNTER_OF_FOXES == 8:
            self.game_won()

    # открытие окна для ввода никнейма
    # в случае занесение результата в таблицу рекордов
    def open_QSaveCSV(self):
        self.qsavecsv.show()
        self.qsavecsv.hide_q.connect(self.hide_window)

    # скрывает окно класса QSaveCSV
    def hide_window(self):
        self.qsavecsv.hide()

    # определение победы
    def game_won(self):
        global COUNTER_OF_HODS, N_SECS, LAST_HOD
        LAST_HOD = COUNTER_OF_HODS
        self.reveal_map()
        self.update_status(STATUS_SUCCESS)
        if LAST_HOD <= 40 and N_SECS <= 3600:
            self.open_QSaveCSV()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
