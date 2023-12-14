from __future__ import annotations

from collections import Counter
from typing import Generator

from common import *


class Reflections:

    def __init__(self, lines: list[str]):
        self.lines: list[str] = lines

        self.horizontal: Grid = Grid(lines)
        self.vertical: Grid = Grid(lines, transpose=True)

    def __repr__(self) -> str:
        return f'Grid({self.horizontal._rows}x{self.horizontal._cols})'

    def mirror_rows(self, grid: Grid) -> Generator[tuple[range, range]]:
        """
        Example: 9 rows of 7 cols:

        Row combinations:
        [0:1 <> 1:2], [0:2 <> 2:4], [0:3 <> 3:6], [0:4 <> 4:8],
        [1:5 <> 5:9], [3:6 <> 6:9], [5:7 <> 7:9], [7:8 <> 8:9],

        Column combinations:
        [0:1 <> 1:2], [0:2 <> 2:4], [0:3 <> 3:6],
        [1:4 <> 4:7[, [3:5 <> 5:7], [5:6 <> 6:7],
        """
        r = grid._rows
        for i in range(1, r//2+1):
            left = range(0, i)
            right = range(2*i-1, i-1, -1)
            yield (left, right)
        for i in range(1, r//2+1):
            left = range(r-2*i, r-i)
            right = range(r-1, r-i-1, -1)
            yield (left, right)

    def reflection(self, grid, margin=0) -> int:
        errors = Counter()

        for left_set, right_set in self.mirror_rows(grid):
            index = left_set.stop
            errors[index] = 0
            for left, right in zip(left_set, right_set):
                if errors[index] > margin:
                    break
                for l, r in zip(grid.row(left), grid.row(right)):
                    if l != r:
                        errors[index] += 1
                    if errors[index] > margin:
                        break

        matches = [k for k, v in errors.items() if v == margin]

        return matches[0] if len(matches) else 0

    def measure(self, margin: int) -> int:
        reflect = self.reflection(self.horizontal, margin) * 100
        reflect = reflect if reflect else self.reflection(
            self.vertical, margin)
        return reflect


class Day13(Puzzle):
    """Point of Incidence"""

    def parse_data(self, filename: str) -> Data:
        lines = self.read_stripped(filename)

        reflections = []
        start = 0
        for pos, line in enumerate(lines):
            if line == '':
                reflections.append(Reflections(lines[start:pos]))
                start = pos+1
        reflections.append(Reflections(lines[start:]))
        return reflections

    def part1(self, data: Data) -> PuzzleResult:
        return sum([reflections.measure(0) for reflections in data])

    def part2(self, data: Data) -> PuzzleResult:
        return sum([reflections.measure(1) for reflections in data])


puzzle = Day13()
puzzle.run(405, 400)
