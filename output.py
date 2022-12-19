from typing import List

import guitarpro

from exercises import RhythmType
from fretboard import Position

song = guitarpro.Song()


def add_exercise(positions: List[Position], rhythm: RhythmType):
    rhythm_settings = {
        RhythmType.STRAIGHT: (16, guitarpro.Duration(guitarpro.Duration.sixteenth)),
        RhythmType.TRIPLET: (12, guitarpro.Duration(guitarpro.Duration.eighth, False, guitarpro.Tuplet(3, 2))),
    }

    beats_per_measure, duration = rhythm_settings[rhythm]

    track = song.tracks[0]
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
        voice.beats.append(beat)

        note = guitarpro.Note(beat)
        note.value = position.fret
        note.string = position.string + 1
        beat.notes.append(note)


def write_file():
    guitarpro.write(song, 'exercise.gp5')
