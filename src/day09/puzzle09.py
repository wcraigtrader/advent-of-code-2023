from __future__ import annotations

import re
from itertools import pairwise

from common import *

INTEGER = re.compile(r'-?\d+')
OFFSETS = { 'first': 0, 'second': 1, 'penultimate': -2, 'last': -1 }


@dataclass
class History:
    values: list[int]

    def __getattr__(self, key) -> Any:
        if key in OFFSETS:
            return getattr(self, 'values')[OFFSETS[key]]
        else:
            return getattr(self, key)

    @cached_property
    def next(self) -> History:
        return self.__class__([y-x for x, y in pairwise(self.values)])

    @cached_property
    def predictable(self) -> bool:
        return all([x==y for x,y in pairwise(self.values)])

    @property
    def prediction(self) -> int:
        if self.predictable:
            return 2 * self.last - self.penultimate
        else:
            return self.last + self.next.prediction

    @property
    def extrapolation(self) -> int:
        if self.predictable:
            return 2 * self.first - self.second
        else:
            return self.first - self.next.extrapolation

    @classmethod
    def parse(cls, text: str) -> History:
        values = list(map(int, INTEGER.findall(text)))
        return cls(values)


class Day09(Puzzle):
    """Mirage Maintenance"""
    
    def parse_data(self, filename: str) -> Data:
        return list(map(History.parse, self.read_stripped(filename)))

    def part1(self, data: Data) -> PuzzleResult:
        predictions = [entry.prediction for entry in data]
        return sum(predictions)

    def part2(self, data: Data) -> PuzzleResult:
        extrapolations = [entry.extrapolation for entry in data]
        return sum(extrapolations)


puzzle = Day09()
puzzle.run(114, 2)
