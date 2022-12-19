from __future__ import annotations

from enum import Enum, auto
from typing import List, Optional, Union, NamedTuple

from music_theory import ScaleDegree, AbsNote, RelNote, Scale


def get_caged_shape(ctx: Context, caged_position: CagedPosition) -> List[Position]:
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
