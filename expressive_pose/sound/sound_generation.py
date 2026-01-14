import numpy as np
import random as rd

SAMPLE_RATE = 44100
PITCH_RANGE = 1.0  # en octaves

def pitch_curve(P, A, D, t, duration):
    # glide principal (linéaire)
    direction = 2 * P - 1  # [-1, +1]
    glide = direction * (t / duration)

    # vibrato (Arousal)
    vib_freq = 2 + rd.uniform(-8*A, 8*A)
    vib_amp = 0.15 * A * (1 - D)
    vibrato = vib_amp * np.sin(2 * np.pi * vib_freq * t)

    return glide + vibrato


def generated_sound_from_pad(P, A, D, duration):
    sr = SAMPLE_RATE
    n = int(sr * duration)
    t = np.linspace(0, duration, n, endpoint=False)

    f0 = 220 + 500 * A * rd.uniform(0, A)  # base pitch

    C = pitch_curve(P, A, D, t, duration)

    # fréquence instantanée
    f = f0 * (2 ** C)

    # intégration de phase
    phase = 2 * np.pi * np.cumsum(f) / sr

    # oscillateurs
    signal = np.sin(phase)
    for k in range(2, 1 + int(1 + 4 * A)):
        signal += (0.3 / k) * np.sin(k * phase)

    # bruit
    noise = (0.08 + 0.1 * A * (1 - D)) * np.random.randn(n)

    # --- enveloppe dynamique ---
    env = np.ones(n)

    # fade-in + fade-out progressif selon durée
    fade_len = int(A * 0.2 * n)  # longueur mini du fade pour éviter coupures brutales
    # montée linéaire progressive sur toute la durée
    env *= np.linspace(0.2, 1.0, n)

    # fade-in rapide au début
    if fade_len > 0:
        env[:fade_len] = np.linspace(0, 1, fade_len)
    # fade-out rapide à la fin
    if fade_len > 0:
        env[-fade_len:] = np.linspace(1, 0, fade_len)

    # gain selon Dominance
    gain = 0.2 + 0.8 * D

    out = gain * env * (signal + noise)
    return out.astype(np.float32)

