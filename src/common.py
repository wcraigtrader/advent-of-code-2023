from __future__ import annotations

from dataclasses import dataclass, field
from functools import cache, cached_property

from grid import (
    Grid,
    GridCol,
    GridDirection,
    GridOrthogonalDistance,
    GridPosition,
    GridRow,
)
from runner import (
    IGNORE,
    Data,
    Puzzle,
    PuzzleResult,
)
from search import (
    AstarNode,
    AstarSearch,
)

if __name__ == '__main__':
    print('You meant to run a Puzzle!')
