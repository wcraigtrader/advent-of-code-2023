from __future__ import annotations

import math
import re
from functools import reduce

from common import *


@dataclass
class Race:
    time: int
    record: int

    def winner(self, t) -> bool:
        return (t * (self.time - t)) > self.record

    @property
    def wins(self) -> int:
        # Quadratic equation solution
        a, b, c = 1, -self.time, self.record
        d = math.sqrt(b**2-4*a*c)
        z1 = (-b-d)/2*a
        z2 = (-b+d)/2*a
        return math.ceil(z2)-math.floor(z1)-1


class Day06(Puzzle):
    """Wait For It"""
    
    def parse_data(self, filename: str) -> list[str]:
        return self.read_stripped(filename)

    def part1(self, lines: list[str]) -> int:
        times = [int(t) for t in re.findall('\d+', lines[0])]
        records = [int(d) for d in re.findall('\d+', lines[1])]
        races = [Race(t, r) for t, r in zip(times, records)]
        wins = [race.wins for race in races]
        return reduce(lambda x, y: x*y, wins, 1)

    def part2(self, lines: list[str]) -> int:
        time = int(lines[0].split(':')[1].replace(' ', ''))
        record = int(lines[1].split(':')[1].replace(' ', ''))
        race = Race(time, record)
        return race.wins


puzzle = Day06()
puzzle.run(288, 71503)
