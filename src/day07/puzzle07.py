from __future__ import annotations

from collections import Counter
from enum import IntEnum
from operator import attrgetter

from common import *

NaturalValues = IntEnum('Card', '2 3 4 5 6 7 8 9 T J Q K A')
WildCardValues = IntEnum('Card', 'J 2 3 4 5 6 7 8 9 T Q K A')

HT = IntEnum(
    'HT', 'HighCard OnePair TwoPair ThreeOFAK FullHouse FourOFAK FiveOFAK')

HandTypes = {
    '5': HT.FiveOFAK,
    '4-1': HT.FourOFAK,
    '3-2': HT.FullHouse,
    '3-1-1': HT.ThreeOFAK,
    '2-2-1': HT.TwoPair,
    '2-1-1-1': HT.OnePair,
    '1-1-1-1-1': HT.HighCard,
}


@dataclass(frozen=True, order=True)
class Hand:
    cards: str
    bid: int

    def handtype(self, wild: bool = False) -> HT:
        cards = Counter()
        for card in self.cards:
            cards[card] += 1

        sizes = list(reversed(sorted(cards.values())))

        if wild and 'J' in cards and len(cards) > 1:
            jacks = cards['J']
            sizes.remove(jacks)
            sizes[0] += jacks

        pattern = '-'.join([chr(48+s) for s in sizes])

        return HandTypes[pattern]

    def rank(self, wild: bool = False) -> int:
        ht = self.handtype(wild)
        values = WildCardValues if wild else NaturalValues
        ranks = [ht] + [values[card].value for card in self.cards]
        rank = sum([100**(5-pos)*rank for pos, rank in enumerate(ranks)])
        return rank

    @cached_property
    def natural(self):
        return self.rank(False)

    @cached_property
    def wildcard(self):
        return self.rank(True)

    @classmethod
    def parse(cls, line: str) -> Hand:
        cards, _, bid = line.partition(' ')
        return cls(cards, int(bid))


class Day07(Puzzle):
    """Camel Cards"""

    def parse_data(self, filename: str) -> Data:
        lines = self.read_stripped(filename)
        return [Hand.parse(line) for line in lines]

    def part1(self, data: list[Hand]) -> PuzzleResult:
        hands = sorted(data, key=attrgetter('natural'))
        values = [value*hand.bid for value, hand in enumerate(hands, 1)]
        return sum(values)

    def part2(self, data: list[Hand]) -> PuzzleResult:
        hands = sorted(data, key=attrgetter('wildcard'))
        values = [value*hand.bid for value, hand in enumerate(hands, 1)]
        return sum(values)


puzzle = Day07()
puzzle.run(6440, 5905)
