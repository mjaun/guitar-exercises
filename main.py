from __future__ import annotations

import argparse
import random

from typing import List
from exercises import Feel, ExerciseDescriptor, generate_exercise
from fretboard import Tuning, Context, get_all_caged_shapes
from music_theory import Scale
from output import GuitarProFile, print_shape, print_tab, print_header

ED = ExerciseDescriptor

# Tuning used for the generated exercises
tuning_text = 'E2-A2-D3-G3-B3-E4'

# Scales used for the generated exercises
scale_texts = [
    'E Aeolian',
    'A Aeolian',
    'G Aeolian',
    'D Aeolian',
]

# Exercises with melodic sequences
melodic_sequences = [
    ED('Melodic Sequences: 1a*', [1, 1, 1, -2], Feel.STRAIGHT),
    ED('Melodic Sequences: 1b*', [1, 1, -2, 1], Feel.STRAIGHT),
    # ED('Melodic Sequences: 1c', [1, -2, 1, 1], Feel.STRAIGHT),
    ED('Melodic Sequences: 1d*', [-2, 1, 1, 1], Feel.STRAIGHT),
    # ED('Melodic Sequences: 1e', [-1, -1, 2, 1], Feel.STRAIGHT),
    ED('Melodic Sequences: 1f*', [1, 1, -1], Feel.STRAIGHT),
    ED('Melodic Sequences: 1g*', [1, 1, -1], Feel.TRIPLET),
    ED('Melodic Sequences: 1h*', [-1, -1, 3], Feel.TRIPLET),
    ED('Melodic Sequences: 1i*', [-1, 1, 1], Feel.TRIPLET),
    # ED('Melodic Sequences: 1j', [1, -1, 1], Feel.TRIPLET),
    # ED('Melodic Sequences: 1k', [1, 1, 1, -2], Feel.TRIPLET),
]

# Exercises with intervals
intervals = {
    '3rds*': 2,
    # '4ths*': 3,
    # '5ths': 4,
    # '6ths*': 5,
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

# Exercises with triads
triad_patterns = [
    ED('Triads: Ascending*', [2, 2, -3], Feel.TRIPLET),
    ED('Triads: Descending*', [-2, -2, 5], Feel.TRIPLET),
    ED('Triads: Combined*', [2, 2, 1, -2, -2, 1], Feel.TRIPLET),
    ED('Triads: High, Low, Middle*', [-4, 2, 3], Feel.TRIPLET),
    # ED('Triads: Middle, High, Low', [2, -4, 3], Feel.TRIPLET),
    ED('Triads: Four Note Pattern, Low Note Doubled*', [2, 2, -4, 1], Feel.STRAIGHT),
    # ED('Triads: Four Note Pattern, Middle Note Doubled', [2, 2, -2, -1], Feel.STRAIGHT),
    # ED('Triads: Four Note Pattern, Low Note Doubled 2', [4, -2, -2, 1], Feel.STRAIGHT),
    # ED('Triads: Four Note Pattern, Middle Note Doubled 2', [-2, 2, 2, -1], Feel.STRAIGHT),
    ED('Triads: Four Note Pattern, High Note Doubled*', [-4, 2, 2, 1], Feel.STRAIGHT),
    # ED('Triads: Ascending, 3 Against 2 Feel*', [2, 2, -3], Feel.STRAIGHT),
    # ED('Triads: Descending, 3 Against 2 Feel', [-2, -2, 5], Feel.STRAIGHT),
    # ED('Triads: Combined, 3 Against 2 Feel', [2, 2, 1, -2, -2, 1], Feel.STRAIGHT),
    # ED('Triads: Reversed Combined, 3 Against 2 Feel', [-2, -2, 1, 2, 2, 1], Feel.STRAIGHT),
]

# Exercises with arpeggios
arpeggio_patterns = [
    ED('Arpeggios: Ascending*', [2, 2, 2, -5], Feel.STRAIGHT),
    ED('Arpeggios: Descending*', [-2, -2, -2, 7], Feel.STRAIGHT),
    # ED('Arpeggios: Ascend Then Descend', [2, 2, 2, 1, -2, -2, -2, 1], Feel.STRAIGHT),
    # ED('Arpeggios: Descend Then Ascend', [-2, -2, -2, 1, 2, 2, 2, 1], Feel.STRAIGHT),
    # ED('Arpeggios: Low To High Then Descend', [6, -2, -2, -1], Feel.STRAIGHT),
    # ED('Arpeggios: Descend Then Jump', [-2, -2, 6, -1], Feel.STRAIGHT),
    # ED('Arpeggios: 4 Against 3 Feel Ascending*', [2, 2, 2, -5], Feel.TRIPLET),
    # ED('Arpeggios: 4 Against 3 Feel Descending*', [-2, -2, -2, 7], Feel.TRIPLET),
    # ED('Arpeggios: 4 Against 3 Feel Ascend Then Descend*', [2, 2, 2, 1, -2, -2, -2, 1], Feel.TRIPLET),
    # ED('Arpeggios: 4 Against 3 Feel Descend Then Ascend', [-2, -2, -2, 1, 2, 2, 2, 1], Feel.TRIPLET),
]

# Collect all exercises in a single list
all_exercises: List[ExerciseDescriptor] = [
    *melodic_sequences,
    *interval_patterns,
    *triad_patterns,
    *arpeggio_patterns,
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output_file', help='Path to the generated GuitarPro file.')
    args = parser.parse_args()

    # determine shape for the exercise
    scale_text = random.choice(scale_texts)
    ctx = Context(Tuning.from_text(tuning_text), Scale.from_text(scale_text))
    caged_position, shape = random.choice(list(get_all_caged_shapes(ctx).items()))

    # generate exercise
    exercise = random.choice(all_exercises)
    positions = generate_exercise(shape, exercise.pattern)
    positions_reverse = generate_exercise(shape, exercise.pattern, reverse=True)

    # print to console
    print_header(f'{scale_text} - {caged_position.name} Shape')
    print_shape(ctx, shape)

    print_header(exercise.name)
    print_tab(ctx, positions)
    print()

    # write to file
    output_file = GuitarProFile('Exercises', f'{scale_text} - {caged_position.name} Shape')
    output_file.add_exercise(exercise.name, positions, exercise.feel)
    output_file.add_exercise('', positions_reverse, exercise.feel)
    output_file.write(args.output_file)


if __name__ == '__main__':
    main()
