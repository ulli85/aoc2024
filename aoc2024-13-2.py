import numpy as np
import re


class Btn:

    def __init__(self, label: str, x_diff: int, y_diff: int):
        self.label = label
        self.cost = 3 if label == 'A' else 1
        self.x_diff = x_diff
        self.y_diff = y_diff

    def __str__(self):
        return f"{self.label}: x={self.x_diff} y={self.y_diff} \n"

    def click(self, times):
        if times < 0:
            raise Exception(f"Negative click {times}")
        return [self.x_diff * times, self.y_diff * times]

    def get_cost(self, times):
        return self.cost * times

    @staticmethod
    def parse(btn: str):
        res = re.findall("^Button (A|B): X([+-]\\d+), Y([+-]\\d+)$", btn)
        return Btn(res[0][0], int(res[0][1]), int(res[0][2]))


class Prize:
    def __init__(self, prize_x: int, prize_y: int):
        self.prize_x = prize_x
        self.prize_y = prize_y

    def __str__(self):
        return f"Prize: X={self.prize_x} Y={self.prize_y} \n"

    @staticmethod
    def parse(prize: str):
        res = re.findall("^Prize: X=(\\d+), Y=(\\d+)$", prize)
        return Prize(10000000000000 + int(res[0][0]), 10000000000000 + int(res[0][1]))


class Combination:
    def __init__(self, btn_a: Btn, a_clicks: int, btn_b: Btn, b_clicks: int):
        self.a_clicks, self.b_clicks = a_clicks, b_clicks
        self.prize_x, self.prize_y = np.add(btn_a.click(a_clicks), btn_b.click(b_clicks))

    def __str__(self):
        return f"Combination: A x {self.a_clicks}  B x {self.b_clicks}"

    def is_winning(self, machine: 'Machine') -> bool:
        return [machine.prize.prize_x, machine.prize.prize_y] == [self.prize_x, self.prize_y]

    def get_cost(self, machine: 'Machine') -> int:
        return machine.btn_a.get_cost(self.a_clicks) + machine.btn_b.get_cost(self.b_clicks)

    @staticmethod
    def find_combinations(machine: 'Machine'):
        ax = machine.btn_a.x_diff
        bx = machine.btn_b.x_diff
        prize_x = machine.prize.prize_x

        ay = machine.btn_a.y_diff
        by = machine.btn_b.y_diff
        prize_y = machine.prize.prize_y

        b1 = int((prize_y * ax - (prize_x * ay)) / (-bx * ay + by * ax))
        a1 = int((prize_y - b1 * by) / ay)

        a2 = int((prize_x * by - (prize_y * bx)) / (ax * by - ay * bx))
        b2 = int((prize_x - a2 * ax) / bx)

        for clicks in [[a1, b1], [a2, b2]]:
            if clicks[0] >= 0 and clicks[1] >= 0:
                combination = Combination(machine.btn_a, clicks[0], machine.btn_b, clicks[1])
                if combination.is_winning(machine):
                    machine.winning_combinations.append(combination)
            else:
                print(f"Negative solution: A = {clicks[0]} B = {clicks[1]}")
        # ------solution 1 ----------
        # 1 |a1 * ax + b1 * bx = prize_x / * -ay
        # 2 |a1 * ay + b1 * by = prize_y / * ax
        # -------------------------
        # 1 |-a1 * ax * ay - b1 * bx * ay = -(prize_x * ay)
        # 2 | a1 * ax * ay + b1 * by * ax = prize_y * ax
        # --------------------------
        # 1 + 2 | b1 * (-bx * ay + by * ax) = prize_y * ax -(prize_x * ay) / : (-bx * ay + by * ax)
        # b1 = (prize_y * ax -(prize_x * ay)) / (-bx * ay + by * ax) ===> solution b
        # a1 = (prize_y - b1 * by) / ay ==> solution ===> solution a

        # --------- solution 2 ---------
        # 1 |a2 * ax + b2 * bx = prize_x / * by
        # 2 |a2 * ay + b2 * by = prize_y / * -bx
        # -------------------------
        # 1 |a2 * ax * by + b2 * bx * by = prize_x * by
        # 2 |-a2 * ay * bx - b2 * by * bx = -(prize_y * bx)
        # -------------------------
        # 1 + 2 | a2 * ax * by - a2 * ay * bx = prize_x * by -(prize_y * bx)
        # a2 = (prize_x * by -(prize_y * bx)) / (ax * by - ay * bx)
        # b2 = (prize_x - a2 * ax) / bx


class Machine:

    def __init__(self, btn_a: str, btn_b: str, prize: str):
        self.btn_a = Btn.parse(btn_a)
        self.btn_b = Btn.parse(btn_b)
        self.prize = Prize.parse(prize)
        self.winning_combinations_searched = False
        self.winning_combinations: ['Combination'] = []

    def __str__(self):
        return (f"{self.btn_a}"
                f"{self.btn_b}"
                f"{self.prize}"
                f"{"None" if not self.possible_2_win() else self.get_winning()}")

    def possible_2_win(self):
        if self.winning_combinations_searched:
            return len(self.winning_combinations) > 0
        self.winning_combinations_searched = True
        Combination.find_combinations(self)
        return len(self.winning_combinations) > 0

    def get_winning(self):
        if self.possible_2_win():
            min_cost = 99999999999999999
            best = self.winning_combinations[0]
            for combination in self.winning_combinations:
                if (combination.get_cost(self) < min_cost):
                    best = combination
            return best
        raise Exception('Not winning combination!')

    def get_tokens(self):
        if self.possible_2_win():
            combination = self.get_winning()
            return combination.get_cost(self)
        raise Exception('Not winning combination!')


f = open("aoc2024-13-1-input.txt", "r")
input = f.read().splitlines()
min_tokens = 0
for i in range(0, int((len(input) + 1)), 4):
    machine = Machine(input[i], input[i + 1], input[i + 2])
    if machine.possible_2_win():
        min_tokens += machine.get_tokens()
        print(machine)
print(min_tokens)