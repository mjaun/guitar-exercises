from __future__ import annotations

import random
from typing import List

from exercises import Feel, ExerciseDescriptor, generate_exercise
from fretboard import Tuning, Context, get_all_caged_shapes
from music_theory import Scale
from output import GuitarProFile, print_shape, print_tab

tuning_text = 'E2-A2-D3-G3-B3-E4'
scale_text = 'E Aeolian'
number_of_exercises = 3

ED = ExerciseDescriptor

melodic_sequences = [
    ED('Melodic Sequences: 1a*', [1, 1, 1, -2], Feel.STRAIGHT),
    ED('Melodic Sequences: 1b*', [1, 1, -2, 1], Feel.STRAIGHT),
    # ED('Melodic Sequences: 1c', [1, -2, 1, 1], Feel.STRAIGHT),
    ED('Melodic Sequences: 1d*', [-2, 1, 1, 1], Feel.STRAIGHT),
    # ED('Melodic Sequences: 1e', [-1, -1, 2, 1], Feel.STRAIGHT),
    # ED('Melodic Sequences: 1f*', [1, 1, -1], Feel.STRAIGHT),
    ED('Melodic Sequences: 1g*', [1, 1, -1], Feel.TRIPLET),
    ED('Melodic Sequences: 1h*', [-1, -1, 3], Feel.TRIPLET),
    ED('Melodic Sequences: 1i*', [-1, 1, 1], Feel.TRIPLET),
    # ED('Melodic Sequences: 1j', [1, -1, 1], Feel.TRIPLET),
    # ED('Melodic Sequences: 1k', [1, 1, 1, -2], Feel.TRIPLET),
]

intervals = {
    '3rds*': 2,
    '4ths*': 3,
    # '5ths': 4,
    '6ths*': 5,
    # '7ths': 6,
    # 'Octaves': 7,
}

interval_patterns = [
    *[ED(f'{n}: Normal*', [s, -(s - 1)], Feel.STRAIGHT) for n, s in intervals.items()],
    *[ED(f'{n}: Inverted*', [-s, (s + 1)], Feel.STRAIGHT) for n, s in intervals.items()],
    *[ED(f'{n}: One Up, One Down*', [s, 1, -s, 1], Feel.STRAIGHT) for n, s in intervals.items()],
    # *[ED(f'{n}: One Down, One Up', [-s, 1, s, 1], Feel.STRAIGHT) for n, s in intervals.items()],
    *[ED(f'{n}: Two Up, One Down*', [s, -(s - 1), s, 1, -s, 1], Feel.STRAIGHT) for n, s in intervals.items()],
    # *[ED(f'{n}: Two Down, One Up', [-s, (s + 1), -s, 1, s, 1], Feel.STRAIGHT) for n, s in intervals.items()],
    # *[ED(f'{n}: In Triplets*', [s, -(s - 1)], Feel.TRIPLET) for n, s in intervals.items()],
    # *[ED(f'{n}: One Up, One Down, In Triplets*', [s, 1, -s], Feel.TRIPLET) for n, s in intervals.items()],
]

all_exercises: List[ExerciseDescriptor] = [
    *melodic_sequences,
    *interval_patterns,
]


def main():
    ctx = Context(Tuning.from_text(tuning_text), Scale.from_text(scale_text))
    caged_position, shape = random.choice(get_all_caged_shapes(ctx))

    print_header(f'{scale_text} - {caged_position.name} Shape')
    print_shape(ctx, shape)

    output_file = GuitarProFile('Exercises', f'{scale_text} - {caged_position.name} Shape')

    for exercise in random.sample(all_exercises, k=number_of_exercises):
        positions = generate_exercise(shape, exercise.pattern)

        print_header(exercise.name)
        print_tab(ctx, positions)

        output_file.add_exercise(exercise.name, positions, exercise.feel)

        positions = generate_exercise(shape, exercise.pattern, reverse=True)
        output_file.add_exercise('', positions, exercise.feel)

    output_file.write('exercises.gp5')


def print_header(text: str):
    print()
    print(text)
    print('=' * len(text))


if __name__ == '__main__':
    main()
