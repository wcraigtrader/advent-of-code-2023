from __future__ import annotations

from collections.abc import MutableMapping, KeysView, ItemsView, ValuesView
from typing import Any, Iterator, Mapping, Optional

GridPosition = GridDirection = complex


def GridRow(position: GridPosition) -> int:
    return int(position.real)


def GridCol(position: GridPosition) -> int:
    return int(position.imag)


def GridOrthogonalDistance(src: GridPosition, tgt: GridPosition) -> int:
    return abs(GridRow(tgt)-GridRow(src))+abs(GridCol(tgt)-GridCol(src))


class Grid(MutableMapping):

    _properties = [
        '_rows',
        '_cols',
        '_offset',
        '_sparse',
        '_origin',
        '_default',
    ]

    def __init__(self, source: list[str] | Grid = None, **keywords):
        self._grid: Mapping[GridPosition, Any] = {}
        self._offset: int = 0
        self._sparse: bool = False
        self._origin: str = 'ul'
        self._default: Any = None
        self._dynamic: bool = False

        self._min_row: int = 1_000_000_000_000
        self._max_row: int = -1_000_000_000_000
        self._min_col: int = 1_000_000_000_000
        self._max_col: int = -1_000_000_000_000

        if source is None:
            self._rows = keywords.get('rows', 0)
            self._cols = keywords.get('cols', 0)
            self._init(**keywords)
        elif issubclass(source.__class__, Grid):
            for p in self._properties:
                setattr(self, p, getattr(source, p))
            self._init(**keywords)
            empty = keywords.get('empty', False)
            if not empty:
                self._grid = source._grid.copy()
        elif isinstance(source, list):
            self._init(**keywords)
            self._parse(source, **keywords)
        elif isinstance(source, str):
            self._init(**keywords)
            self._parse(source.strip().split('\n'), **keywords)

        else:
            raise ValueError('Invalid source: {source}')

    def _init(self, **keywords) -> None:
        self._offset = keywords.get('offset', 0)
        self._sparse = keywords.get('sparse', False)
        self._origin = keywords.get('origin', 'ul')
        self._default = keywords.get('default', None)
        self._dynamic = keywords.get('dynamic', False)

    def _parse(self, source: list[str], **keywords) -> None:
        transpose = keywords.get('transpose', False)
        conversion = keywords.get('conversion', None)

        rows = len(source)
        cols = len(source[0])

        self._rows: int = cols if transpose else rows
        self._cols: int = rows if transpose else cols

        for row, line in enumerate(source):
            for col, value in enumerate(line):
                r, c = row + self._offset, col + self._offset
                if transpose:
                    r, c = c, r
                if self._origin == 'll':
                    r = self._rows + self._offset - r

                if conversion:
                    value = conversion(value)

                if not (self._sparse and value is None):
                    self._grid[GridPosition(r, c)] = value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._rows}, {self._cols})'

    def __getitem__(self, key: GridPosition) -> Any:
        if isinstance(key, GridPosition):
            if key in self._grid:
                return self._grid[key]
            elif self._sparse:
                return self._default
            else:
                raise IndexError
        raise KeyError

    def __setitem__(self, key: GridPosition, value: Any) -> None:
        if isinstance(key, GridPosition):
            self._grid[key] = value
            if self._dynamic:
                self._min_row = min(self._min_row, GridRow(key))
                self._max_row = max(self._max_row, GridRow(key))
                self._min_col = min(self._min_col, GridCol(key))
                self._max_col = max(self._max_col, GridCol(key))
                self._rows = self._max_row - self._min_row + 1
                self._cols = self._max_col - self._min_col + 1
            return
        raise KeyError

    def __delitem__(self, key: GridPosition) -> None:
        if isinstance(key, GridPosition):
            if key in self._grid:
                del self._grid[key]
                return
            elif self._sparse:
                return
            else:
                raise IndexError
        raise KeyError

    def __contains__(self, key: GridPosition) -> bool:
        return key in self._grid

    def __len__(self) -> int:
        return len(self._grid)

    def __iter__(self) -> Iterator:
        return KeysView(self._grid)

    def __eq__(self, other: Grid) -> bool:
        if any([getattr(self, p) != getattr(other, p) for p in self._properties]):
            return False

        if len(self._grid) != len(other._grid):
            return False

        return all([v == other._grid[k] for k, v in self._grid.items()])

    def __str__(self) -> str:
        rows = reversed(self.row_range) if self._origin == 'll' else self.row_range
        lines = [f'{r:3d}: {self.render_row(r)}' for r in rows]
        return '\n'.join(lines)

    def keys(self):
        return KeysView(self._grid)

    def values(self):
        return ValuesView(self._grid)

    def items(self):
        return ItemsView(self._grid)

    def clear(self) -> None:
        self._grid.clear()

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    @property
    def center(self) -> GridPosition:
        if self._dynamic:
            row = (self._max_row - self._min_row) // 2 + self._min_row
            col = (self._max_col - self._min_col) // 2 + self._min_col
        else:
            row = self.rows // 2 + self._offset
            col = self.cols // 2 + self._offset
        return GridPosition(row, col)

    @property
    def row_range(self) -> range:
        if self._dynamic:
            return range(self._min_row, self._max_row+1)
        return range(self._offset, self._rows + self._offset)

    @property
    def col_range(self) -> range:
        if self._dynamic:
            return range(self._min_col, self._max_col+1)
        return range(self._offset, self._cols+self._offset)

    @property
    def lines(self) -> list[str]:
        return [self.render_row(r) for r in self.row_range]

    def render(self, value: Any) -> str:
        return ' ' if value is None else str(value)[0]

    def render_row(self, row: int) -> str:
            return ''.join([self.render(v) for v in self.row(row)])

    def row(self, r: int) -> list[Any]:
        return [self[GridPosition(r, c)] for c in self.col_range]

    def col(self, c: int) -> list[Any]:
        return [self[GridPosition(r, c)] for r in self.row_range]

    def inbounds(self, position: GridPosition) -> bool:
        return (GridRow(position) in self.row_range and
                GridCol(position) in self.col_range)
