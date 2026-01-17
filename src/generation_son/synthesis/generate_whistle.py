import numpy as np
import soundfile as sf

SAMPLE_RATE = 44100

# ------------------------------------------------------------
# Chargement du sifflement de référence
# ------------------------------------------------------------
WHISTLE_SAMPLE, SR = sf.read("w1.wav")
if SR != SAMPLE_RATE:
    raise ValueError("Le sample doit être en 44.1 kHz")

WHISTLE_SAMPLE = WHISTLE_SAMPLE.astype(np.float32)

# normalisation de sécurité
WHISTLE_SAMPLE /= np.max(np.abs(WHISTLE_SAMPLE))


# ------------------------------------------------------------
# Estimation grossière de la fréquence dominante du sample
# ------------------------------------------------------------
def estimate_fundamental(wave):
    spectrum = np.abs(np.fft.rfft(wave))
    freqs = np.fft.rfftfreq(len(wave), 1 / SAMPLE_RATE)
    return freqs[np.argmax(spectrum)]


BASE_FREQ = estimate_fundamental(WHISTLE_SAMPLE)


# ------------------------------------------------------------
# Pitch shift par resampling (strident et naturel pour un sifflement)
# ------------------------------------------------------------
def pitch_shift_resample(wave, target_freq):
    ratio = target_freq / BASE_FREQ
    idx = np.arange(0, len(wave), ratio)
    idx = idx[idx < len(wave)].astype(int)
    return wave[idx]


# ------------------------------------------------------------
# Ajustement de durée
# ------------------------------------------------------------
def stretch_to_duration(wave, duration):
    target_len = int(SAMPLE_RATE * duration)
    return np.interp(
        np.linspace(0, len(wave), target_len),
        np.arange(len(wave)),
        wave
    )


# ------------------------------------------------------------
# Génération du sifflement final
# ------------------------------------------------------------
def generate_whistle_wave(freq, duration, intensity):
    """
    freq      : fréquence cible en Hz
    duration  : durée en secondes
    intensity : gain (0.0 – 1.0)
    """

    # 1. Pitch shift
    wave = pitch_shift_resample(WHISTLE_SAMPLE, freq)

    # 2. Ajustement de durée
    wave = stretch_to_duration(wave, duration)

    N = len(wave)
    t = np.arange(N) / SAMPLE_RATE

    # 3. Micro-instabilité de hauteur (stridence)
    fm_rate = 160
    fm_depth = 0.003
    fm = 1 + fm_depth * np.sin(2 * np.pi * fm_rate * t)
    wave *= fm

    # 4. Bruit d’air haute fréquence
    wave += 0.02 * np.random.randn(N)

    # 5. Saturation douce (essentielle)
    wave = np.tanh(3.0 * wave)

    # 6. Enveloppe réaliste
    attack = int(0.02 * SAMPLE_RATE)
    release = int(0.08 * SAMPLE_RATE)

    env = np.ones(N)
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] *= np.linspace(1, 0, release)

    wave *= env

    # 7. Intensité finale
    wave *= intensity

    return wave.astype(np.float32)
