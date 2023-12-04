from __future__ import annotations

import os
import sys
import time

from math import isnan, nan
from typing import (
    IO,
    Optional,
)

IGNORE = nan

Data = list[str]
PuzzleResult = int | dict | list


class Puzzle:
    """This is a framework for solving each day's puzzle"""

    def __init__(self, datafile: str = 'real.data', *testfiles: str):
        self.base = os.path.dirname(sys.argv[0])

        self.datafile = datafile
        self.testfiles = testfiles or ['test.data']
        self.currentfile = None

        self.data = None
        self.tests = None

        self._started = 0
        self._elapsed = 0
        self._overall = 0

    def __repr__(self) -> str:
        text = self.__class__.__name__.replace('Day', 'Day ')
        if self.__doc__:
            text = f'{text}: {self.__doc__}'
        return text

    # ----- Methods each Puzzle needs to implement ----------------------------

    def parse_data(self, filename):
        """Parse a data file, returning data for each part of the puzzle"""
        raise NotImplementedError('parse_data')

    def part1(self, data) -> PuzzleResult:
        """Implement part 1 of the puzzle"""
        raise NotImplementedError('part1')

    def part2(self, data) -> PuzzleResult:
        """Implement part 2 of the puzzle"""
        raise NotImplementedError('part2')

    # ----- Useful methods for parsing data files -----------------------------

    def open(self, filename: str, mode: str = 'r') -> IO:
        return open(os.path.join(self.base, filename), mode)

    def read_blob(self, filename: str) -> str:
        """Read a data file, returning its entire contents as a string"""

        with self.open(filename) as df:
            return df.read()

    def read_lines(self, filename: str) -> Data:
        """Read a data file, returning a list, one entry per line"""

        with self.open(filename) as df:
            return df.readlines()

    def read_stripped(self, filename: str) -> Data:
        """Read a data file as lines, stripping leading and trailing white space"""

        return list(map(str.strip, self.read_lines(filename)))

    def read_split(self, filename: str, sep: str) -> Data:
        """Read a data file, splitting on a seperator"""

        return self.read_blob(filename).strip().split(sep)

    def read_bytes(self, filename: str) -> Data:
        with self.open(filename, 'rb') as df:
            return df.read().splitlines()

    def read_bytearrays(self, filename: str) -> Data:
        return [bytearray(row) for row in self.read_bytes(filename)]

    def read_bytes_split(self, filename: str, sep: bytes) -> Data:
        with self.open(filename, 'rb') as df:
            return df.read().strip().split(sep)

    def data_path(self, filename: str, extension: str) -> str:
        name = filename.replace('.data', extension)
        path = os.path.join(self.base, name)
        return path

    def current_path(self, extension: str = '.out') -> str:
        return self.data_path(self.currentfile, extension)

    # ----- Test runner -------------------------------------------------------

    def run(self,
            test1: Optional[PuzzleResult] = None,
            test2: Optional[PuzzleResult] = None,
            **keywords: dict,) -> None:
        """Load data and run tests"""

        print(f'===== {self} =====')

        self.testonly = keywords.get('testonly', False)

        try:
            if self.check_data_files():
                return

            self.start()
            self.tests = [self.parse_data(tf) for tf in self.testfiles]
            self.stop()
            print(f'{self.elapsed_}: parsed test data')

            if not self.testonly:
                self.start()
                self.data = self.parse_data(self.datafile)
                self.stop()
                print(f'{self.elapsed_}: parsed real data')

            skip = keywords.get('skip', False)

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
                    else:
                        self.single_test('part2', test2)
                except AssertionError as e:
                    print(f'part 2 failed: {" ".join(e.args)}')

            print(f'{self.overall_}: total')

        except NotImplementedError as e:
            print(f'{self.__class__.__name__}: {" ".join(e.args)} not implemented.')

    def check_data_files(self):
        filenames = [self.datafile]
        filenames.extend(self.testfiles)

        errors = False
        for filename in filenames:
            pathname = os.path.relpath(os.path.join(self.base, filename))
            try:
                stat = os.stat(pathname)
                if stat.st_size == 0:
                    print(f'Data file {pathname} is empty.')
                    errors = True

            except FileNotFoundError:
                print(f'Data file {pathname} is missing.')
                errors = True

        return errors

    def single_test(self, name: str, expected, test_index: int = 0) -> None:
        """Execute one test run and one real run for part1 or part2"""

        method = getattr(self, name)

        if expected is not None and not isnan(expected):
            self.start()
            self.currentfile = self.testfiles[test_index]
            test_result = method(self.tests[test_index])
            self.stop()
            print(f'{self.elapsed_}: {name} test = {test_result}')
            assert test_result == expected, f'Was {test_result}, should have been {expected}'

        if not self.testonly:
            self.start()
            self.currentfile = self.datafile
            real_result = method(self.data)
            self.stop()
            print(f'{self.elapsed_}: {name} real = {real_result}')

    def multi_test(self, name: str, expectations: list, testdata: list, multifile: bool) -> None:
        """Execute multiple test runs and one real run for part1 or part2"""

        method = getattr(self, name)

        for i, (test, expected) in enumerate(zip(testdata, expectations), 1):
            if expected is not None and not isnan(expected):
                self.start()
                self.currentfile = self.testfiles[i-1]
                result = method(test)
                self.stop()
                passed = 'passed' if result == expected else 'failed'
                print(
                    f'{self.elapsed_}: {name} test {i}, {expected} == {result} => {passed}')

        if not self.testonly:
            self.start()
            self.currentfile = self.datafile
            real_result = method(
                self.data) if multifile else method(self.data[0])
            self.stop()
            print(f'{self.elapsed_}: {name} real = {real_result}')

    def map_test(self, name: str, **keywords: dict) -> None:
        """Execute one test run and one real run for part1 or part2"""

        method = getattr(self, name)
        expected = keywords.get('expected')
        self.start()
        self.currentfile = self.testfiles[0]
        test_result = method(self.tests[0], keywords.get('test', None))
        self.stop()
        print(f'{self.elapsed_}: {name} test = {test_result}')
        if not isnan(expected):
            assert test_result == expected, f'Was {test_result}, should have been {expected}'

        if not self.testonly:
            self.start()
            self.currentfile = self.datafile
            real_result = method(self.data, keywords.get('real', None))
            self.stop()
            print(f'{self.elapsed_}: {name} real = {real_result}')

    # ----- Internal methods --------------------------------------------------

    def start(self):
        """Start a timer"""
        self._started = time.perf_counter_ns()

    def stop(self):
        """Stop the timer and save the elapsed time in milliseconds"""
        self._elapsed = (time.perf_counter_ns() - self._started) / 1_000_000
        self._overall += self._elapsed

    @property
    def elapsed_(self):
        """Format the elapsed time in milliseconds"""
        return f'{self._elapsed:10,.3f} ms'

    @property
    def overall_(self):
        """Format the overall time in milliseconds"""
        return f'{self._overall:10,.3f} ms'

    @property
    def instant_(self):
        instant = (time.perf_counter_ns() - self._started) / 1_000_000
        return f'{instant:10,.3f} ms'
