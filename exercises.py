from __future__ import annotations

from enum import Enum, auto
from typing import NamedTuple, List

from fretboard import Position, Shape


class ExerciseDescriptor(NamedTuple):
    """
    Represents a type of exercise defined by a name, a pattern and a feel.

    A pattern is a list of offsets in which a shape is traversed. For example:
    - [1] Is playing the shape linearly.
    - [1, 1, -1] Is playing the shape two notes ascending, then one descending.
    - [2, -1] Is playing the shape in thirds (assuming the shape consists of seconds).
    """

    name: str
    pattern: List[int]
    feel: Feel


class Feel(Enum):
    """
    Represents the feel of an exercise.
    """

    STRAIGHT = auto(),
    TRIPLET = auto(),

    def __str__(self):
        lookup_table = {
            Feel.STRAIGHT: 'straight',
            Feel.TRIPLET: 'triplet',
        }

        return lookup_table[self]


def generate_exercise(shape: Shape, pattern: List[int], reverse=False) -> List[Position]:
    """
    Generates the positions to play a given shape in the given pattern.

    :param shape: The shape to play.
    :param pattern: The pattern used to traverse the shape.
    :param reverse: True, to traverse reversed. False, otherwise.
    :return: The positions to play the exercise.
    """

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
