from __future__ import annotations

import re
from typing import Generator, Iterator

from common import *

mode = str.maketrans('01', '.#')

DOT = '.'


@dataclass
class Properties:
    pattern: str
    lengths: list[int]

    @property
    def size(self) -> int:
        return len(self.lengths)

    @property
    def minimum(self) -> int:
        return sum(self.lengths)

    @property
    def maximum(self) -> int:
        return len(self.pattern)

    @property
    def extra(self) -> int:
        return self.maximum - self.minimum

    @property
    def regex(self) -> str:
        return self.pattern.replace('?', '[.#]')


class Dots:
    def __init__(self, start, end, prefix=''):
        self.range = range(start, end)
        self.prefix = prefix
        self.iter = iter(self.range)
        self.index = None
        self.curr = None

    def __iter__(self) -> Iterator:
        return self.iter

    def __next__(self) -> str:
        self.index = next(self.iter)
        self.curr = self.prefix+'.'*self.index
        return self.curr

    def __repr__(self):
        return f'State({self.range.start}, {self.range.stop})'

    @property
    def done(self) -> bool:
        return self.index == self.range.stop


@dataclass
class Condition:
    pattern: str
    lengths: list[int]

    @property
    def part1(self) -> Properties:
        return Properties(self.pattern, self.lengths)

    @property
    def part2(self) -> Properties:
        return Properties('?'.join(self.pattern*5), self.lengths * 5)

    def brute_force(self, p: Properties) -> int:
        matches = 0

        groups = ['#'*l for l in p.lengths]
        expanded = r'^\.*' + r'\.+'.join(groups) + r'\.*$'
        regex = re.compile(expanded)

        q = p.pattern.count('?')
        expansion = p.pattern.replace('?', '{}')

        for permutation in range(q**2):
            chars = bin(permutation)[2:].zfill(q).translate(mode)
            potential = expansion.format(*chars)
            if regex.match(potential):
                matches += 1

        return matches

    def faster(self, p: Properties) -> int:
        """Faster way to victory

        What varies is the number of dots (.) between groups of #
        For something like ?###???????? 3,2,1, 
        the desired length is 12, the minimum is 8, 
        so you get a pattern like {}###{}##{}#{}, 
        and 6 extra dots need to be distributed amongst the {}. 
        The edge groups are optional, the others are mandatory.

        0112, 0121, 0130, 0211, 0220, 0310
        1111, 1120, 1210, 2110

        for a in range(0, 6-3+1):
            for b in range(1, 6-a-2+1):
                for c in range(1, 6-a-b-1+1):
                    for d in range(0, 6-a-b-c+1):
                        if pattern matches.{a}###.{b}##.{c}#.{d}:
                            print(f'{a}{b}{c}{d}')

        While it's easy to handle 4 levels of nested loops, 
        when the number of loops varies from one row to the next, 
        and the maxium number of loops is ~20, you need a solution 
        that doesn't depend on recursion or high memory usage.
        """

        if p.extra == 1:
            return 1

        matches = 0

        groups = ['#'*l for l in p.lengths]
        expanded = r'{}' + r'{}'.join(groups) + r'{}'

        regex = re.compile(p.regex)
        for dots in self.dots(p):
            potential = expanded.format(dots)
            if regex.matches(potential):
                matches += 1

        return matches

    def dots(self, p: Properties) -> Generator[str]:
        """Yields a list of strings of dots"""

        states: list[Dots] = [None]*p.size
        broken: list[str] = ['#'*l for l in p.lengths]

        depth = 0
        while True:
            # if pos == 0
            if depth == p.size-1:
                for pattern in states[depth]:
                    yield pattern
                depth -= 1

    @classmethod
    def parse(cls, line) -> Condition:
        pattern, _, rest = line.partition(' ')
        lengths = list(map(int, rest.split(',')))
        return cls(pattern, lengths)


class Day12(Puzzle):
    """Hot Springs"""
    
    def parse_data(self, filename: str) -> Data:
        conditions = list(map(Condition.parse, self.read_stripped(filename)))
        return conditions

    def part1(self, data: list[Condition]) -> PuzzleResult:
        return sum([c.faster(c.part1) for c in data])

    def part2(self, data: list[Condition]) -> PuzzleResult:
        return sum([c.faster(c.part2) for c in data])


puzzle = Day12()
puzzle.run() # 21