from __future__ import annotations

from common import *

@dataclass
class Pull:
    red: int
    green: int
    blue: int
    
    @classmethod
    def parse(cls, text: str) -> "Pull":
        red, green, blue = 0, 0, 0
        for cube in text.strip().split(', '):
            qty, _, color = cube.partition(' ')
            if color == 'red':
                red = int(qty)
            elif color == 'green':
                green = int(qty)
            else:
                blue = int(qty)
                
        return cls( red, green, blue)

@dataclass
class Game:
    id: int
    pulls: list[Pull]

    @property
    def red(self) -> int:
        return max([pull.red for pull in self.pulls])

    @property
    def green(self) -> int:
        return max([pull.green for pull in self.pulls])

    @property
    def blue(self) -> int:
        return max([pull.blue for pull in self.pulls])

    @property
    def power(self) -> int:
        return self.red * self.green * self.blue

    @classmethod
    def parse(cls, text: str) -> "Game":
        game, _, actions = text.strip().partition(': ')
        id = int(game[5:])
        pulls = [Pull.parse(action) for action in actions.split('; ')]
        
        return cls(id, pulls)


class Day02(Puzzle):
    """Cube Conundrum"""
    
    def parse_data(self, filename) -> list[Game]:
        return [Game.parse(line) for line in self.read_stripped(filename)]
    
    def part1(self, data: list[Game]) -> int:
        return sum([game.id for game in data 
                     if game.red <= 12 and game.green <= 13 and game.blue <= 14])

    def part2(self, data: list[Game]) -> int:
        return sum([game.power for game in data])

puzzle = Day02()
puzzle.run(8, 2286)
