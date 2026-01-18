#------------- IMPORTS -------------#

import numpy as np
import soundfile as sf


#------- PATHS AND PARAMETERS -------#

SAMPLE_RATE = 44100

WHISTLE_SAMPLE, SR = sf.read("whistle_sample.wav")
WHISTLE_SAMPLE = WHISTLE_SAMPLE.astype(np.float32)
if SR != SAMPLE_RATE:
    raise ValueError("The sample must be at 44.1 kHz")
WHISTLE_SAMPLE /= np.max(np.abs(WHISTLE_SAMPLE))

#------------ ESTIMATION ------------#

def estimate_fundamental(wave):
    spectrum = np.abs(np.fft.rfft(wave))
    freqs = np.fft.rfftfreq(len(wave), 1 / SAMPLE_RATE)
    return freqs[np.argmax(spectrum)]

BASE_FREQ = estimate_fundamental(WHISTLE_SAMPLE)

def pitch_shift_resample(wave, target_freq):
    ratio = target_freq / BASE_FREQ
    idx = np.arange(0, len(wave), ratio)
    idx = idx[idx < len(wave)].astype(int)
    return wave[idx]

def stretch_to_duration(wave, duration):
    target_len = int(SAMPLE_RATE * duration)
    return np.interp(
        np.linspace(0, len(wave), target_len),
        np.arange(len(wave)),
        wave
    )

def generate_whistle_wave(freq, duration, intensity):
    """
    freq      : target frequency in Hz
    duration  : duration in seconds
    intensity : gain (0.0 – 1.0)
    """

    # 1. Pitch shift
    wave = pitch_shift_resample(WHISTLE_SAMPLE, freq)

    # 2. Duration adjustment
    wave = stretch_to_duration(wave, duration)

    N = len(wave)
    t = np.arange(N) / SAMPLE_RATE

    # 3. Micro pitch instability (shrillness)
    fm_rate = 160
    fm_depth = 0.003
    fm = 1 + fm_depth * np.sin(2 * np.pi * fm_rate * t)
    wave *= fm

    # 4. High-frequency air noise
    wave += 0.02 * np.random.randn(N)

    # 5. Soft saturation (essential)
    wave = np.tanh(3.0 * wave)

    # 6. Realistic envelope
    attack = int(0.02 * SAMPLE_RATE)
    release = int(0.08 * SAMPLE_RATE)

    env = np.ones(N)
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] *= np.linspace(1, 0, release)

    wave *= env

    # 7. Final intensity
    wave *= intensity

    return wave.astype(np.float32)


#------------ EXECUTION ------------#
