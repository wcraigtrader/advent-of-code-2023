from __future__ import annotations

from collections import OrderedDict
from enum import IntEnum
from typing import Union

from common import *

Category = IntEnum(
    'Category', 'seed soil fertilizer water light temperature humidity location')


@dataclass(frozen=True)
class Pair:
    beg: int
    end: int

    def __post_init__(self):
        assert self.beg <= self.end

    def __contains__(self, other: Union[int, "Pair"]) -> bool:
        if isinstance(other, int):
            return self.beg <= other <= self.end
        elif isinstance(other, self.__class__):
            return self.beg <= other.beg <= other.end <= self.end

    def __len__(self) -> int:
        return self.end - self.beg + 1

    def __hash__(self):
        return hash((self.beg, self.end))

    def __eq__(self, other: "Pair") -> bool:
        return isinstance(other, self.__class__) and self.beg == other.beg and self.end == other.end

    def __lt__(self, other: "Pair") -> bool:
        return isinstance(other, self.__class__) and self.end < other.beg

    def __le__(self, other: "Pair") -> bool:
        return isinstance(other, self.__class__) and self.end <= other.beg

    def __gt__(self, other: "Pair") -> bool:
        return isinstance(other, self.__class__) and self.beg > other.end

    def __ge__(self, other: "Pair") -> bool:
        return isinstance(other, self.__class__) and self.beg >= other.end

    @property
    def points(self) -> list[int]:
        return [self.beg, self.end]

    def leftlaps(self, other: "Pair") -> bool:
        """Self overlaps and extends to the left of other"""
        return (self.beg < other.beg <= self.end <= other.end)

    def rightlaps(self, other: "Pair") -> bool:
        """Self overlaps and extends to the right of other"""
        return (other.beg <= self.beg <= other.end < self.end)

    def contains(self, other: "Pair") -> bool:
        """Self completely contains other"""
        return (self.beg <= other.beg <= other.end <= self.end)

    def containedby(self, other: "Pair") -> bool:
        """Self completely contained by other"""
        return (other.beg <= self.beg <= self.end <= other.end)

    def overlaps(self, other: "Pair") -> bool:
        return isinstance(other, self.__class__) and (
            self.contains(other) or self.containedby(other) or
            self.leftlaps(other) or self.rightlaps(other)
        )

    def intersection(self, other: "Pair") -> list["Pair"]:
        results = []
        if self.overlaps(other):
            results.append(Pair(max(self.beg, other.beg),
                           min(self.end, other.end)))
        return results

    def disjoint(self, other: "Pair") -> list["Pair"]:
        results = []
        if self.leftlaps(other):
            results.append(Pair(self.beg, max(self.beg, other.beg-1)))
        if self.rightlaps(other):
            results.append(Pair(max(self.end, other.end+1), self.end))
        return results

    def union(self, other: "Pair") -> list["Pair"]:
        results = []
        if self.overlaps(other):
            results.append(Pair(min(self.beg, other.beg),
                           max(self.end, other.end)))
        return results


@dataclass
class Mapping:
    dst: Pair
    src: Pair

    def __contains__(self, number: int) -> bool:
        return number in self.src

    def __getitem__(self, number: int) -> int:
        if number in self:
            return number - self.src.beg + self.dst.beg

        raise IndexError(f'{number} not in {self}')

    @property
    def offset(self) -> int:
        return self.dst.beg-self.src.beg

    def adjusted(self, source: Pair) -> Pair:
        return Pair(source.beg+self.offset, source.end+self.offset)

    @classmethod
    def parse(cls, line: str) -> "Mapping":
        d, s, l = [int(x) for x in line.split(' ')]
        return cls(Pair(d, d+l-1), Pair(s, s+l-1))

    def __repr__(self) -> str:
        return f'{self.src.beg}-{self.src.end}->{self.dst.beg}-{self.dst.end}'


class SparseList:

    def __init__(self, thing: Union["SparseList", list[Pair]]):
        if isinstance(thing, self.__class__):
            self.data = thing.data.copy()
        else:
            self.data = thing.copy()
        self.data.sort()

    def __contains__(self, thing: [int | Pair]) -> bool:
        if isinstance(thing, int):
            for pair in self.data:
                if thing in pair:
                    return True
            else:
                return False
        else:
            for pair in self.data:
                if pair.overlaps(thing):
                    return True
            else:
                return False

    def __len__(self) -> int:
        return len(self.data)

    def combine(self):
        self.data.sort()

        # Combine overlapping pairs
        for i in range(len(self.data)-2, -1, -1):
            if self.data[i].overlaps(self.data[i+1]):
                self.data[i:i+1] = self.data[i].union(self.data[i+1])

    def add(self, thing: Pair) -> None:
        self.data.append(thing)
        self.combine()

    def remove(self, thing: Pair) -> None:
        indexes = list(range(len(self.data)-1, -1, -1))
        for i in indexes:
            pair = self.data[i]
            if thing.contains(pair):
                self.data[i:i+1] = []

            elif pair.contains(thing):
                self.data[i:i+1] = pair.disjoint(thing)
                break

            elif pair.leftlaps(thing) or pair.rightlaps(thing):
                self.data[i:i+1] = pair.disjoint(thing)

            elif thing.leftlaps(pair) or thing.rightlaps(pair):
                self.data[i:i+1] = thing.disjoint(pair)

    def sections(self, thing: Pair) -> list[Pair]:
        results = []
        for pair in self.data:
            if thing.overlaps(pair):
                results.extend(thing.intersection(pair))
        return results

    @property
    def smallest(self):
        return self.data[0].beg

    @property
    def size(self):
        return sum([len(pair) for pair in self.data])

    def __repr__(self) -> str:
        pairs = [f'{p.beg}->{p.end}' for p in self.data]
        return f'{self.__class__.__name__}({"|".join(pairs)})'


@dataclass
class Map:
    name: str
    source: Category
    target: Category
    mappings: list[Mapping]

    @classmethod
    def parse(cls, lines: list[str]) -> "Map":
        name, _, _ = lines[0].partition(' ')
        s, _, t = name.partition('-to-')
        mappings = [Mapping.parse(line) for line in lines[1:]]
        return cls(name, Category[s], Category[t], mappings)

    def apply_list(self, cells: list[int]) -> list[int]:
        result = cells.copy()
        for i, cell in enumerate(cells):
            for mapping in self.mappings:
                if cell in mapping:
                    result[i] = mapping[cell]
                    continue
        return result

    def apply_sparse_list(self, source: SparseList) -> SparseList:
        result = SparseList(source)
        for mapping in self.mappings:
            if mapping.src in source:
                sections = source.sections(mapping.src)
                for section in sections:
                    target = mapping.adjusted(section)
                    result.remove(section)
                    result.add(target)

        return result


@dataclass
class Almanac:
    lines: list[str]

    seeds: list[int] = field(default_factory=list)
    maps: OrderedDict[str, Map] = field(default_factory=OrderedDict)
    lists: dict[Category, list] = field(default_factory=dict)

    def __post_init__(self):
        _, _, s = self.lines[0].partition(': ')
        self.seeds = [int(seed) for seed in s.split(' ')]

        for pos in range(2, len(self.lines)):
            line = self.lines[pos]
            if line.endswith('map:'):
                start = pos
            elif line == '':
                map = Map.parse(self.lines[start:pos])
                self.maps[map.name] = map

        map = Map.parse(self.lines[start:])
        self.maps[map.name] = map

    @property
    def seed_pairs(self):
        return [Pair(self.seeds[n], self.seeds[n]+self.seeds[n+1]-1) for n in range(0, len(self.seeds), 2)]

    def apply_all_maps_to_lists(self) -> None:
        self.lists.clear()
        self.lists[Category.seed] = self.seeds
        for map in self.maps.values():
            source = self.lists[map.source]
            target = map.apply_list(source)
            self.lists[map.target] = target

    def apply_all_maps_to_sparse_lists(self) -> None:
        self.lists.clear()
        self.lists[Category.seed] = SparseList(self.seed_pairs)
        for map in self.maps.values():
            source = self.lists[map.source]
            target = map.apply_sparse_list(source)
            self.lists[map.target] = target

    def bruteforce(self) -> None:
        self.lists.clear()
        seeds = []
        for pair in self.seed_pairs:
            seeds.extend(range(pair.beg, pair.end+1))
        self.lists[Category.seed] = seeds
        for map in self.maps.values():
            source = self.lists[map.source]
            target = map.apply_list(source)
            self.lists[map.target] = target


class Day05(Puzzle):
    """If You Give A Seed A Fertilizer"""

    def parse_data(self, filename: str) -> Almanac:
        return Almanac(self.read_stripped(filename))

    def part1(self, data: Almanac) -> int:
        data.apply_all_maps_to_lists()
        return min(data.lists[Category.location])

    def part2(self, data: Almanac) -> int:
        data.apply_all_maps_to_sparse_lists()
        return data.lists[Category.location].smallest


puzzle = Day05()
puzzle.run(35, 46)
