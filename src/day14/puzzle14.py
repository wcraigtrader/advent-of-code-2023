from __future__ import annotations

from common import *

NORTH = GridDirection(1, 0)
SOUTH = GridDirection(-1, 0)
EAST = GridDirection(0, 1)
WEST = GridDirection(0, -1)

DOT = '.'
FIXED = '#'
ROUNDED = 'O'


class Platform(Grid):

    def __init__(self, lines):
        super().__init__(lines, origin='ll', offset=1, sparse=True)

    def slide(self, position: GridPosition, direction: GridDirection) -> None:
        if self[position] == ROUNDED:
            next = position + direction
            while self.inbounds(next) and self[next] == DOT:
                self[next] = self[position]
                self[position] = DOT
                position, next = next, next + direction

    def tilt(self, direction: GridDirection) -> None:
        if direction == NORTH:  # Rows 9-1, all columns
            for row in reversed(self.row_range[:-1]):
                for col in self.col_range:
                    self.slide(GridPosition(row, col), direction)
        elif direction == SOUTH:  # Rows 2-10, all columns
            for row in self.row_range[1:]:
                for col in self.col_range:
                    self.slide(GridPosition(row, col), direction)
        elif direction == EAST:  # Cols 9-1, all rows
            for col in reversed(self.col_range[:-1]):
                for row in self.row_range:
                    self.slide(GridPosition(row, col), direction)
        elif direction == WEST:  # Cols 2-10, all rows
            for col in self.col_range[1:]:
                for row in self.row_range:
                    self.slide(GridPosition(row, col), direction)

    def spin(self, cycles: int) -> None:
        history = []
        for i in range(1, cycles+1):
            for direction in [NORTH, WEST, SOUTH, EAST]:
                self.tilt(direction)

    def load_score(self, orientation: GridDirection, position: GridPosition) -> int:
        if orientation == NORTH:
            return int(position.real)
        elif orientation == EAST:
            return int(position.imag)
        elif orientation == SOUTH:
            return self.offset + self.rows - int(position.real)
        elif orientation == WEST:
            return self.offset + self.cols - int(position.imag)
        return 0

    def load(self, orientation: GridDirection) -> int:
        return sum([self.load_score(orientation, GridPosition(row, col))
                    for col in self.col_range
                    for row in self.row_range
                    if self[GridPosition(row, col)] == ROUNDED])


class Day14(Puzzle):
    """Parabolic Reflector Dish"""

    def parse_data(self, filename: str) -> Data:
        return Platform(self.read_stripped(filename))

    def part1(self, platform: Platform) -> PuzzleResult:
        platform.tilt(NORTH)
        load = platform.load(NORTH)
        return load

    def part2(self, platform: Platform) -> PuzzleResult:
        platform.spin(1_000)
        return platform.load(NORTH)


puzzle = Day14()
puzzle.run(136, 64, testonly=True)  # 95254 in 210 seconds
