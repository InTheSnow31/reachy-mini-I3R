import random as rd
from typing import Final

import numpy as np
from scipy.interpolate import make_interp_spline


# =========================
# Global constants
# =========================

SAMPLE_RATE: Final[int] = 44_100
PITCH_RANGE: Final[float] = 1.0  # Pitch range in octaves
MAX_END: Final[float] = 2.0

# Frequency ratios for consonant and dissonant intervals
CONSONANT: Final[np.ndarray] = np.array([1, 6 / 5, 5 / 4, 4 / 3, 3 / 2, 5 / 3, 2])
DISSONANT: Final[np.ndarray] = np.array([1, 16 / 15, 9 / 8, 7 / 5, 10 / 7, 11 / 8, 13 / 9])


def note_curve(
    P: float,
    A: float,
    D: float,
    t: np.ndarray,
    duration: float,
) -> np.ndarray:
    """
    Generate a discrete, note-based pitch curve with smooth glides between notes.
    """
    # Total number of samples
    n: int = len(t)

    # Number of notes depends on arousal and dominance
    n_notes: int = int(2 + 10 * A * (1 - D))

    # Note durations
    if D > 0.5:
        durations = np.ones(n_notes)
    else:
        durations = np.random.rand(n_notes)

    # Normalize durations to match total duration
    durations = durations / durations.sum() * duration

    # Choose harmonic or dissonant ratios based on pleasure
    ratios = CONSONANT if P > 0.5 else DISSONANT
    notes: list[float] = []
    current: float = 0.0

    # Generate successive pitch values
    for _ in range(n_notes):
        ratio = rd.choice(ratios)
        jitter = rd.uniform(-0.03, 0.03) * (1 - D)
        current += np.log2(ratio) + jitter
        notes.append(current)

    curve = np.zeros(n)
    idx: int = 0

    # Glide duration in samples (2 ms to 50 ms)
    glide_time: float = (1 - D) * 0.05 + 0.002
    glide_n: int = int(glide_time * SAMPLE_RATE)

    prev: float = notes[0]

    for dur, val in zip(durations, notes):
        # Number of samples for this note segment
        seg_n = int(dur / duration * n)
        seg_n = max(seg_n, glide_n + 1)

        # Stable pitch region
        curve[idx:idx + seg_n] = val

        # Glide from previous note
        if idx > 0 and glide_n > 1:
            end = min(idx + glide_n, n)
            actual_n = end - idx

            if actual_n > 1:
                g = np.linspace(0.0, 1.0, actual_n)
                g = g**1.5
                curve[idx:end] = prev + g * (val - prev)

        prev = val
        idx += seg_n

    # Fill remaining samples with last pitch value
    curve[idx:] = prev
    return curve


def pitch_curve(
    P: float,
    A: float,
    D: float,
    t: np.ndarray,
    duration: float,
) -> np.ndarray:
    """
    Generate a continuous pitch contour using spline interpolation and vibrato.
    """
    start: float = 0.0

    # Number of intermediate segments depends on arousal
    n_mid: int = rd.randint(1, max(1, int(10 * A)))
    mid_points: list[float] = [start]

    sign: int = 1  # Initial slope direction
    for _ in range(n_mid):
        # Segment strength scales with arousal
        strength = A * rd.uniform(0.5, 1.0)
        sign *= -1
        mid_val = mid_points[-1] + sign * strength
        mid_points.append(mid_val)

    # End point influenced by pleasure and dominance
    gravity = (1 - D) * (1 - P)
    end_sign = 1 if P > 0.5 else -1
    end = end_sign * gravity * MAX_END * (0.5 + rd.random())
    mid_points.append(end)

    # Randomized segment durations
    durations = np.random.rand(len(mid_points) - 1)
    durations = durations / durations.sum() * duration
    key_times = np.cumsum([0.0] + list(durations))

    key_values = np.array(mid_points)

    # Quadratic spline interpolation
    spline = make_interp_spline(key_times, key_values, k=2)
    curve = spline(t)

    # Vibrato component
    vib_freq = 3 + (1 - D) * 10
    vib_freq *= 0.7 + 0.6 * (1 - D)
    vib_amp = 0.15 * A * (1 - D)

    vibrato = vib_amp * np.sin(2 * np.pi * vib_freq * t)

    return curve + vibrato


def generate_sound(
    P: float,
    A: float,
    D: float,
    duration: float,
) -> np.ndarray:
    """
    Generate a synthetic audio signal driven by pleasure, arousal, and dominance.
    """
    sr: int = SAMPLE_RATE
    n: int = int(sr * duration)
    t = np.linspace(0.0, duration, n, endpoint=False)

    # Base fundamental frequency
    f0: float = 220 + 440 * A * rd.uniform(0.0, A)

    # Pitch curves
    C_cont = pitch_curve(P, A, D, t, duration)
    C_note = note_curve(P, A, D, t, duration)

    # Dominance controls morphing between pitch behaviors
    key_offset = rd.uniform(-0.5, 0.5) * (1 - D)
    C = C_cont # + C_note + key_offset # Can be used, but still sounds weird

    # Instantaneous frequency
    f = f0 * (2.0**C)

    # Phase integration
    phase = 2 * np.pi * np.cumsum(f) / sr

    # Harmonic oscillator bank
    signal = np.sin(phase)
    num_harmonics: int = int(2 + 10 * A)

    for k in range(2, 2 + num_harmonics):
        amp = 1.0 / k

        # Inharmonicity increases for low pleasure values
        inharm = (1 - P) * rd.uniform(-0.15, 0.15)
        freq_ratio = k * (1 + inharm)

        # Arousal adds slight randomness to reduce robotic tone
        freq_ratio += rd.uniform(-0.07, 0.07) * A

        signal += amp * np.sin(k * freq_ratio * phase)

    # Noise component
    noise = (0.08 + 0.1 * A * (1 - D)) * np.random.randn(n)

    # Global gain controlled by dominance
    gain: float = 0.2 + 0.8 * D

    # Amplitude envelope
    env = np.ones(n)

    # Attack phase depends on arousal
    attack_time = 0.2 + (1 - A + 0.01) * 0.5
    attack_n = min(int(sr * attack_time), n // 2)
    env[:attack_n] = np.linspace(0.0, 1.0, attack_n)

    # Sustain level depends on dominance
    sustain_level = 0.6 + 0.4 * D
    env[attack_n:] = sustain_level

    # Global rise over the full duration
    env *= np.linspace(0.2, 1.0, n)

    # Release phase
    release_ratio = 0.3 + 0.4 * (1 - A)
    release_n = min(int(release_ratio * n), n - attack_n)

    env[-release_n:] *= np.linspace(1.0, 0.0, release_n)
    r = np.linspace(0.0, 1.0, release_n)
    env[-release_n:] *= np.exp(-4.5 * r)

    out = gain * env * (signal + noise)
    return out.astype(np.float32)
