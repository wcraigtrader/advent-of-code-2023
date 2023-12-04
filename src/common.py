import os
import sys
import time

from dataclasses import dataclass, field
from enum import Enum
from functools import cache, cached_property
from typing import Any, Optional, Iterator


class Puzzle:
    """This is a framework for solving each day's puzzle"""

    def __init__(self, datafile: str = 'real.data', *testfiles: str):
        self.base = os.path.dirname(sys.argv[0])

        self.datafile = datafile
        self.testfiles = testfiles or ['test.data']

        self.data = None
        self.tests = None

        self._started = 0
        self._elapsed = 0
        self._overall = 0

    # ----- Methods each Puzzle needs to implement ----------------------------

    def parse_data(self, filename):
        """Parse a data file, returning data for each part of the puzzle"""
        raise NotImplementedError('parse_data')

    def part1(self, data) -> int:
        """Implement part 1 of the puzzle"""
        raise NotImplementedError('part1')

    def part2(self, data) -> int:
        """Implement part 2 of the puzzle"""
        raise NotImplementedError('part2')

    # ----- Useful methods for parsing data files -----------------------------

    def read_blob(self, filename: str) -> str:
        """Read a data file, returning its entire contents as a string"""

        with open(os.path.join(self.base, filename), 'r') as df:
            return df.read()

    def read_lines(self, filename: str) -> list[str]:
        """Read a data file, returning a list, one entry per line"""

        with open(os.path.join(self.base, filename), 'r') as df:
            return df.readlines()

    def read_stripped(self, filename: str) -> list[str]:
        """Read a data file, stripping leading and trailing white space"""

        return list(map(str.strip, self.read_lines(filename)))

    # ----- Test runner -------------------------------------------------------

    def run(self,
            test1: Optional[int | dict | list] = None,
            test2: Optional[int | dict | list] = None,
            **keywords: dict,) -> None:
        """Load data and run tests"""

        try:
            print('Parsing test data ...')
            self.start()
            self.tests = [self.parse_data(tf) for tf in self.testfiles]
            self.stop()
            print(f'{self.elapsed}: parsed test data')

            print('Parsing real data ...')
            self.start()
            self.data = self.parse_data(self.datafile)
            self.stop()
            print(f'{self.elapsed}: parsed real data')

            skip = keywords.get('skip', False)
            different = keywords.get('different', False)

            print('Calculating ...')

            if test1 is not None and not skip:
                try:
                    if isinstance(test1, dict):
                        self.map_test('part1', **test1)
                    elif isinstance(test1, list):
                        if len(self.tests) == len(test1):
                            self.multi_test('part1', test1, self.tests, True)
                        else:
                            self.multi_test(
                                'part1', test1, self.tests[0], False)
                    else:
                        self.single_test('part1', test1)
                except AssertionError as e:
                    print(f'part 1 failed: {" ".join(e.args)}')

            if test2 is not None:
                try:
                    if isinstance(test2, dict):
                        self.map_test('part2', **test2)
                    elif isinstance(test2, list):
                        if len(self.tests) == len(test2):
                            self.multi_test('part2', test2, self.tests, True)
                        else:
                            self.multi_test(
                                'part2', test2, self.tests[0], False)
                    elif different:
                        self.single_test('part2', test2, 1)
                    else:
                        self.single_test('part2', test2)
                except AssertionError as e:
                    print(f'part 2 failed: {" ".join(e.args)}')

            print(f'{self.overall}: total')

        except NotImplementedError as e:
            print(f'{self.__class__.__name__}: {" ".join(e.args)} not implemented.')

    def single_test(self, name: str, expected, test_index: int = 0) -> None:
        """Execute one test run and one real run for part1 or part2"""

        method = getattr(self, name)

        self.start()
        test_result = method(self.tests[test_index])
        self.stop()
        print(f'{self.elapsed}: {name} test = {test_result}')
        assert test_result == expected, f'Was {test_result}, should have been {expected}'

        self.start()
        real_result = method(self.data)
        self.stop()
        print(f'{self.elapsed}: {name} real = {real_result}')

    def multi_test(self, name: str, expectations: list, testdata: list, multifile: bool) -> None:
        """Execute multiple test runs and one real run for part1 or part2"""

        method = getattr(self, name)

        for i, (test, expected) in enumerate(zip(testdata, expectations), 1):
            self.start()
            result = method(test)
            self.stop()
            passed = 'passed' if result == expected else 'failed'
            print(
                f'{self.elapsed}: {name} test {i}, {expected} == {result} => {passed}')

        self.start()
        real_result = method(self.data) if multifile else method(self.data[0])
        self.stop()
        print(f'{self.elapsed}: {name} real = {real_result}')

    def map_test(self, name: str, **keywords: dict) -> None:
        """Execute one test run and one real run for part1 or part2"""

        method = getattr(self, name)
        expected = keywords.get('expected')
        self.start()
        test_result = method(self.tests[0], keywords.get('test', None))
        self.stop()
        print(f'{self.elapsed}: {name} test = {test_result}')
        assert test_result == expected, f'Was {test_result}, should have been {expected}'

        self.start()
        real_result = method(self.data, keywords.get('real', None))
        self.stop()
        print(f'{self.elapsed}: {name} real = {real_result}')

    # ----- Internal methods --------------------------------------------------

    def start(self):
        """Start a timer"""
        self._started = time.perf_counter_ns()

    def stop(self):
        """Stop the timer and save the elapsed time in milliseconds"""
        self._elapsed = (time.perf_counter_ns() - self._started) / 1_000_000
        self._overall += self._elapsed

    @property
    def elapsed(self):
        """Format the elapsed time in milliseconds"""
        return f'{self._elapsed:10,.3f} ms'

    @property
    def overall(self):
        """Format the overall time in milliseconds"""
        return f'{self._overall:10,.3f} ms'


@dataclass(order=True, unsafe_hash=True)
class AstarNode:
    """A node wrapper for A*Search

    This class is hashable, but hashes only on the node.
    This class is sortable, but only on the priority.
    """

    node: Any = field(compare=False, hash=True)
    priority: float = field(compare=True, hash=False, default=0.0)
    backtrack: 'AstarNode' = field(compare=False, default=None, repr=False)

    def __eq__(self, other: 'AstarNode') -> bool:
        return self.node == other.node


class AstarSearch:
    """Implement the A* search algorithm for Any type of node

    Each node in the search graph / grid gets wrapped in an AstarNode
    as it becomes visible in the search.

    Subclass this and implement the `neighbors`, `distance`, and `heuristic` methods.
    Call `traverse` to

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
        from heapq import heappush, heappop

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
