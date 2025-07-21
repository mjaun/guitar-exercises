from __future__ import annotations

import functools
import re

from typing import Union, List, Optional

# text representations of commonly known scales
known_scale_types = {
    'minor pentatonic': '1-b3-4-5-b7',
    'major pentatonic': '1-2-3-5-6',

    'ionian': '1-2-3-4-5-6-7',
    'dorian': '1-2-b3-4-5-6-b7',
    'phrygian': '1-b2-b3-4-5-b6-b7',
    'lydian': '1-2-3-#4-5-6-7',
    'mixolydian': '1-2-3-4-5-6-b7',
    'aeolian': '1-2-b3-4-5-b6-b7',
    'locrian': '1-b2-b3-4-b5-b6-b7',
}


class Scale:
    """
    Represents a scale which is defined by a root note and a set of scale degrees.
    """

    @staticmethod
    def from_text(text: str):
        """
        Parses a scale from its text representation.

        Examples: A# Lydian, G Aeolian

        :param text: Text to parse.
        :return: The parsed scale.
        """

        parts = text.split()
        root_text = parts[0]
        scale_type_text = ' '.join(parts[1:])

        return Scale(RelNote.from_text(root_text), ScaleType.from_text(scale_type_text))

    def __init__(self, root: RelNote, scale_type: ScaleType):
        self.root = root
        self.degrees = scale_type.degrees

    def get_scale_degree(self, note: Union[AbsNote, RelNote]) -> ScaleDegree:
        """
        Gets the scale degree of a note.

        Example: B# in a scale with root note A is the b3.

        :param note: The note to get the scale degree for.
        :return: The parsed scale degree.
        """

        if isinstance(note, AbsNote):
            note = note.rel_note()

        if self.root.value < note.value:
            return ScaleDegree(note.value - self.root.value)
        else:
            return ScaleDegree(note.value - self.root.value + 12)

    def get_rel_note(self, scale_degree: ScaleDegree) -> RelNote:
        """
        Gets the note of a scale degree.

        Example: The b3 in a scale with root note A is B#.

        :param scale_degree: The scale degree to get the note for.
        :return: The parsed note.
        """

        return RelNote((self.root.value + scale_degree.value) % 12)


class ScaleType:
    """
    Represents a scale type which is defined by a set of scale degrees.
    """

    @staticmethod
    def from_text(text: str) -> ScaleType:
        """
        Parses a scale type from its text representation.

        Examples: Lydian, Aeolian, 1-2-b3-4-5-6-b7

        :param text: Text to parse.
        :return: The parsed scale type.
        """

        if text.lower() in known_scale_types:
            text = known_scale_types[text.lower()]

        return ScaleType([ScaleDegree.from_text(x) for x in text.split('-')])

    def __init__(self, degrees: List[ScaleDegree]):
        self.degrees = degrees


@functools.total_ordering
class ScaleDegree:
    """
    Represents a scale degree which is defined by its interval.
    """

    values_by_name = {'1': 0, '2': 2, '3': 4, '4': 5, '5': 7, '6': 9, '7': 11}
    default_names = ['1', 'b2', '2', 'b3', '3', '4', 'b5', '5', 'b6', '6', 'b7', '7']

    @staticmethod
    def from_text(text: str) -> ScaleDegree:
        """
        Parses a scale degree from its text representation.

        Examples: b3, #4, 5

        :param text: Text to parse.
        :return: The parsed scale degree.
        """

        match = re.match('(b+|#+)?([1-7])', text)
        assert match

        name_value = ScaleDegree.values_by_name[match[2]]
        accidentals_value = get_accidentals_value(match[1])

        return ScaleDegree(name_value + accidentals_value)

    def __init__(self, value: int):
        assert 0 <= value < 12
        self.value = value

    def add_half_steps(self, half_steps: int) -> ScaleDegree:
        """
        Adds a given amount of half steps to this scale degree (wraps around).

        Examples: b3 + 2 = 4, 5 + 1 = b6, 7 + 2 = b2

        :param half_steps: Number of half steps to add.
        :return: The resulting scale degree.
        """

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
    """
    Represents a musical note in a specific octave.
    """

    @staticmethod
    def from_text(text: str):
        """
        Parses an absolute note from its text representation.

        Examples: D#3, Ab3

        :param text: Text to parse.
        :return: The parsed absolute note.
        """

        match = re.match('([A-G])(b+|#+)?(-?[0-9]+)?', text)
        assert match

        name_value = RelNote.values_by_name[match[1]]
        accidentals_value = get_accidentals_value(match[2])
        octave_value = (int(match[3]) + 1) * 12

        return AbsNote(octave_value + name_value + accidentals_value)

    def __init__(self, value: int):
        assert value >= 0
        self.value = value

    def next_note(self, note: RelNote) -> AbsNote:
        """
        Returns the next absolute note corresponding to a given relative note.

        Example: The next C# from a B3 would be C#3.

        :param note: The given relative note.
        :return: The next absolute note.
        """

        self_rel = self.rel_note()

        if self_rel.value < note.value:
            return AbsNote(self.value + (note.value - self_rel.value))
        else:
            return AbsNote(self.value + (note.value - self_rel.value + 12))

    def rel_note(self) -> RelNote:
        """
        Returns the corresponding relative note.
        """

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
    """
    Represents a musical note without a specific octave.
    """

    values_by_name = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    default_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    @staticmethod
    def from_text(text: str) -> RelNote:
        """
        Parses a relative note from its text representation.

        Examples: D#, Ab

        :param text: Text to parse.
        :return: The parsed relative note.
        """

        match = re.match('([A-G])(b+|#+)?', text)
        assert match

        name_value = RelNote.values_by_name[match[1]]
        accidentals_value = get_accidentals_value(match[2])

        return RelNote(name_value + accidentals_value)

    def __init__(self, value: int):
        assert 0 <= value < 12
        self.value = value

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: RelNote) -> bool:
        return self.value == other.value

    def __repr__(self) -> str:
        return RelNote.default_names[self.value]


def get_accidentals_value(accidentals: Optional[str]) -> int:
    """
    Returns the accidentals value of a note.

    Examples: # -> 1, ## -> 2, b -> -1, bb -> -2

    :param accidentals: The accidentals string.
    :return: The relative value of the accidentals.
    """

    if not accidentals:
        return 0

    if accidentals[0] == '#':
        assert accidentals == '#' * len(accidentals)
        return len(accidentals)

    if accidentals[0] == 'b':
        assert accidentals == 'b' * len(accidentals)
        return -len(accidentals)

    raise ValueError()
