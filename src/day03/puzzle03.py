from __future__ import annotations

from typing import Iterator

from common import *

DOT = '.'
GEAR = '*'
DIGITS = '0123456789'
DIGITS_OR_DOT = DIGITS + DOT


@dataclass(frozen=True)
class Position:
    row: int
    col: int


@dataclass(frozen=True)
class Part:
    number: int
    left: Position
    right: Position

    def __mul__(self, other) -> int:
        return self.number * other.number

    @classmethod
    def parse(cls, text: str, left: Position) -> "Part":
        n = int(text)
        l = left
        r = Position(l.row, l.col+len(text)-1)
        return cls(n, l, r)


@dataclass
class Schematic:
    lines: list[str]

    parts: list[Part] = field(default_factory=list)
    symbols: dict[Position, str] = field(default_factory=dict)
    gears: dict[Position, list[Part]] = field(default_factory=dict)

    def __getitem__(self, pos: Position) -> str:
        return self.lines[pos.row][pos.col]

    @cached_property
    def max_r(self):
        return len(self.lines)

    @cached_property
    def max_c(self):
        return len(self.lines[0])

    def add_part(self, token: str, pos: Position) -> None:
        if len(token):
            part = Part.parse(token, pos)
            if self.valid_part(part):
                self.parts.append(part)

    def add_symbol(self, pos: Position, ch: str) -> None:
        if pos not in self.symbols:
            self.symbols[pos] = ch

    def add_gear(self, pos: Position, part: Part) -> None:
        parts = self.gears.setdefault(pos, list())
        if part not in parts:
            parts.append(part)

    def valid_position(self, pos: Position) -> bool:
        return (0 <= pos.row < self.max_r and 0 <= pos.col < self.max_c)

    def adjacent(self, part: Part) -> Iterator[Position]:
        for col in (part.right.col+1, part.left.col-1):
            pos = Position(part.left.row, col)
            if self.valid_position(pos):
                yield pos
        for col in range(part.left.col-1, part.right.col+2, 1):
            for row in (part.left.row-1, part.left.row+1):
                pos = Position(row, col)
                if self.valid_position(pos):
                    yield pos

    def valid_part(self, part) -> bool:
        result = False

        for pos in self.adjacent(part):
            ch = self[pos]
            if ch == GEAR:
                self.add_gear(pos, part)
                self.add_symbol(pos, ch)
                result = True
            elif ch not in DIGITS_OR_DOT:
                self.add_symbol(pos, ch)
                result = True

        return result

    def parse(self) -> None:
        pos: Position = None
        for row, line in enumerate(self.lines):
            token = ''
            for col in range(len(line)):
                ch = line[col]
                if ch in DIGITS:
                    if not token:
                        pos = Position(row, col)
                        token = ch
                    else:
                        token += ch
                elif ch == DOT and token:
                    self.add_part(token, pos)
                    token = ''
                elif ch != DOT:
                    self.add_symbol(Position(row, col), ch)
                    self.add_part(token, pos)
                    token = ''
            self.add_part(token, pos)

    def __post_init__(self):
        self.parse()


class Day03(Puzzle):
    """Gear Ratios"""
    
    def parse_data(self, filename) -> Schematic:
        lines = self.read_stripped(filename)
        return Schematic(lines)

    def part1(self, data) -> int:
        return sum(part.number for part in data.parts)

    def part2(self, data) -> int:
        return sum([parts[0]*parts[1]
                    for parts in data.gears.values()
                    if len(parts) == 2])


puzzle = Day03()
puzzle.run(4361, 467835)
