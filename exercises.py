from __future__ import annotations

import itertools
from enum import Enum, auto
from typing import NamedTuple, List

from fretboard import Position


class RhythmType(Enum):
    STRAIGHT = auto(),
    TRIPLET = auto(),

    def __str__(self):
        lookup_table = {
            RhythmType.STRAIGHT: 'straight',
            RhythmType.TRIPLET: 'triplet',
        }

        return lookup_table[self]


class ExerciseDescriptor(NamedTuple):
    name: str
    pattern: List[int]
    rhythm: RhythmType


def exercise_from_shape_and_pattern(shape: List[Position], pattern: List[int]) -> List[Position]:
    assert sum(pattern) > 0

    result = []
    current_index = -min(sum(pattern[:n]) for n in range(len(pattern)))

    pattern_iterator = itertools.cycle(pattern)

    while current_index < len(shape):
        result.append(shape[current_index])
        current_index += next(pattern_iterator)

    return result
