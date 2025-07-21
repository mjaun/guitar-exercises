from __future__ import annotations

from enum import Enum, auto
from typing import List, Optional, Union, NamedTuple, Dict

from music_theory import ScaleDegree, AbsNote, RelNote, Scale

HIGHEST_FRET = 22


def get_all_caged_shapes(ctx: Context) -> Dict[CagedPosition, Shape]:
    """
    Returns all CAGED shapes for a given fretboard context.

    :param ctx: The fretboard context.
    :return: Dictionary of all CAGED shapes.
    """

    shapes = {}

    for caged_position in CagedPosition:
        shape = get_caged_shape(ctx, caged_position)
        shapes[caged_position] = shape

        if shape_octave_up := move_shape_octave_up(shape):
            shapes[caged_position] = shape_octave_up

    return shapes


def get_caged_shape(ctx: Context, caged_position: CagedPosition) -> Shape:
    """
    Returns a CAGED shape for a given fretboard context.

    :param ctx: The fretboard context.
    :param caged_position: CAGED position to get the shape for.
    :return: The requested CAGED shape.
    """

    string_count = ctx.tuning.string_count()

    # step one: figure out which scale degrees are on which string
    # we use a fixed definition of which scale degree range may occur on which string per CAGED position
    # note that this definition only makes sense for standard tuning
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
                abs_note = last_abs_note.next_note(rel_note)
                fret = ctx.tuning.get_fret(string, abs_note)

            positions.append(Position(string, fret))
            last_abs_note = abs_note

    # step three: move an octave up if necessary
    if any(position.fret < 0 for position in positions):
        positions = [Position(position.string, position.fret + 12) for position in positions]

    return positions


def move_shape_octave_up(shape: Shape) -> Optional[Shape]:
    """
    Moves a given shape up one octave.

    :param shape: The shape to move up.
    :return: The resulting shape or None if we would run out of frets.
    """

    if any(position.fret + 12 > HIGHEST_FRET for position in shape):
        return None

    return [Position(position.string, position.fret + 12) for position in shape]


class CagedPosition(Enum):
    C = auto()
    A = auto()
    G = auto()
    E = auto()
    D = auto()


class Context:
    """
    Represents a fretboard context which is defined by a tuning and a scale.
    """

    def __init__(self, tuning: Tuning, scale: Scale):
        self.tuning = tuning
        self.scale = scale


class Tuning:
    """
    Represents a tuning defined by an absolute note per string.
    """

    @staticmethod
    def from_text(text: str):
        """
        Parses a tuning from its text representation.

        Example: E2-A2-D3-G3-B3-E4

        :param text: Text to parse.
        :return: The parsed tuning.
        """

        return Tuning([AbsNote.from_text(x) for x in reversed(text.split('-'))])

    def __init__(self, strings: List[AbsNote]):
        self.strings = strings

    def string_count(self) -> int:
        """
        Returns the number of strings in the tuning.
        """

        return len(self.strings)

    def get_note(self, position: Position) -> AbsNote:
        """
        Returns the absolute note of a given position.

        :param position: The position to get the note for.
        :return: The absolute note of the given position.
        """

        return AbsNote(self.strings[position.string].value + position.fret)

    def get_fret(self, string: int, note: Union[RelNote, AbsNote]) -> int:
        """
        Returns the fret of a given note on a given string.

        The returned value is theoretical and can be negative or too high.

        :param string: The string index.
        :param note: Note to get the fret for.
        :return: The fret index.
        """

        open_note = self.strings[string]

        if isinstance(note, AbsNote):
            return note.value - open_note.value

        if isinstance(note, RelNote):
            if open_note.rel_note() == note:
                return 0
            else:
                return open_note.next_note(note).value - open_note.value

        raise NotImplementedError()


class Position(NamedTuple):
    """
    Represents a position on the guitar fretboard defined by a string index and a fret index.

    String index 0 is the highest string.
    Fret index 0 is the open string.
    """

    string: int
    fret: int


Shape = List[Position]
