from __future__ import annotations

import os
import re
from enum import Enum
from itertools import pairwise
from operator import attrgetter

from common import *

INFINITY = 999_999_999


class Direction(Enum):
    U = GridDirection(-1, 0)
    D = GridDirection(1, 0)
    R = GridDirection(0, 1)
    L = GridDirection(0, -1)


@dataclass
class Boundaries:
    walls: set[int] = field(default_factory=set)
    runs: set[range] = field(default_factory=set)


@dataclass
class Step:
    direction: GridDirection
    distance: int
    color: int

    def __repr__(self) -> str:
        return f'{self.direction.name} {self.distance} #{self.color}'

    @classmethod
    def parse(cls, line) -> Step:
        match = re.match(r'([RLUD]) (\d+) \(#([0-9a-f]{6})\)', line)
        dir, dis, rgb = match.groups()
        return cls(Direction[dir], int(dis), rgb)


class Lagoon(Grid):

    def __init__(self, lines):
        super().__init__(sparse=True, dynamic=True)
        self.steps: list[Step] = [Step.parse(line) for line in lines]
        self.bounds: dict[int, Boundaries] = {}

    def load_grid_from_steps(self) -> int:
        position = GridPosition(0, 0)
        self[position] = '#'

        for step in self.steps:
            for _ in range(step.distance):
                position = position + step.direction.value
                self[position] = '#'

        return len(self)

    def grid_fill(self) -> int:
        # https://en.wikipedia.org/wiki/Flood_fill

        queue: list[GridPosition] = []

        marking = False
        row = GridRow(self.center)
        for col in self.col_range:
            position = GridPosition(row, col)
            if not marking and position in self:
                marking = True
            elif marking and position not in self:
                queue.append(position)
                break

        while len(queue):
            node = queue.pop(0)
            self[node] = '#'
            for direction in Direction:
                next = node + direction.value
                if next not in self:
                    queue.append(next)

        return len(self)

    def load_bounds_from_steps(self) -> int:
        position = GridPosition(0, 0)
        self.bounds[0] = Boundaries({0})
        for step in self.steps:
            target = position + step.direction.value * step.distance

            if step.direction == Direction.U:
                col = GridCol(position)
                for row in range(GridRow(target), GridRow(position)+1):
                    self.bounds.setdefault(row, Boundaries()).walls.add(col)
            elif step.direction == Direction.D:
                col = GridCol(position)
                for row in range(GridRow(position), GridRow(target)+1):
                    self.bounds.setdefault(row, Boundaries()).walls.add(col)
            elif step.direction == Direction.R:
                run = range(GridCol(position), GridCol(target))
                self.bounds.setdefault(
                    GridRow(position), Boundaries()).runs.add(run)
            elif step.direction == Direction.L:
                run = range(GridCol(target), GridCol(position))
                self.bounds.setdefault(
                    GridRow(position), Boundaries()).runs.add(run)

            position = target

        return sum(step.distance for step in self.steps)

    def bounds_fill(self) -> int:
        count = 0

        for row, bounds in self.bounds.items():
            inside = False
            last = None
            for start, stop in pairwise(sorted(bounds.walls)):
                inside = not inside
                if range(start, stop) in bounds.runs:
                    inside = True
                if inside:
                    count += stop-start+1

        return count


class Day18(Puzzle):
    """Lavaduct Lagoon"""

    def parse_data(self, filename: str) -> Lagoon:
        return Lagoon(self.read_stripped(filename))

    def dump(self, data: Lagoon, extension: str = '.grid') -> None:
        with open(self.test_path(extension), 'w') as mf:
            mf.write(str(data))

    def part1(self, data: Lagoon) -> PuzzleResult:
        edges = data.load_bounds_from_steps()
        fills = data.bounds_fill()
        return fills

    def part2(self, data: Lagoon) -> PuzzleResult:
        return 0


puzzle = Day18()
puzzle.run(62)
