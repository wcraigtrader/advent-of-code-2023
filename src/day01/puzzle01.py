from __future__ import annotations

import re

from common import *

digits = '123456789'
words = {
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
}


class Day01(Puzzle):
    """Trebuchet?"""
    
    def parse_data(self, filename) -> list[str]:
        return self.read_stripped(filename)

    def find(self, pattern, line) -> tuple:
        left = pattern.search(line).group(0)
        for pos in range(len(line)-1, -1, -1):
            s = pattern.search(line, pos)
            if s:
                right = s.group(0)
                break
        return (left, right)

    def calculate1(self, data: list[str], pattern: re.Pattern) -> list[int]:
        numbers = [pattern.findall(line) for line in data]
        calibration = [10*words[row[0]] + words[row[-1]] for row in numbers]

        return calibration

    def calculate2(self, data: list[str], pattern: re.Pattern) -> list[int]:
        numbers = [self.find(pattern, line) for line in data]
        calibration = [10*words[row[0]] + words[row[-1]] for row in numbers]

        return calibration

    def compare(self, data: list[str], pattern: re.Pattern) -> None:
        c1 = self.calculate1(data, pattern)
        c2 = self.calculate2(data, pattern)

        for i, (x1, x2, line) in enumerate(zip(c1, c2, data)):
            if x1 != x2:
                print(f'{i:4d}: {x1:2d} {x2:2d} <- {line}')

    def part1(self, data) -> int:
        pattern = re.compile("|".join(digits))
        # self.compare(data, pattern)
        return sum(self.calculate2(data, pattern))

    def part2(self, data) -> int:
        pattern = re.compile("|".join(words.keys()))
        # self.compare(data, pattern)
        return sum(self.calculate2(data, pattern))


puzzle = Day01('real.data', 'test1.data', 'test2.data')
puzzle.run([142, None], [None, 281])
