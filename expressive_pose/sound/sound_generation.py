import numpy as np
import random as rd
from scipy.interpolate import make_interp_spline

SAMPLE_RATE = 44100
PITCH_RANGE = 1.0  # en octaves


def pitch_curve(P, A, D, t, duration):
    """
    Courbe de pitch modulée par PAD avec beta-spline et probabilité selon Pleasure.
    P : Pleasure ∈ [0,1]
    A : Arousal ∈ [0,1]
    D : Dominance ∈ [0,1]
    t : temps
    duration : durée totale
    """
    n = len(t)
    
    # --- Points clés ---
    start = 0.0
    
    # --- Middle : arousal + un peu de hasard
    # Plus A élevé → le milieu s'écarte du start
    middle_shift = A * rd.uniform(0.2, 1.0) if rd.random() < P else A * rd.uniform(-0.8, 0.2)
    middle = start + middle_shift

    # --- End : se rapproche de start selon dominance et pleasure
    # Plus D élevé → fin proche du début
    # Plus P élevé → fin plus aigu, sinon plus grave
    gravity_factor = 10 * (1 - D) * (1 - P)  # 0 = fin proche start, 1 = fin très éloignée
    end_shift = gravity_factor * rd.uniform(-0.5, 0.5)
    end = start + end_shift
    
    # --- Position relative dans le temps ---
    key_times = np.array([0.0, 0.5, 1.0]) * duration
    key_values = np.array([start, middle, end])
    
    # --- Beta-spline pour interpolation lisse ---
    spline = make_interp_spline(key_times, key_values, k=2)
    curve = spline(t)
    
    # --- Vibrato ---
    vib_freq = 2 + rd.uniform(-8*A, 8*A)
    vib_amp = 0.15 * A * (1 - D)
    vibrato = vib_amp * np.sin(2 * np.pi * vib_freq * t)
    
    return curve + vibrato




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
    num_harmonics = int(1 + 10 * A)

    for k in range(2, 2 + num_harmonics):
        amp = 1 / k
        # écart entre harmoniques pour un timbre plus naturel
        # P proche de 1 → ratios stables (plaisir)
        # P faible → ratios légèrement décalés (mineur / sombre)
        base_ratio = k if P > 0.5 else k * rd.uniform(-0.5, 0.8)
        
        # Arousal → ajouter un petit random pour rendre la voix moins robotique
        freq_ratio = base_ratio + rd.uniform(-0.07, 0.07) * A

        signal += amp * np.sin(k * freq_ratio * phase)

    # bruit
    noise = (0.08 + 0.1 * A * (1 - D)) * np.random.randn(n)

    # gain selon Dominance
    gain = 0.2 + 0.8 * D

    # --- enveloppe ---
    env = np.ones(n)

    # attaque dépendante de l'arousal
    attack_time = 0.2 + (1 - A + 0.01) * 0.5
    attack_n = int(sr * attack_time)
    attack_n = min(attack_n, n // 2)

    env[:attack_n] = np.linspace(0, 1, attack_n)

    # Sustain
    env[attack_n:] = 1.0

    # montée progressive sur toute la durée
    env *= np.linspace(0.2, 1.0, n)

    # release doux
    release_ratio = 0.3 + 0.4 * (1 - A)
    release_n = int(release_ratio * n)
    release_n = min(release_n, n - attack_n)

    env[-release_n:] *= np.linspace(1, 0, release_n)

    r = np.linspace(0, 1, release_n)
    env[-release_n:] *= np.exp(-4.5 * r)

    out = gain * env * (signal + noise)
    
    return out.astype(np.float32)

