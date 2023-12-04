from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True, unsafe_hash=True)
class AstarNode:
    """A node wrapper for A*Search

    This class is hashable, but hashes only on the node.
    This class is sortable, but only on the priority.
    """

    node: Any = field(compare=False, hash=True)
    priority: float = field(compare=True, hash=False, default=0.0)
    backtrack: AstarNode = field(compare=False, default=None, repr=False)

    def __eq__(self, other: AstarNode) -> bool:
        return self.node == other.node


class AstarSearch:
    """Implement the A* search algorithm for Any type of node

    Each node in the search graph / grid gets wrapped in an AstarNode
    as it becomes visible in the search.

    Subclass this and implement the `neighbors`, `distance`, and `heuristic` methods.
    Call `traverse` to get the optimum list of nodes traversed.

    Notes: https://en.wikipedia.org/wiki/A*_search_algorithm
    """

    UNSEEN = 999_999_999

    def _clear(self):
        self._lookup: dict[Any, AstarNode] = {}

    def _find(self, node: Any) -> AstarNode:
        if node not in self._lookup:
            self._lookup[node] = AstarNode(node, self.UNSEEN)
        return self._lookup[node]

    def _reconstruct_path(self, current: AstarNode) -> list[Any]:
        path = [current.node]
        while current.backtrack:
            current = current.backtrack
            path.append(current.node)

        path.reverse()

        return path

    def backtrack(self, node: Any) -> Any:
        if node in self._lookup:
            back = self._lookup[node].backtrack
            if back:
                return back.node
        return None

    def neighbors(self, node: Any) -> list[Any]:
        """Return a list of all of the neighbors of a node"""
        raise NotImplementedError('neighbors function')

    def distance(self, src: Any, dst: Any) -> float:
        """Distance between two nodes"""
        raise NotImplementedError('distance function')

    def heuristic(self, node: Any) -> float:
        """Estimate the cost to get to the goal from a node"""
        raise NotImplementedError('heuristic function')

    def traverse(self, origin: Any, target: Any) -> list[Any]:
        from collections import defaultdict
        from heapq import heappop, heappush

        self._clear()

        a_origin = self._find(origin)
        a_target = self._find(target)

        exploring: list[AstarNode] = []
        heappush(exploring, a_origin)

        g_score: dict[AstarNode, int] = defaultdict(lambda: self.UNSEEN)
        g_score[a_origin] = 0

        while len(exploring):
            current = heappop(exploring)
            if current == a_target:
                return self._reconstruct_path(current)

            for node in self.neighbors(current.node):
                neighbor = self._find(node)
                tentative = g_score[current] + \
                    self.distance(current.node, neighbor.node)
                if tentative < g_score[neighbor]:
                    neighbor.backtrack = current
                    g_score[neighbor] = tentative
                    neighbor.priority = tentative + \
                        self.heuristic(neighbor.node)
                    if neighbor not in exploring:
                        heappush(exploring, neighbor)

        return None
