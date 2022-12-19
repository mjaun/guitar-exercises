from __future__ import annotations

import random

from typing import List

from exercises import RhythmType, ExerciseDescriptor, exercise_from_shape_and_pattern
from music_theory import Scale
from fretboard import get_caged_shape, CagedPosition, Tuning, Position, Context
from output import add_exercise, write_file

melodic_sequences = [
    ExerciseDescriptor('1a*', [1, 1, 1, -2], RhythmType.STRAIGHT),
    ExerciseDescriptor('1b*', [1, 1, -2, 1], RhythmType.STRAIGHT),
    # ExerciseDescriptor('1c', [1, -2, 1, 1], RhythmType.STRAIGHT),
    ExerciseDescriptor('1d*', [-2, 1, 1, 1], RhythmType.STRAIGHT),
    # ExerciseDescriptor('1e', [-1, -1, 2, 1], RhythmType.STRAIGHT),
    ExerciseDescriptor('1f*', [1, 1, -1], RhythmType.STRAIGHT),
    ExerciseDescriptor('1g*', [1, 1, -1], RhythmType.TRIPLET),
    ExerciseDescriptor('1h*', [-1, -1, 3], RhythmType.TRIPLET),
    ExerciseDescriptor('1i*', [-1, 1, 1], RhythmType.TRIPLET),
    # ExerciseDescriptor('1j', [-1, 1, 1], RhythmType.TRIPLET),
    # ExerciseDescriptor('1k', [1, -1, 1], RhythmType.TRIPLET),
]

intervals = [
    ExerciseDescriptor('2a*', [2, -1], RhythmType.STRAIGHT),  # 3rds
    ExerciseDescriptor('2b*', [3, -2], RhythmType.STRAIGHT),  # 4ths
    # ExerciseDescriptor('2c', [4, -3], RhythmType.STRAIGHT),  # 5ths
    ExerciseDescriptor('2d*', [5, -4], RhythmType.STRAIGHT),  # 6ths
    # ExerciseDescriptor('2e', [6, -5], RhythmType.STRAIGHT),  # 7ths
    # ExerciseDescriptor('2f', [7, -6], RhythmType.STRAIGHT),  # 7ths
]

included_exercises: List[ExerciseDescriptor] = [
    # *melodic_sequences,
    *intervals,
]


def main():
    tuning = Tuning.from_text('E2-A2-D3-G3-B3-E4')
    scale = Scale.from_text('E dorian')
    ctx = Context(tuning, scale)

    shape = get_caged_shape(ctx, random.choice(list(CagedPosition)))

    print_shape(ctx, shape)
    print()

    exercise = random.choice(included_exercises)

    print(f'Exercise {exercise.name} ({exercise.rhythm}):')
    positions = exercise_from_shape_and_pattern(shape, exercise.pattern, reversed=False)
    add_exercise(positions, exercise.rhythm)
    print_tab(ctx, positions)
    print()
    positions = exercise_from_shape_and_pattern(shape, exercise.pattern, reversed=True)
    add_exercise(positions, exercise.rhythm)
    print_tab(ctx, positions)
    print()

    write_file()


def print_shape(ctx: Context, shape: List[Position]):
    min_fret = min(position.fret for position in shape)
    max_fret = max(position.fret for position in shape)

    line = ' '
    for fret in range(min_fret, max_fret + 1):
        line += str(fret).rjust(2) + '  '
    print(line)

    for string in range(ctx.tuning.string_count()):
        line = '|'
        for fret in range(min_fret, max_fret + 1):
            if Position(string, fret) in shape:
                line += '-x-|'
            else:
                line += '---|'
        print(line)


def print_tab(ctx: Context, positions: List[Position]):
    lines = ['-' for _ in range(ctx.tuning.string_count())]

    for position in positions:
        for string in range(len(lines)):
            if string == position.string:
                lines[string] += str(position.fret) + '-'
            else:
                lines[string] += '-' * (len(str(position.fret)) + 1)

    for line in lines:
        print(line)


if __name__ == '__main__':
    main()
