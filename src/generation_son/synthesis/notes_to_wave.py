import numpy as np
import soundfile as sf
import math
from Note import Note

SAMPLE_RATE = 44100
A4_PITCH = 49
A4_FREQ = 440.0
DEFAULT_BPM = 400

# Harmoniques typiques
harmonics_crisp = [
        (1.0, 1.0),
        (2.0, 0.5),
        (3.0, 0.3),
        (4.0, 0.15),
        (5.0, 0.08),
    ]

harmonics_soft = [
    (1, 1.00),    # DO#7 fondamentale
    (2, 0.08),
    (3, 0.04),
    (4, 0.05),
    (5, 0.02),
    (6, 0.04),
    (7, 0.02),
    (8, 0.02),
    (9, 0.02),
    (10, 0.02),
    (12, 0.04),
    (16, 0.003),
    ]

harmonics = harmonics_soft

def generate_piano_like_wave(freq, duration, intensity):
    t = np.arange(int(SAMPLE_RATE * duration)) / SAMPLE_RATE

    wave = np.zeros_like(t)

    for multiplier, amplitude in harmonics:
        wave += amplitude * np.sin(2 * math.pi * freq * multiplier * t)

    # enveloppe piano-like
    N = len(t)

    attack = int(0.01 * SAMPLE_RATE)
    decay = int(0.35 * SAMPLE_RATE)  # plus long

    attack = min(attack, N)
    decay = min(decay, N - attack)

    envelope = np.zeros(N)
    envelope[:attack] = np.linspace(0, 1, attack)
    envelope[attack:attack+decay] = np.linspace(1, 0, decay)

    wave *= envelope
    wave *= intensity


    return wave

def generate_whistle_wave(freq, duration, intensity):
    N = int(SAMPLE_RATE * duration)
    t = np.arange(N) / SAMPLE_RATE

    # FM rapide
    fm_rate = 180
    fm_depth = 0.03
    fm = fm_depth * np.sin(2 * np.pi * fm_rate * t)
    freq_t = freq * (1 + fm)

    phase = np.cumsum(2 * np.pi * freq_t / SAMPLE_RATE)

    # partiels agressifs
    partials = [
        (1.00, 1.00),
        (2.01, 0.05),
        (6.87, 0.015),
    ]

    wave = np.zeros(N)
    for mult, amp in partials:
        wave += amp * np.sin(mult * phase)

    # bruit HF
    wave += 0.02 * np.random.randn(N)

    # saturation douce
    wave = np.tanh(2.5 * wave)

    # enveloppe simple
    attack = int(0.01 * SAMPLE_RATE)
    release = int(0.05 * SAMPLE_RATE)
    env = np.ones(N)
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] *= np.linspace(1, 0, release)

    return wave * env * intensity


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

    total_duration = duration_to_seconds(note.duration, bpm)

    sound_duration = min(0.2, total_duration)  # note courte
    sound = generate_whistle_wave(freq, sound_duration, note.intensity)

    silence_duration = total_duration - sound_duration
    silence = np.zeros(int(SAMPLE_RATE * silence_duration))

    return np.concatenate([sound, silence])

def generate_slide_wave(pitch_start, pitch_end, duration, intensity):
    N = int(SAMPLE_RATE * duration)

    # interpolation linéaire en pitch
    pitch_t = np.linspace(pitch_start, pitch_end, N)
    freq_t = A4_FREQ * (2 ** (((pitch_t + 1) - A4_PITCH) / 12))

    # intégration de phase
    phase = np.cumsum(2 * np.pi * freq_t / SAMPLE_RATE)

    wave = np.zeros(N)

    for mult, amp in harmonics:
        wave += amp * np.sin(mult * phase)

    # enveloppe simple
    attack = int(0.02 * SAMPLE_RATE)
    envelope = np.ones(N)
    envelope[:attack] = np.linspace(0, 1, attack)
    envelope *= intensity

    return wave * envelope


def notes_to_wav(notes, output_path, bpm=DEFAULT_BPM):
    audio = np.array([], dtype=np.float32)

    for i,note in enumerate(notes):
        if (i > 0):
            prev_note = notes[i-1]
            if note.slide:
                slide_wave = generate_slide_wave(prev_note.pitch, note.pitch, duration_to_seconds(note.duration, bpm), note.intensity)
                audio = np.concatenate((audio, slide_wave))
        audio = np.concatenate((audio, generate_note_wave(note, bpm)))

    # Anti-clipping
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio /= peak

    sf.write(output_path, audio, SAMPLE_RATE)
    print(f"WAV généré : {output_path}")

notes = [
    Note(55, 0.7, 1,False),  # noire
    Note(44, 0.7, 2, True),  # noire
    Note(47, 0.7, 1,True),  # noire
    Note(52, 1.0, 4, False),  # ronde
]

notes_to_wav(notes, "melodie2.wav")