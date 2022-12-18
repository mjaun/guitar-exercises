from __future__ import annotations

import functools
import re

from enum import Enum, auto
from typing import List, Optional, NamedTuple, Union


def main():
    tuning = Tuning.from_text('E2-A2-D3-G3-B3-E4')
    scale = Scale.from_text('A major pentatonic')
    ctx = Context(tuning, scale)

    for position in CagedPosition:
        pattern = get_caged_pattern(ctx, position)
        print_pattern(ctx, pattern)


def print_pattern(ctx: Context, pattern: List[Position]):
    min_fret = min(position.fret for position in pattern)
    max_fret = max(position.fret for position in pattern)

    line = ' '
    for fret in range(min_fret, max_fret + 1):
        line += str(fret).rjust(2) + '  '
    print(line)

    for string in range(ctx.tuning.string_count()):
        line = '|'
        for fret in range(min_fret, max_fret + 1):
            if Position(string, fret) in pattern:
                line += '-x-|'
            else:
                line += '---|'
        print(line)


def get_caged_pattern(ctx: Context, caged_position: CagedPosition) -> List[Position]:
    string_count = ctx.tuning.string_count()

    # step one: figure out which scale degrees are on which string
    range_per_string = {
        CagedPosition.C: [('3', 'b6'), ('7', 'b3'), ('#4', 'b7'), ('2', '4'), ('6', 'b2'), ('3', 'b6')],
        CagedPosition.A: [('#4', 'b7'), ('2', '4'), ('6', 'b2'), ('3', 'b6'), ('7', 'b3'), ('#4', 'b7')],
        CagedPosition.G: [('6', 'b2'), ('3', 'b6'), ('7', 'b3'), ('#4', 'b7'), ('2', '4'), ('6', 'b2')],
        CagedPosition.E: [('7', 'b3'), ('#4', 'b7'), ('2', '4'), ('6', 'b2'), ('3', 'b6'), ('7', 'b3')],
        CagedPosition.D: [('2', '4'), ('6', 'b2'), ('3', 'b6'), ('7', 'b3'), ('#4', 'b7'), ('2', '4')],
    }

    degrees_per_string: List[List[ScaleDegree]] = [[] for _ in range(string_count)]

    for string in range(string_count):
        current_degree = ScaleDegree.from_text(range_per_string[caged_position][string][0])
        last_degree = ScaleDegree.from_text(range_per_string[caged_position][string][1])

        while True:
            if current_degree in ctx.scale.degrees:
                degrees_per_string[string].append(current_degree)

            if current_degree == last_degree:
                break

            current_degree = current_degree.add_half_steps(1)

    # step two: figure out positions
    positions: List[Position] = []
    last_abs_note: Optional[AbsNote] = None

    for string in reversed(range(string_count)):
        for degree in degrees_per_string[string]:
            rel_note = ctx.scale.get_rel_note(degree)

            if not last_abs_note:
                fret = ctx.tuning.get_fret(string, rel_note)
                abs_note = ctx.tuning.get_note(Position(string, fret))
            else:
                abs_note = last_abs_note.next(rel_note)
                fret = ctx.tuning.get_fret(string, abs_note)

            positions.append(Position(string, fret))
            last_abs_note = abs_note

    # step three: move an octave up if necessary
    if any(position.fret < 0 for position in positions):
        positions = [Position(position.string, position.fret + 12) for position in positions]

    return positions


class CagedPosition(Enum):
    C = auto()
    A = auto()
    G = auto()
    E = auto()
    D = auto()


class Context:
    def __init__(self, tuning: Tuning, scale: Scale):
        self.tuning = tuning
        self.scale = scale


class Tuning:
    @staticmethod
    def from_text(text: str):
        return Tuning([AbsNote.from_text(x) for x in reversed(text.split('-'))])

    def __init__(self, strings: List[AbsNote]):
        self.strings = strings

    def string_count(self) -> int:
        return len(self.strings)

    def get_note(self, position: Position):
        return AbsNote(self.strings[position.string].value + position.fret)

    def get_fret(self, string: int, note: Union[RelNote, AbsNote]) -> int:
        open_note = self.strings[string]

        if isinstance(note, AbsNote):
            return note.value - open_note.value

        if isinstance(note, RelNote):
            if open_note.rel_note() == note:
                return 0
            else:
                return open_note.next(note).value - open_note.value

        raise NotImplementedError()


class Position(NamedTuple):
    string: int
    fret: int


class Scale:
    @staticmethod
    def from_text(text: str):
        parts = text.split()
        root_text = parts[0]
        scale_type_text = ' '.join(parts[1:])

        return Scale(RelNote.from_text(root_text), ScaleType.from_text(scale_type_text))

    def __init__(self, root: RelNote, scale_type: ScaleType):
        self.root = root
        self.degrees = scale_type.degrees

    def get_scale_degree(self, note: Union[AbsNote, RelNote]) -> ScaleDegree:
        if isinstance(note, AbsNote):
            note = note.rel_note()

        if self.root.value < note.value:
            return ScaleDegree(note.value - self.root.value)
        else:
            return ScaleDegree(note.value - self.root.value + 12)

    def get_rel_note(self, scale_degree: ScaleDegree):
        return RelNote((self.root.value + scale_degree.value) % 12)


class ScaleType:
    common_types = {
        'minor pentatonic': '1-b3-4-5-b7',
        'major pentatonic': '1-2-3-5-6',
        'ionian': '1-2-3-4-5-6-7',
        # ...
    }

    @staticmethod
    def from_text(text: str):
        if text in ScaleType.common_types:
            text = ScaleType.common_types[text]

        return ScaleType([ScaleDegree.from_text(x) for x in text.split('-')])

    def __init__(self, degrees: List[ScaleDegree]):
        self.degrees = degrees


@functools.total_ordering
class ScaleDegree:
    values_by_name = {'1': 0, '2': 2, '3': 4, '4': 5, '5': 7, '6': 9, '7': 11}
    default_names = ['1', 'b2', '2', 'b3', '3', '4', 'b5', '5', 'b6', '6', 'b7', '7']

    @staticmethod
    def from_text(text: str):
        match = re.match('(b+|#+)?([1-7])', text)
        assert match

        name_value = ScaleDegree.values_by_name[match[2]]
        accidentals_value = get_accidentals_value(match[1])

        return ScaleDegree(name_value + accidentals_value)

    def __init__(self, value: int):
        assert 0 <= value < 12
        self.value = value

    def add_half_steps(self, half_steps: int) -> ScaleDegree:
        return ScaleDegree((self.value + half_steps) % 12)

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other: ScaleDegree):
        return self.value == other.value

    def __lt__(self, other: ScaleDegree):
        return self.value < other.value

    def __repr__(self):
        return ScaleDegree.default_names[self.value]


@functools.total_ordering
class AbsNote:
    @staticmethod
    def from_text(text: str):
        match = re.match('([A-G])(b+|#+)?(-?[0-9]+)?', text)
        assert match

        name_value = RelNote.values_by_name[match[1]]
        accidentals_value = get_accidentals_value(match[2])
        octave_value = (int(match[3]) + 1) * 12

        return AbsNote(octave_value + name_value + accidentals_value)

    def __init__(self, value: int):
        assert value >= 0
        self.value = value

    def next(self, note: RelNote):
        self_rel = self.rel_note()

        if self_rel.value < note.value:
            return AbsNote(self.value + (note.value - self_rel.value))
        else:
            return AbsNote(self.value + (note.value - self_rel.value + 12))

    def rel_note(self) -> RelNote:
        return RelNote(self.value % 12)

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other: AbsNote):
        return self.value == other.value

    def __lt__(self, other: AbsNote):
        return self.value < other.value

    def __repr__(self):
        return repr(self.rel_note()) + str(int(self.value / 12) - 1)


class RelNote:
    values_by_name = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    default_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    @staticmethod
    def from_text(text: str):
        match = re.match('([A-G])(b+|#+)?', text)
        assert match

        name_value = RelNote.values_by_name[match[1]]
        accidentals_value = get_accidentals_value(match[2])

        return RelNote(name_value + accidentals_value)

    def __init__(self, value: int):
        assert 0 <= value < 12
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other: RelNote):
        return self.value == other.value

    def __repr__(self):
        return RelNote.default_names[self.value]


def get_accidentals_value(accidentals: Optional[str]):
    if not accidentals:
        return 0

    if accidentals[0] == '#':
        assert accidentals == '#' * len(accidentals)
        return len(accidentals)

    if accidentals[0] == 'b':
        assert accidentals == 'b' * len(accidentals)
        return -len(accidentals)

    raise ValueError()


if __name__ == '__main__':
    main()
