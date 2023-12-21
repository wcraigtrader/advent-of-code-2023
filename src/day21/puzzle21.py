from __future__ import annotations

from typing import Optional

from common import *

DIRECTIONS = [
    GridDirection(1, 0),
    GridDirection(0, 1),
    GridDirection(-1, 0),
    GridDirection(0, -1),
]


class Garden:

    def __init__(self, lines: str | list[str]):
        if isinstance(lines, str):
            lines = lines.split('\n')

        self.rows = range(len(lines))
        self.cols = range(len(lines[0]))
        self.start: GridPosition
        self.rocks: list[GridPosition] = []

        for row, line in enumerate(lines):
            for col, ch in enumerate(line):
                if ch == 'S':
                    self.start = GridPosition(row, col)
                elif ch == '#':
                    self.rocks.append(GridPosition(row, col))

    def valid(self, position: GridPosition, infinite: bool) -> bool:
        if infinite:
            row = GridRow(position) % self.rows.stop
            col = GridCol(position) % self.cols.stop
            return GridPosition(row, col) not in self.rocks
        else:
            return (GridRow(position) in self.rows and
                    GridCol(position) in self.cols and
                    position not in self.rocks)

    def one_step(self, previous: set[GridPosition], infinite: bool = False) -> set(GridPosition):
        reachable: set(GridPosition) = set()

        for position in previous:
            for direction in DIRECTIONS:
                potential = position + direction
                if self.valid(potential, infinite):
                    reachable.add(potential)

        return reachable

    def steps(self, steps: int, infinite: bool = False) -> int:
        positions = {self.start}

        for i in range(1, steps+1):
            positions = self.one_step(positions, infinite)
            # print(i, len(positions))

        return len(positions)


class Day21(Puzzle):
    """Step Counter"""

    def parse_data(self, filename: str) -> Data:
        return Garden(self.read_stripped(filename))

    def part1(self, data: Data) -> PuzzleResult:
        return data.steps(64)

    def part2(self, data: Data) -> PuzzleResult:
        return data.steps(26_501_365, True)


puzzle = Day21()
puzzle.run(42, 167409079868000)
