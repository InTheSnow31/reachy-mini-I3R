import numpy as np
import soundfile as sf
import math
from Note import Note

SAMPLE_RATE = 44100
A4_PITCH = 49
A4_FREQ = 440.0
DEFAULT_BPM = 400

def generate_piano_like_wave(freq, duration, intensity):
    t = np.arange(int(SAMPLE_RATE * duration)) / SAMPLE_RATE

    # Harmoniques typiques
    harmonics = [
        (1.0, 1.0),
        (2.0, 0.5),
        (3.0, 0.3),
        (4.0, 0.15),
        (5.0, 0.08),
    ]

    wave = np.zeros_like(t)

    for multiplier, amplitude in harmonics:
        wave += amplitude * np.sin(2 * math.pi * freq * multiplier * t)

    # Enveloppe simple (attaque rapide, decay lent)
    attack = int(0.02 * SAMPLE_RATE)
    decay = len(t) - attack

    envelope = np.concatenate([
        np.linspace(0, 1, attack),
        np.linspace(1, 0.4, decay)
    ])

    wave *= envelope
    wave *= intensity

    return wave

def pitch_to_frequency(pitch):
    if not 0 <= pitch <= 87:
        raise ValueError("Pitch doit être entre 0 et 87, ici :", pitch)
    return A4_FREQ * (2 ** (((pitch+1) - A4_PITCH) / 12))

def duration_to_seconds(duration, bpm=DEFAULT_BPM):
    if not 1 <= duration <= 4:
        raise ValueError("Duration doit être entre 1 et 4")

    quarter_note = 60.0 / bpm
    return duration * quarter_note


def generate_note_wave(note: Note, bpm=DEFAULT_BPM):
    freq = pitch_to_frequency(note.pitch)
    duration_sec = duration_to_seconds(note.duration, bpm)

    return generate_piano_like_wave(freq, duration_sec, note.intensity)


def notes_to_wav(notes, output_path, bpm=DEFAULT_BPM):
    audio = np.array([], dtype=np.float32)

    for note in notes:
        audio = np.concatenate((audio, generate_note_wave(note, bpm)))

    # Anti-clipping
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio /= peak

    sf.write(output_path, audio, SAMPLE_RATE)
    print(f"WAV généré : {output_path}")

notes = [
    Note(87, 0.7, 1),  # noire
    Note(44, 0.7, 2),  # noire
    Note(47, 0.7, 1),  # noire
    Note(52, 1.0, 4),  # ronde
]

notes_to_wav(notes, "melodie.wav")