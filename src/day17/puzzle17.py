from __future__ import annotations

from typing import Any

from common import *

DIRECTIONS = [
    GridDirection(1, 0),
    GridDirection(0, 1),
    GridDirection(-1, 0),
    GridDirection(0, -1),
]


class Crucible(Grid, AstarSearch):

    def __init__(self, lines):
        super().__init__(lines, conversion=int)

        self.origin = GridPosition(0, 0)
        self.target = GridPosition(self.rows-1, self.cols-1)

    def neighbors(self, node: Any) -> list[Any]:
        """Return a list of all of the neighbors of a node"""
        directions = set(DIRECTIONS)

        prev1 = self.backtrack(node)
        if prev1 is not None:
            backwards = prev1 - node
            directions.remove(backwards)
            prev2 = self.backtrack(prev1)
            if prev2 is not None:
                prev3 = self.backtrack(prev2)
                if prev3 is not None:
                    if backwards == (prev2-prev1) == (prev3-prev2):
                        forwards = 0 - backwards
                        directions.remove(forwards)

        neighbors = [n for n in
                     [node + d for d in directions]
                     if self.inbounds(n)]
        return neighbors

    def distance(self, src: Any, dst: Any) -> float:
        """Distance between two nodes"""
        # distance = GridOrthogonalDistance(src, dst)
        # distance = GridRow(src)-GridRow(dst) + GridCol(src)-GridCol(dst)
        cost = self[dst]
        return cost

    def heuristic(self, node: Any) -> float:
        """Estimate the cost to get to the goal from a node"""
        return GridOrthogonalDistance(node, self.target)


class Day17(Puzzle):
    """Clumsy Crucible"""

    def parse_data(self, filename: str) -> Data:
        return Crucible(self.read_stripped(filename))

    def part1(self, data: Crucible) -> PuzzleResult:
        path = data.traverse(data.origin, data.target)
        score = sum([data[node] for node in path[1:]])

        temp = Grid(data)
        temp[path[0]] = '.'
        for pos in path[1:]:
            temp[pos] = '*'

        for row in data.row_range:
            print(f'{data.render_row(row)} : {temp.render_row(row)}')

        return score

    def part2(self, data: Crucible) -> PuzzleResult:
        return 0


puzzle = Day17()
puzzle.run(102)
