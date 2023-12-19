from __future__ import annotations

import os

from common import *


class Direction:
    COMPASS: list[Direction] = []
    REVERSE: dict[Direction, Direction] = {}

    def __init__(self, name: str, dr: int, dc: int, compass: bool = False):
        self.name: str = name
        self.delta: GridDirection = GridDirection(dr, dc)
        self.cardinal = compass

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash((self.name, self.delta))

    def __eq__(self, other: Direction) -> bool:
        return self.name == other.name and self.delta == other.delta


NORTH = Direction('north', -1, 0, True)
EAST = Direction('east', 0, 1, True)
SOUTH = Direction('south', 1, 0, True)
WEST = Direction('west', 0, -1, True)

Direction.COMPASS.extend([NORTH, EAST, SOUTH, WEST])
Direction.REVERSE.update({NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST})


class Pipe:
    PIPES: dict[str, Pipe] = {}
    LEFT: list[Pipe] = []
    RIGHT: list[Pipe] = []
    INSIDE: list[Pipe] = []

    def __init__(self, name: str, symbol: str, *directions: str):
        self.name: str = name
        self.symbol: int = ord(symbol)
        self.directions: list[Direction] = directions

    def matches(self, directions: list[Direction]) -> bool:
        return all([d in self.directions for d in directions])


NS = Pipe('ne', b'|', NORTH, SOUTH)
EW = Pipe('ew', b'-', EAST, WEST)
NW = Pipe('nw', b'F', SOUTH, EAST)
SW = Pipe('sw', b'L', NORTH, EAST)
NE = Pipe('ne', b'7', SOUTH, WEST)
SE = Pipe('se', b'J', NORTH, WEST)
DOT = Pipe('dot', b'.')
START = Pipe('start', b'S')

Pipe.PIPES = {s.symbol: s for s in [NS, EW, SW, SE, NE, NW]}
Pipe.RIGHT = [p.symbol for p in [NS, NW, SW]]
Pipe.LEFT = [p.symbol for p in [NS, NE, SE]]
Pipe.INSIDE = [p.symbol for p in [NS, NE, NW]]


class PipeMaze:

    def __init__(self, data: list[bytearray], path: bool = False):
        self.grid: list[bytearray] = data
        self.path = [bytearray(' '*self.cols, 'utf-8')
                     for row in range(self.rows)] if path else None

        self.start: GridPosition
        self.loop: list[GridPosition]

        self.find_start()
        self.find_loop()

    @property
    def rows(self):
        return len(self.grid)

    @property
    def cols(self):
        return len(self.grid[0])

    @cache
    def __getitem__(self, position: GridPosition) -> str:
        return self.grid[int(position.real)][int(position.imag)]

    def __setitem__(self, position: GridPosition, value: int) -> None:
        self.grid[int(position.real)][int(position.imag)] = value

    def find_start(self) -> None:
        for row, line in enumerate(self.grid):
            col = line.find(b'S')
            if col >= 0:
                self.start = GridPosition(row, col)

                directions = []
                for direction in Direction.COMPASS:
                    try:
                        neighbor = self.start+direction.delta
                        cell = self[neighbor]
                        if cell in Pipe.PIPES:
                            reverse = Direction.REVERSE[direction]
                            if reverse in Pipe.PIPES[cell].directions:
                                directions.append(direction)
                    except IndexError:
                        pass

                for pipe in Pipe.PIPES.values():
                    if pipe.matches(directions):
                        self[self.start] = pipe.symbol
                        if self.path:
                            self.path[row][col] = pipe.symbol
                        break
                else:
                    print('Did not match starting symbol')

                return
        raise ValueError('No start cell in maze')

    def find_loop(self) -> None:
        self.loop = [self.start]

        direction = Pipe.PIPES[self[self.start]].directions[0]
        neighbor = self.start + direction.delta
        while neighbor not in self.loop:
            self.loop.append(neighbor)
            if self.path:
                self.path[int(neighbor.real)][int(neighbor.col)
                                              ] = Pipe.PIPES[self[neighbor]].symbol

            next = self.leaving(neighbor, direction)
            neighbor = neighbor + next.delta
            direction = next

    def leaving(self, position: GridPosition, entering: Direction) -> Direction:
        directions = Pipe.PIPES[self[position]].directions
        return directions[1] if directions[0] == Direction.REVERSE[entering] else directions[0]

    def farthest(self) -> int:
        return len(self.loop) // 2

    def inside(self) -> int:
        inside = 0

        for row in range(self.rows):
            interior = False
            for col, symbol in enumerate(self.grid[row]):
                pos = GridPosition(row, col)
                if pos in self.loop:
                    if symbol in Pipe.INSIDE:
                        interior = not interior
                elif interior:
                    inside += 1
                    if self.path:
                        self.path[int(pos.real)][int(pos.imag)] = ord('I')

        return inside


class Day10(Puzzle):
    """Pipe Maze"""

    pretty = str.maketrans("-|F7LJ", "─│╭╮╰╯")

    def parse_data(self, filename: str) -> Data:
        maze = PipeMaze(self.read_bytearrays(filename), False)
        return maze

    def dump(self, data: PipeMaze, extension: str = '.maze', filename: str = None) -> None:
        mazename = filename or self.currentfile
        mazename = mazename.replace('.data', extension)
        mazepath = os.path.join(self.base, mazename)
        with open(mazepath, 'w') as mf:
            for raw in data.path:
                line = raw.decode('utf-8').translate(self.pretty)
                mf.write(line)
                mf.write('\n')

    def part1(self, data: PipeMaze) -> PuzzleResult:
        return data.farthest()

    def part2(self, data: PipeMaze) -> PuzzleResult:
        inside = data.inside()
        if data.path:
            self.dump(data, '.inside')
        return inside


puzzle = Day10('real.data', 'test1.data', 'test2.data',
               'test3.data', 'test4.data', 'test5.data', 'test6.data')
puzzle.run(
    [4, 8, None, None, None, None],
    [1, 1, 4, 4, 8, 10],
    testonly=False
)
