from __future__ import annotations

from itertools import combinations

from common import *


@dataclass
class Galaxy:
    row: int
    col: int

    def __sub__(self, other: Galaxy) -> int:
        return abs(other.row-self.row) + abs(other.col - self.col)


class Universe:

    def __init__(self, data: list[str]):
        self.data = data

    def expand(self, expanse: int) -> None:
        galaxies: list[Galaxy] = []

        rows, cols = set(), set()
        for row, line in enumerate(self.data):
            for col, spot in enumerate(line):
                if spot == '#':
                    galaxies.append(Galaxy(row, col))

        rows = set([galaxy.row for galaxy in galaxies])
        cols = set([galaxy.col for galaxy in galaxies])

        row_gap = set(range(max(rows)+1)) - rows
        col_gap = set(range(max(cols)+1)) - cols

        for gap in sorted(list(row_gap), reverse=True):
            for galaxy in galaxies:
                if galaxy.row > gap:
                    galaxy.row += expanse - 1

        for gap in sorted(list(col_gap), reverse=True):
            for galaxy in galaxies:
                if galaxy.col > gap:
                    galaxy.col += expanse - 1

        return galaxies


class Day11(Puzzle):
    """Cosmic Expansion"""
    
    def parse_data(self, filename: str) -> Data:
        return Universe(self.read_stripped(filename))

    def part1(self, data: Universe) -> PuzzleResult:
        galaxies = data.expand(2)
        pairs = list(combinations(galaxies, 2))
        result = sum([y-x for x, y in pairs])
        return result

    def part2(self, data: Universe) -> PuzzleResult:
        galaxies = data.expand(1_000_000)
        pairs = list(combinations(galaxies, 2))
        result = sum([y-x for x, y in pairs])
        return result


puzzle = Day11()
puzzle.run(374, IGNORE)
