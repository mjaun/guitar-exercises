from __future__ import annotations

import itertools
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

    pattern_iterator = itertools.cycle(pattern)

    while current_index < len(shape):
        result.append(shape[current_index])
        current_index += next(pattern_iterator)

    return result
