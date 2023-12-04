My solutions to the Advent of Code 2023 challenge.

Implementation language is Python 3. My personal goal is to write well-structured, efficient Python 3 code.

## Running puzzles

Run each puzzle like this:
```shell
PYTHONPATH=src python3 src/day01/puzzle01.py
```

Run all puzzles like this:
```shell
bash run_all.sh
```

## Solving puzzles

1. Create a directory for the day (day##)
1. Add data files for the actual input (`real.data`) and test inputs (`test1.data`, `test2.data`, ...). You can use any names you like, but `real.data` and `test.data` are the detaults.
1. Create a puzzle solution class:
   ```python
   from common input *

   class DayXX(Puzzle):

      def parse_data(self, filename: str) -> Data:
          return self.read_stripped(filename)

      def part1(self, data: Data) -> PuzzleResult:
          return 0

      def part2(self, data: Data) -> PuzzleResult:
          return 0

   puzzle = Day09()
   puzzle.run()
   ```
1. The constuctor is used to define the data files. The first argument is the actual data file name; subsequent arguments are for test data file names. If called without arguments, it defaults to `'real.data', 'test.data'`.
1. The `run` method will first call `parse_data` method for each data file, then it will call the solution methods (`part1` and `part2`) for the test and actual data files.
1. The `run` method takes 2 optional arguments: the expected results for the test data for parts 1 and 2. If the part2 test results are not present, then part2 will be skipped.

## Test expectations

The expectations can be specified as follows:

* If the expectation is a primitive (`int`, `str`), then the test is run once.
* If the expectation is a `dict` then the test is run once, expecting a `dict`.
* If the expectation is a `list`, then:
  * If the length of the list matches the number of test files provided, 
    then the test is run once for each test file, expecting one value. 
    If the test value is `None` then the test will be skipped.
  * The test is run once, expecting a `list`.

## Test examples

```python
puzzle = Day01()
puzzle.run(8)
```

`part1` will be tested with `test.data`, expecting `8`.  

```python
puzzle = Day01()
puzzle.run(8, 2286)
```

`part1` will be tested with `test.data`, expecting `8`.  
`part2` will be tested with `test.data`, expecting `2286`. 

```python
puzzle = Day01('real.data', 'test1.data', 'test2.data')
puzzle.run([142, None], [None, 281])
```

`part1` will be tested with `test1.data`, expecting `142`.  
`part2` will be tested with `test2.data`, expecting `281`.
