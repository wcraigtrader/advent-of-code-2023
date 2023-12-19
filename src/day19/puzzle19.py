from __future__ import annotations

import io
import re
from typing import Optional
from copy import deepcopy
from collections import Counter

from common import *


@dataclass
class Part:
    x: int
    m: int
    a: int
    s: int

    def value(self, key) -> int:
        return getattr(self, key)

    @property
    def rating(self):
        return self.x + self.m + self.a + self.s

    @classmethod
    def parse(cls, line) -> Part:
        x, m, a, s = map(int, re.findall(r'\d+', line))
        return cls(x, m, a, s)


@dataclass
class Rule:
    category: str
    condition: str
    threshold: int
    target: str

    def __repr__(self) -> str:
        if self.condition in '<>':
            return f'{self.category} {self.condition} {self.threshold} :: {self.target}'
        return f'default :: {self.target}'

    @property
    def default(self) -> bool:
        return self.condition not in '<>'

    def evaluate(self, part: Part) -> bool:
        if self.condition == '<':
            return part.value(self.category) < self.threshold
        elif self.condition == '>':
            return part.value(self.category) > self.threshold
        else:  # default
            return True


DEFAULT = range(1, 4001)


class Edge:

    def __init__(self, *args) -> None:
        self.x = DEFAULT
        self.m = DEFAULT
        self.a = DEFAULT
        self.s = DEFAULT
        self.target = None

        for arg in args:
            if isinstance(arg, str):
                self.target = arg
            elif isinstance(arg, Edge):
                self.x = arg.x
                self.m = arg.m
                self.a = arg.a
                self.s = arg.s
                self.target = arg.target

    def __repr__(self) -> str:
        categories = ''
        for category in 'xmas':
            cat = self[category]
            if cat == DEFAULT:
                continue
            if categories:
                categories += ', '
            if cat.start != DEFAULT.start and cat.stop != DEFAULT.stop:
                categories += f'{cat.start} < {category} < {cat.stop}'
            elif cat.start != DEFAULT.start:
                categories += f'{category} > {cat.start-1}'
            else:
                categories += f'{category} < {cat.stop}'
        return f'{self.target}({categories}) -> {self.value}'

    def __getitem__(self, key: str) -> range:
        if key in 'xmas':
            return getattr(self, key)
        raise KeyError

    def __setitem__(self, key: str, value: range) -> None:
        if key in 'xmas':
            setattr(self, key, value)
        else:
            raise KeyError

    def partition(self, rule: Rule) -> tuple[Edge, Edge]:
        if rule.condition not in '<>':
            raise ValueError

        chunk = Edge(self, rule.target)
        remains = Edge(self)

        cat = rule.category
        r = self[cat]

        if rule.condition == '<':
            if rule.threshold < r.start:
                chunk[cat] = range[0]
            elif r.start < rule.threshold < r.stop:
                chunk[cat] = range(r.start, rule.threshold)
                remains[cat] = range(rule.threshold, r.stop)
            elif r.stop < rule.threshold:
                remains[cat] = range(0)
            else:
                raise ValueError

        elif rule.condition == '>':
            if rule.threshold < r.start:
                remains[cat] = range(0)
            elif r.start < rule.threshold < r.stop:
                remains[cat] = range(r.start, rule.threshold+1)
                chunk[cat] = range(rule.threshold+1, r.stop)
            elif r.stop < rule.threshold:
                chunk[cat] = range(0)
            else:
                raise ValueError

        return chunk, remains

    @property
    def value(self) -> int:
        return len(self.x) * len(self.m) * len(self.a) * len(self.s)


@dataclass
class Workflow:
    name: str
    rules: list[Rule]

    @property
    def default(self) -> str:
        return self.rules[-1].target

    def evaluate(self, part: Part) -> str:
        for rule in self.rules:
            if rule.evaluate(part):
                return rule.target
        return self.default

    @property
    def results(self) -> list(str):
        results = set([rule.target for rule in self.rules])
        return list(results)

    @classmethod
    def parse(cls, line) -> Workflow:
        line = line.replace('}', '')
        name, _, rest = line.partition('{')
        chunks = rest.split(',')
        rules = []
        for chunk in chunks[:-1]:
            match = re.match(r'([xmas])([<>])(\d+):(.+)', chunk)
            category, condition, threshold, target = match.groups()
            threshold = int(threshold)
            rules.append(Rule(category, condition, threshold, target))
        rules.append(Rule('', 'default', 0, chunks[-1]))
        return cls(name, rules)


class Ratings:

    def __init__(self, lines: list[str]) -> None:
        self.flows: dict[str, Workflow] = {}
        self.parts: list[Part] = []
        self.load_workflows(lines)

    def load_workflows(self, lines: list[str]) -> None:
        section = 1
        for line in lines:
            if line == '':
                section += 1
            elif section == 1:
                workflow = Workflow.parse(line)
                self.flows[workflow.name] = workflow
            elif section == 2:
                self.parts.append(Part.parse(line))

    @property
    def render(self) -> str:
        with io.StringIO() as buf:
            buf.write('''digraph {
  "in" [color=orange]
  "A" [color=green]
  "R" [color=red]

''')
            line_attrs = ''  # 'color="purple"'

            order = list(sorted(self.flows))
            order.remove('in')
            order.insert(0, 'in')

            for name in order:
                flow = self.flows[name]
                for rule in flow.rules[:-1]:
                    buf.write(
                        f'  "{flow.name}" -> "{rule.target}" [label="{rule.category} {rule.condition} {rule.threshold}" {line_attrs}]\n')
                buf.write(
                    f'  "{flow.name}" -> "{flow.default}" [label="default" {line_attrs}]\n\n')
            buf.write('}\n')
            return buf.getvalue()

    def reduce(self) -> None:
        self.reduce_flows_1()
        self.reduce_flows_2()

    def reduce_flows_1(self) -> None:
        """For any workflow with all targets the same,
        remove it and repoint any rules that reference it to its target"""

        for flow in list(self.flows.values()):
            results = flow.results
            if len(results) == 1:
                self.remove_one_flow(flow.name, results[0])

    def remove_one_flow(self, source: str, target: str) -> None:
        del self.flows[source]
        for flow in self.flows.values():
            for rule in flow.rules:
                if rule.target == source:
                    rule.target = target

    def reduce_flows_2(self) -> None:
        """For any workflow that's only referenced by the default rule in one workflow,
        append its rules to the end of the referring flow, and change the referring
        default to the old rule's default."""

        backlinks: dict[str, set[str]] = {}
        for flow in self.flows.values():
            for rule in flow.rules:
                backlinks.setdefault(rule.target, set()).add(flow.name)
            backlinks.setdefault(flow.default, set()).add(flow.name)

        for name, links in backlinks.items():
            if name in ['in', 'A', 'R'] or len(links) != 1:
                continue
            sname = list(links)[0]
            if sname in self.flows:
                source = self.flows[sname]
                if source.default == name:
                    self.collapse_one_flow(self.flows[name], source)

    def collapse_one_flow(self, target: Workflow, source: Workflow) -> None:
        del self.flows[target.name]
        source.rules.pop(-1)
        source.rules.extend(target.rules)

    def evaluate(self, part: Part) -> bool:
        wf = self.flows['in']
        while wf:
            result = wf.evaluate(part)
            if result == 'A':
                return True
            elif result == 'R':
                return False
            else:
                wf = self.flows[result]
        return True

    def accepted(self) -> list[Part]:
        accepted = [part for part in self.parts if self.evaluate(part)]
        return accepted

    def predicted(self) -> int:
        accepted: list[Edge] = []
        edges: list[Edge] = [Edge('in')]

        while len(edges):
            edge = edges.pop(0)
            flow = self.flows[edge.target]
            for rule in flow.rules:
                if rule.default:
                    if rule.target == 'A':
                        accepted.append(edge)
                    elif rule.target != 'R':
                        edges.append(Edge(edge, rule.target))
                else:
                    chunk, edge = edge.partition(rule)
                    if rule.target == 'A':
                        accepted.append(Edge(chunk, flow.name))
                    elif rule.target != 'R':
                        edges.append(chunk)

        return sum([edge.value for edge in accepted])


class Day19(Puzzle):
    """Aplenty"""

    def parse_data(self, filename: str) -> Data:
        ratings = Ratings(self.read_stripped(filename))
        # with open(self.data_path(filename, '.dot'), 'w') as df:
        #     df.write(ratings.render)
        # ratings.reduce_flows_1()
        # with open(self.data_path(filename, '1.dot'), 'w') as df:
        #     df.write(ratings.render)
        # ratings.reduce_flows_2()
        # with open(self.data_path(filename, '2.dot'), 'w') as df:
        #     df.write(ratings.render)
        return ratings

    def part1(self, data: Data) -> PuzzleResult:
        accepted = data.accepted()
        return sum([part.rating for part in accepted])

    def part2(self, data: Data) -> PuzzleResult:
        return data.predicted()


puzzle = Day19()
puzzle.run(19114, 167409079868000)
