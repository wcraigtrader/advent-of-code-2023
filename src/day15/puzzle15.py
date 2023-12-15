from __future__ import annotations

from functools import reduce
from operator import itemgetter

from common import *


@dataclass
class Lens:
    label: str
    box: int
    length: int

    def __repr__(self) -> str:
        return f'{self.label} {self.length}'


class Operation:

    def __init__(self, line):
        self.line: str = line
        self.linehash: int = self.hash(line)
        self.label: str
        self.box: int
        self.op: str
        self.lens: Lens = None

        label, op, length = line.partition('-') \
            if line.endswith('-') \
            else line.partition('=')

        self.label = label
        self.box = self.hash(label)
        self.op = op
        if op == '=':
            self.lens = Lens(self.label, self.box, int(length))

    def __repr__(self):
        return self.line

    @classmethod
    def hashstep(cls, start: int, value: int | str) -> int:
        value = ord(value) if isinstance(value, str) else value
        return (((start + value)*17) % 256)

    @classmethod
    def hash(cls, data: bytes) -> int:
        return reduce(cls.hashstep, data, 0)


class Boxes:

    def __init__(self, operations: list[Operation]):
        self.operations: list[Operation] = operations
        self.boxes: dict[int, list[Lens]] = {}

        for op in operations:
            if op.op == '=':
                self.insert(op.box, op.lens)
            else:
                self.remove(op.box, op.label)

    def insert(self, box: int, lens: Lens) -> None:
        if not box in self.boxes:
            self.boxes[box] = [lens]
        else:
            for i, old in enumerate(self.boxes[box]):
                if old.label == lens.label:
                    self.boxes[box][i] = lens
                    break
            else:
                self.boxes[box].append(lens)

    def remove(self, box: int, label: str) -> None:
        if box in self.boxes:
            for i, old in enumerate(self.boxes[box]):
                if old.label == label:
                    self.boxes[box].remove(old)
                    if not self.boxes[box]:
                        del self.boxes[box]
                    break

    def print(self) -> None:
        for box, slots in sorted(self.boxes.items(), key=itemgetter(0)):
            print(f'{(box+1):3d} {slots}')

    @property
    def focusing_power(self) -> int:
        power = 0
        for box, slots in self.boxes.items():
            for slot, lens in enumerate(slots, 1):
                power += (box+1)*slot*lens.length
        return power


class Day15(Puzzle):
    """Lens Library"""

    def parse_data(self, filename: str) -> Data:
        return [Operation(phrase) for phrase in self.read_split(filename, ',')]

    def part1(self, data: Data) -> PuzzleResult:
        return sum([c.linehash for c in data])

    def part2(self, data: Data) -> PuzzleResult:
        boxes = Boxes(data)
        return boxes.focusing_power


puzzle = Day15()
puzzle.run(1320, 145)
