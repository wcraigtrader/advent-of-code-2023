from __future__ import annotations

from collections import Counter
from enum import Enum
from typing import Optional

from common import *

PulseType = bool
LOW = False
HIGH = True


class ModuleType(Enum):
    BROADCAST = 1
    FLIPFLOP = 2
    CONJUNCTION = 3
    OTHER = 4


@dataclass(unsafe_hash=True)
class Module:
    name: str = field(hash=True, compare=True)
    type: ModuleType = field(hash=True, compare=True)
    targets: Optional[list[str]] = field(hash=False, compare=False, default=list)

    state: PulseType = field(hash=False, compare=False, default=LOW)
    saved: dict[Module, PulseType] = field(
        hash=False, compare=False, default_factory=dict
    )

    @classmethod
    def parse(cls, line) -> Module:
        label, _, modules = line.partition(" -> ")

        if label == "broadcaster":
            type = ModuleType.BROADCAST
            name = label
        elif label.startswith("%"):
            type = ModuleType.FLIPFLOP
            name = label[1:]
        elif label.startswith("&"):
            type = ModuleType.CONJUNCTION
            name = label[1:]
        else:
            type = ModuleType.OTHER
            name = label

        targets = modules.split(", ")

        return cls(name, type, targets)


@dataclass
class Pulse:
    pulse: PulseType
    source: Optional[Module]
    target: Module


class Propagator:
    def __init__(self, lines: list[str]):
        self.modules: dict[str, Module] = {m.name: m for m in map(Module.parse, lines)}
        self.broadcaster: Module = None

        self.counts: Counter = Counter()
        self.pulses: list[Pulse] = []
        self.low: Counter = Counter()

        for module in list(self.modules.values()):
            if module.type == ModuleType.BROADCAST:
                self.broadcaster = module
            for name in module.targets:
                if name not in self.modules:
                    self.modules[name] = Module(name, ModuleType.OTHER)
                else:
                    target = self.modules[name]
                    if target.type == ModuleType.CONJUNCTION:
                        target.saved[module] = LOW

    def reset(self):
        self.counts.clear()
        self.pulses.clear()
        
        for module in self.modules.values():
            if module.type == ModuleType.FLIPFLOP:
                module.state = LOW
            elif module.type == ModuleType.CONJUNCTION:
                for source in module.saved.keys():
                    module.saved[source] = LOW

    def push_once(self):
        self.send(LOW, None, self.broadcaster)

        while self.pulses:
            action = self.pulses.pop(0)
            pulse = action.pulse
            source = action.source
            module = action.target
            self.counts[pulse] += 1
            if pulse == LOW:
                self.low[module] += 1

            if module.type == ModuleType.BROADCAST:
                self.send(pulse, module, *module.targets)

            elif module.type == ModuleType.FLIPFLOP:
                if pulse == LOW:
                    module.state = not module.state
                    self.send(module.state, module, *module.targets)

            elif module.type == ModuleType.CONJUNCTION:
                module.saved[source] = pulse
                if all(module.saved.values()):
                    self.send(LOW, module, *module.targets)
                else:
                    self.send(HIGH, module, *module.targets)
                    
        return

    def send(
        self,
        pulse: PulseType,
        source: Optional[Module],
        *targets: str | Module,
    ) -> None:
        for target in targets:
            if isinstance(target, str):
                target = self.modules[target]
            assert isinstance(target, Module)
            self.pulses.append(Pulse(pulse, source, target))

    def push(self, qty: int) -> tuple[int, int]:
        for _ in range(qty):
            self.push_once()

        return (self.counts[LOW], self.counts[HIGH])

    def push_to_rx(self) -> int:
        self.reset()
        
        rx = self.modules.get('rx')
        assert rx, 'rx not in modules list'

        count = 0
        while self.low[rx] != 1:
            count += 1
            self.low.clear()
            self.push_once()
            if self.low[rx] != 0:
                print(count, self.low[rx])
            
        return count

class Day20(Puzzle):
    """Pulse Propagation"""

    def parse_data(self, filename: str) -> Propagator:
        return Propagator(self.read_stripped(filename))

    def part1(self, data: Propagator) -> PuzzleResult:
        low, high = data.push(1000)
        return low * high

    def part2(self, data: Propagator) -> PuzzleResult:
        return data.push_to_rx()


puzzle = Day20("real.data", "test1.data", "test2.data")
puzzle.run([32000000, 11687500])
