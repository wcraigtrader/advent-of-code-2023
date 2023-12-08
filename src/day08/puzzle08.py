from __future__ import annotations

from math import lcm

from common import *


@dataclass(frozen=True)
class Node:
    name: str
    left: str
    right: str

    @property
    def origin(self) -> bool:
        return self.name[2] == 'A'

    @property
    def goal(self) -> bool:
        return self.name[2] == 'Z'


@dataclass
class Map:
    directions: str
    nodes: dict[str, Node]

    @property
    def length(self):
        return len(self.directions)

    def turn(self, position: Node, direction: str) -> Node:
        return self.nodes[position.left] if direction == 'L' else self.nodes[position.right]

    def follow(self) -> PuzzleResult:
        steps = 0
        position = self.nodes['AAA']
        while position.name != 'ZZZ':
            for direction in self.directions:
                position = self.turn(position, direction)
            steps += self.length
        return steps

    def follow_ghosts(self) -> PuzzleResult:
        positions = [node for node in self.nodes.values() if node.origin]
        steps = [0] * len(positions)

        for i in range(len(positions)):
            while not positions[i].goal:
                for direction in self.directions:
                    positions[i] = self.turn(positions[i], direction)
                steps[i] += self.length

        return lcm(*steps)

    @classmethod
    def parse(cls, data: Data) -> Map:
        directions = data[0]
        nodes = {line[0:3]: Node(line[0:3], line[7:10], line[12:15])
                 for line in data[2:]}
        return cls(directions, nodes)


class Day08(Puzzle):
    """Haunted Wasteland"""

    def parse_data(self, filename: str) -> Map:
        lines = self.read_stripped(filename)
        return Map.parse(lines)

    def part1(self, map: Map) -> PuzzleResult:
        return map.follow()

    def part2(self, map: Map) -> PuzzleResult:
        return map.follow_ghosts()


puzzle = Day08('real.data', 'test1.data', 'test2.data', 'test3.data')
puzzle.run([2, 6, None], [2, 6, 6])
