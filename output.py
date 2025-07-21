from typing import List

import guitarpro

from exercises import Feel
from fretboard import Position, Context


class GuitarProFile:
    def __init__(self, title: str, subtitle: str):
        self.song = guitarpro.Song()
        self.song.title = title
        self.song.subtitle = subtitle
        self.song.tempo = 100

    def add_exercise(self, name: str, positions: List[Position], rhythm: Feel):
        rhythm_settings = {
            Feel.STRAIGHT: (16, guitarpro.Duration(guitarpro.Duration.sixteenth)),
            Feel.TRIPLET: (12, guitarpro.Duration(guitarpro.Duration.eighth, False, guitarpro.Tuplet(3, 2))),
        }

        beats_per_measure, duration = rhythm_settings[rhythm]

        track = self.song.tracks[0]
        measure = track.measures[0]
        voice = measure.voices[0]

        if not voice.isEmpty:
            measure = guitarpro.Measure(track, measure.header)
            track.measures.append(measure)
            voice = measure.voices[0]

        for i, position in enumerate(positions):
            if i > 0 and i % beats_per_measure == 0:
                measure = guitarpro.Measure(track, measure.header)
                track.measures.append(measure)
                voice = measure.voices[0]

            beat = guitarpro.Beat(voice)
            beat.duration = duration

            if i == 0:
                beat.text = name

            voice.beats.append(beat)

            note = guitarpro.Note(beat)
            note.value = position.fret
            note.string = position.string + 1
            beat.notes.append(note)

    def write(self, path: str):
        guitarpro.write(self.song, path)


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
