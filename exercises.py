from __future__ import annotations

from enum import Enum, auto
from typing import NamedTuple, List

from fretboard import Position


class ExerciseDescriptor(NamedTuple):
    name: str
    pattern: List[int]
    feel: Feel


class Feel(Enum):
    STRAIGHT = auto(),
    TRIPLET = auto(),

    def __str__(self):
        lookup_table = {
            Feel.STRAIGHT: 'straight',
            Feel.TRIPLET: 'triplet',
        }

        return lookup_table[self]


def generate_exercise(shape: List[Position], pattern: List[int], reverse=False) -> List[Position]:
    assert sum(pattern) > 0

    if reverse:
        shape = list(reversed(shape))

    result = []
    current_index = -min(sum(pattern[:n]) for n in range(len(pattern)))

    while True:
        cycle = [shape[current_index]]

        for i in range(len(pattern) - 1):
            current_index += pattern[i]
            if current_index >= len(shape):
                return result

            cycle.append(shape[current_index])

        result.extend(cycle)

        current_index += pattern[-1]
        if current_index >= len(shape):
            return result
