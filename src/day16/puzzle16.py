from __future__ import annotations

from collections import Counter
from enum import Enum

from common import *


class Direction(Enum):
    UP = GridDirection(-1, 0)
    DOWN = GridDirection(1, 0)
    RIGHT = GridDirection(0, 1)
    LEFT = GridDirection(0, -1)


@dataclass(frozen=True)
class Path:

    position: GridPosition
    direction: Direction

    def __add__(self, direction: Direction) -> Path:
        if isinstance(direction, Direction):
            return Path(self.position + direction.value, direction)
        raise ValueError('Cannot add {direction} to {self}')

    def __repr__(self) -> str:
        return f'{self.direction.name} from {self.position}'


MIRROR: dict[str, dict[Direction: Direction]] = {
    '/': {
        Direction.RIGHT: Direction.UP,
        Direction.LEFT: Direction.DOWN,
        Direction.UP: Direction.RIGHT,
        Direction.DOWN: Direction.LEFT,
    },
    '\\': {
        Direction.RIGHT: Direction.DOWN,
        Direction.LEFT: Direction.UP,
        Direction.UP: Direction.LEFT,
        Direction.DOWN: Direction.RIGHT,
    },
}

SPLITTER = {
    '|': {
        Direction.RIGHT: [Direction.UP, Direction.DOWN],
        Direction.LEFT: [Direction.UP, Direction.DOWN],
    },
    '-': {
        Direction.UP: [Direction.RIGHT, Direction.LEFT],
        Direction.DOWN: [Direction.RIGHT, Direction.LEFT],
    },
}


class Cave(Grid):

    def __init__(self, lines):
        super().__init__(lines)

        self.counts = Counter()

    def energized(self, start: Path) -> int:
        if start in self.counts:
            return self.counts[start]

        energized: set[GridPosition] = set()
        beams: list[Path] = [start]
        history: set[Path] = set()

        while len(beams):
            turn1 = turn2 = None

            path = beams.pop(0)
            if path in history:
                continue

            history.add(path)
            energized.add(path.position)

            device = self[path.position]
            if device in MIRROR:
                turn1 = path + MIRROR[device][path.direction]
                beams.extend(self.valid(turn1))
            elif device in SPLITTER and path.direction in SPLITTER[device]:
                turn1 = path + SPLITTER[device][path.direction][0]
                turn2 = path + SPLITTER[device][path.direction][1]
                beams.extend(self.valid(turn1, turn2))
            else: # just keep swimming
                beams.extend(self.valid(path + path.direction))

        self.counts[start] = len(energized)
        return self.counts[start]

    def valid(self, *paths: Path) -> list[Path]:
        valid = [p for p in paths if self.inbounds(p.position)]
        return valid

    def max_power(self):
        for row in self.row_range:
            self.energized(Path(GridPosition(row, 0), Direction.RIGHT))
            self.energized(Path(GridPosition(row, self.cols-1), Direction.LEFT))

        for col in self.col_range:
            self.energized(Path(GridPosition(0, col), Direction.DOWN))
            self.energized(Path(GridPosition(self.rows-1, col), Direction.UP))

        return max(self.counts.values())


class Day16(Puzzle):
    """The Floor Will Be Lava"""
    def parse_data(self, filename: str) -> Data:
        return Cave(self.read_stripped(filename))

    def part1(self, data: Data) -> PuzzleResult:
        return data.energized(Path(GridPosition(0, 0), Direction.RIGHT))

    def part2(self, data: Data) -> PuzzleResult:
        return data.max_power()


puzzle = Day16()
puzzle.run(46, 51)
