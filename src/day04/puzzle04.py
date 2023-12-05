from common import *


@dataclass
class Card:
    id: int
    winners: set[int]
    numbers: set[int]

    @cached_property
    def count(self) -> int:
        return len(self.winners & self.numbers)

    @cached_property
    def score(self) -> int:
        score = pow(2, self.count-1) if self.count else 0
        return score

    @classmethod
    def parse(cls, line):
        card_id, _, all_numbers = line.partition(': ')
        id = int(card_id.split(' ')[-1])
        winners, _, numbers = all_numbers.partition(' | ')
        win_list = set([int(n) for n in winners.split(' ') if n])
        num_list = set([int(n) for n in numbers.split(' ') if n])
        return cls(id, win_list, num_list)


class Day04(Puzzle):
    """Scratchcards"""
    
    def parse_data(self, filename: str) -> list[Card]:
        return [Card.parse(line) for line in self.read_stripped(filename)]

    def part1(self, data: list[Card]) -> int:
        return sum([card.score for card in data])

    def part2(self, data: list[Card]) -> int:
        cards = [1]*len(data)
        for id, card in enumerate(data):
            if card.count:
                for copy in range(id+1, id+card.count+1):
                    cards[copy] += cards[id]

        result = sum(cards)
        return result


puzzle = Day04()
puzzle.run(13, 30)
