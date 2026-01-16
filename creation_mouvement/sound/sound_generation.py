import numpy as np
import random as rd
from scipy.interpolate import make_interp_spline

SAMPLE_RATE = 44100
PITCH_RANGE = 1.0  # en octaves
MAX_END = 2
CONSONANT = np.array([1, 6/5, 5/4, 4/3, 3/2, 5/3, 2])
DISSONANT = np.array([1, 16/15, 9/8, 7/5, 10/7, 11/8, 13/9])


def note_curve(P, A, D, t, duration):
    # nombre de notes
    n = len(t)
    n_notes = int(2 + 10 * A * (1-D))
    
    # durées
    if D > 0.5:
        durations = np.ones(n_notes)
    else:
        durations = np.random.rand(n_notes)
    durations = durations / durations.sum() * duration

    # hauteurs
    ratios = CONSONANT if P > 0.5 else DISSONANT
    notes = []
    current = 0.0

    for _ in range(n_notes):
        r = rd.choice(ratios)
        jitter = rd.uniform(-0.03, 0.03) * (1 - D)
        current += np.log2(r) + jitter
        notes.append(current)

    curve = np.zeros(n)
    idx = 0

    # durée du glide (en samples)
    glide_time = (1 - D) * 0.05 + 0.002   # 2ms → 50ms
    glide_n = int(glide_time * SAMPLE_RATE)

    prev = notes[0]

    for dur, val in zip(durations, notes):
        seg_n = int(dur / duration * n)
        seg_n = max(seg_n, glide_n + 1)

        # partie stable
        curve[idx:idx+seg_n] = val

        # transition depuis la note précédente
        if idx > 0 and glide_n > 1:
            g = np.linspace(0, 1, glide_n)
            # interpolation non linéaire (plus nerveux)
            g = g**1.5
            curve[idx:idx+glide_n] = prev + g * (val - prev)

        prev = val
        idx += seg_n

    curve[idx:] = prev
    return curve



def pitch_curve(P, A, D, t, duration):
    start = 0.0
    
    # --- nombre de segments intermédiaires selon D ---
    n_mid = rd.randint(1, max(1, int(10 * A)))
    mid_points = [start]
    sign = 1  # la première pente va vers le haut
    for i in range(n_mid):
        # force de la pente dépend de A
        strength = A * rd.uniform(0.5, 1.0)
        # on flip le signe à chaque segment
        sign *= -1
        mid_val = mid_points[-1] + sign * strength
        mid_points.append(mid_val)
    
    # --- end point ---
    gravity = (1 - D) * (1 - P)
    end_sign = 1 if P > 0.5 else -1
    end = end_sign * gravity * MAX_END * (0.5 + rd.random())
    mid_points.append(end)
    
    # --- temps clé avec durées aléatoires ---
    durations = np.random.rand(len(mid_points)-1)  # génère des valeurs aléatoires pour chaque segment
    durations = durations / durations.sum() * duration  # normalise pour que la somme = duration totale
    key_times = np.cumsum([0] + list(durations))  # cumul pour avoir les temps de chaque point
    
    key_values = np.array(mid_points)
    
    # --- beta-spline ---
    spline = make_interp_spline(key_times, key_values, k=2)
    curve = spline(t)
    
    # --- vibrato ---
    vib_freq = 3 + (1-D) * 10
    vib_freq *= (0.7 + 0.6 * (1 - D))
    vib_amp = 0.15 * A * (1 - D)
    vibrato = vib_amp * np.sin(2 * np.pi * vib_freq * t)
    
    return curve + vibrato


def generate_sound(P, A, D, duration):
    sr = SAMPLE_RATE
    n = int(sr * duration)
    t = np.linspace(0, duration, n, endpoint=False)

    f0 = 220 + 440 * A * rd.uniform(0, A)  # base pitch

    C_cont = pitch_curve(P, A, D, t, duration)
    C_note = note_curve(P, A, D, t, duration)

    # dominance = morph
    C = (1 - D) * C_cont + D * C_note

    # fréquence instantanée
    f = f0 * (2 ** C)

    # intégration de phase
    phase = 2 * np.pi * np.cumsum(f) / sr

    # oscillateurs
    signal = np.sin(phase)
    num_harmonics = int(2 + 10 * A)

    for k in range(2, 2 + num_harmonics):
        amp = 1 / k
        # écart entre harmoniques pour un timbre plus naturel
        # P proche de 1 → ratios stables (plaisir)
        # P faible → ratios légèrement décalés (mineur / sombre)
        # base_ratio = k if P > 0.5 else k * rd.uniform(-0.3, 0.3)
        inharm = (1 - P) * rd.uniform(-0.15, 0.15)
        freq_ratio = k * (1 + inharm)

        
        # Arousal → ajouter un petit random pour rendre la voix moins robotique
        freq_ratio = freq_ratio + rd.uniform(-0.07, 0.07) * A

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
    sustain_level = 0.6 + 0.4 * D
    env *= sustain_level

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

