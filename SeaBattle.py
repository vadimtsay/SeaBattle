from random import randint

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

#     def shooten(self, shot):
#         return shot in self.dots


class Board:
    def __init__(self, hid=True, size=6, line = 0):
        self.size = size
        self.hid = hid
        self.line = line
        self.count = 0
        self.i = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)
    def print_file(self, init):
        # with open('test.txt', "w+") as f:
        #     i = sum(1 for _ in f)
        if init == 1:
            if self.i == 0:
                data_file = open('test.txt', 'w+', encoding="utf-8")
                data_file.seek(0)
                data_file.close()
                self.i += self.i
            data_file = open("test.txt", "a+", encoding="utf-8")
            data_file.write("%s\n" % (self.field))
            if self.hid:
               data_file.write("%s\n" % str(self.field).replace("■", "O"))
            data_file.close()
        elif init == 0:
            with open("test.txt", "r", encoding="utf-8") as f:
                first = f.readline()
                second = f.readline()
            with open("test.txt", "r", encoding="utf-8") as f:
                old_file = f.read()
                new_first = old_file.replace(first, "%s\n" % self.field)
                new_second = old_file.replace(second, "%s\n" % str(self.field).replace("■", "O"))
            with open("test.txt", "w", encoding="utf-8") as f:
                if self.line == 0:
                    f.write(new_first)
                elif self.line == 1:
                    f.write(new_second)
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                self.print_file(0)
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    self.print_file(0)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "T"
        self.print_file(0)
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        pl.line = 0
        co = self.random_board()
        co.hid = True
        co.line = 1

        self.ai = AI(co, pl)
        self.us = User(pl, co)
    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.print_file(1)
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветствуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def print_boards(self):
        f = open("test.txt", "r", encoding="utf-8")
        l1 = f.readline()
        l2 = f.readline()
        lst1 = eval(l1)
        lst2 = eval(l2)
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |" + " "*5 + "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(lst1):
            res += "             "
            res += f"\n{i + 1} | " + " | ".join(row) + " |"
            for j, row1 in enumerate(lst2):
                if j == i:
                    res += f"     {i + 1} | " + " | ".join(row1) + " |"
        print(res)
    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:             Доска компьютера:")
            print("-" * 20 + " " * 12 + "-" * 20)
            s = self
            self.print_boards()
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")

                break
            num += 1

    def start(self):
        self.greet()
        self.loop()
g = Game()
g.start()
